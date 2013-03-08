/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include "pythonhelpers.h"


using namespace PythonHelpers;

extern "C" {

// Type structure for WeakMethod instances
typedef struct {
    PyObject_HEAD
    PyObject* weakreflist;  // weakrefs to this object
    PyObject* func;         // method.im_func
    PyObject* selfref;      // weakref.ref(method.im_self)
    PyObject* cls;          // method.im_class
} WeakMethod;


// A dict where a key is weakref.ref(method.im_self) and the value is a
// list of WeakMethod instances for that object. This is initialized in
// the module init function. This is not declared as a PyObjectPtr since
// a destructor being run on dlclose() has the potential to call the
// tp_dealloc slot after interpreter shut down.
static PyObject* weak_methods;


// A preallocated string object to lookup the `_remove` staticmethod.
static PyObject* remove_str;


static PyObject*
WeakMethod_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyDictPtr kwargsptr( kwargs, true );
    if( ( kwargsptr ) && ( kwargsptr.size() > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "WeakMethod() takes no keyword arguments (";
        ostr << kwargsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyTuplePtr argsptr( args, true );
    if( argsptr.size() != 1 )
    {
        std::ostringstream ostr;
        ostr << "WeakMethod() takes 1 argument (";
        ostr << argsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyMethodPtr method( argsptr.get_item( 0 ) );
    if( !PyMethod_Check( method.get() ) )
        return py_expected_type_fail( method.get(), "MethodType" );

    PyObjectPtr self( method.get_self() );
    PyObjectPtr cls( method.get_class() );
    PyObjectPtr func( method.get_function() );
    if( !self )
        return py_type_fail( "Expected a bound method. Got unbound method instead." );

    /* The logic to setup the weakref is as follows:

    The keys of the weak_methods dict should be weakrefs for a given
    object and have a callback that will pop the item from the dict
    when the underlying object is destroyed. When using weakrefs as
    keys in a dictionary, two weakrefs will hash to the same value
    and compare equally if their underlying object is the same. This
    is true even if the two weakrefs have different callbacks. When
    creating weakrefs without callbacks, Python will only create a
    single instance for a given object, and return that same weakref
    instance for multiple calls. i.e:

        >>> f = Foo()
        >>> r = weakref.ref(f)
        >>> r is weakref.ref(f)
        True

    However, Python will create a new weakref instance for each
    weakref with a callback, even if the callback is the same:

        >>> def bar(): pass
        >>> f = Foo()
        >>> r = weakref.ref(f, bar)
        >>> r is weakref.ref(f, bar)
        False

    A `WeakMethod` instance does not rely on a callback. Therefore, a
    good amount of space can be saved if all `WeakMethod` instances for
    a given object share the same no-callback weakref for that object,
    and the only weakref with callback kept around is the one used as
    the key in the dict.

    The logic below first creates a no-callback weakref, which is always
    necessary and will only be created by Python once and then reused.
    That weakref is used to lookup the item in the dict. If that lookup
    succeeds, the weakref with callback already exists and no more work
    is required. Otherwise, the weakref with callback is created and
    used as the key in the dict.

    */

    PyWeakrefPtr selfref( PyWeakref_NewRef( self.get(), 0 ) );
    if( !selfref )
        return 0;

    PyDictPtr wmethods_ptr( weak_methods, true );
    PyListPtr items( wmethods_ptr.get_item( selfref ) );
    if( !items )
    {
        items = PyList_New( 0 );
        if( !items )
            return 0;
        PyObjectPtr wm_type( reinterpret_cast<PyObject*>( type ), true );
        PyObjectPtr _remove_str( remove_str, true );
        PyObjectPtr _remove( wm_type.get_attr( _remove_str ) );
        if( !_remove )
            return 0;
        PyWeakrefPtr selfrefcb( PyWeakref_NewRef( self.get(), _remove.get() ) );
        if( !selfrefcb )
            return 0;
        if( !wmethods_ptr.set_item( selfrefcb, items ) )
            return 0;
    }

    WeakMethod* pywm = 0;
    Py_ssize_t size = items.size();
    for( Py_ssize_t idx = 0; idx < size; idx++ )
    {
        PyObjectPtr wmptr( items.get_item( idx ) );
        pywm = reinterpret_cast<WeakMethod*>( wmptr.get() );
        if( ( func.get() == pywm->func ) && ( cls.get() == pywm->cls ) )
            return wmptr.release();
    }

    PyObjectPtr wm( PyType_GenericNew( type, args, kwargs ) );
    if( !wm )
        return 0;

    pywm = reinterpret_cast<WeakMethod*>( wm.get() );
    pywm->func = func.release();
    pywm->selfref = selfref.release();
    pywm->cls = cls.release();

    if( !items.append( wm ) )
        return 0;

    return wm.release();
}


static void
WeakMethod_clear( WeakMethod* self )
{
    Py_CLEAR( self->func );
    Py_CLEAR( self->selfref );
    Py_CLEAR( self->cls );
}


static int
WeakMethod_traverse( WeakMethod* self, visitproc visit, void* arg )
{
    Py_VISIT( self->func );
    Py_VISIT( self->selfref );
    Py_VISIT( self->cls );
    return 0;
}


static void
WeakMethod_dealloc( WeakMethod* self )
{
    PyObject_GC_UnTrack( self );
    if( self->weakreflist )
        PyObject_ClearWeakRefs( reinterpret_cast<PyObject*>( self ) );
    WeakMethod_clear( self );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
WeakMethod_call( WeakMethod* self, PyObject* args, PyObject* kwargs )
{
    PyWeakrefPtr selfref( self->selfref, true );
    PyObjectPtr mself( selfref.get_object() );
    if( mself.is_None() )
        Py_RETURN_NONE;
    PyMethodPtr method( PyMethod_New( self->func, mself.get(), self->cls ) );
    if( !method )
        return 0;
    PyTuplePtr argsptr( args, true );
    PyDictPtr kwargsptr( kwargs, true );
    return method( argsptr, kwargsptr ).release();
}


// A staticmethod fired by the object underlyling a weakref used as the
// key in the weak_methods dict when it is garbage collected. This will
// remove the entry from the dict and allows the WeakMethod instances
// to be garbage collected.
static PyObject*
WeakMethod__remove( PyObject* ignored, PyObject* wr_item )
{
    PyDictPtr wmethods_ptr( weak_methods, true );
    PyObjectPtr wrptr( wr_item, true );
    if( !wmethods_ptr.del_item( wrptr ) )
        return 0;
    Py_RETURN_NONE;
}


static PyMethodDef
WeakMethod_methods[] = {
    { "_remove", ( PyCFunction )WeakMethod__remove, METH_O | METH_STATIC,
      "Release internal strong references to WeakMethod instances" },
    { 0 } // sentinel
};


PyDoc_STRVAR(WeakMethod__doc__,
"WeakMethod(method)\n\n"
"An object which weakly binds a method with a lifetime bound\n"
"to the lifetime of the underlying object.\n\n"
"Instances of WeakMethod are also weakref-able with a lifetime which\n"
"is also bound to lifetime of the method owner.\n\n"
"If multiple WeakMethods are requested for the same equivalent method\n"
"object, the same WeakMethod will be returned. This behavior is the\n"
"same as the standard weakref semantics.\n\n"
"Parameters\n"
"----------\n"
"method : A bound method object\n"
"    The bound method which should be wrapped weakly.\n\n");


PyTypeObject WeakMethod_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "weakmethod.WeakMethod",                /* tp_name */
    sizeof( WeakMethod ),                   /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)WeakMethod_dealloc,         /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)WeakMethod_call,           /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC, /* tp_flags */
    WeakMethod__doc__,                      /* Documentation string */
    (traverseproc)WeakMethod_traverse,      /* tp_traverse */
    (inquiry)WeakMethod_clear,              /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    offsetof( WeakMethod, weakreflist ),    /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)WeakMethod_methods, /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)WeakMethod_new,                /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
weakmethod_methods[] = {
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initweakmethod( void )
{
    PyObject* mod = Py_InitModule( "weakmethod", weakmethod_methods );
    if( !mod )
        return;

    weak_methods = PyDict_New();
    if( !weak_methods )
        return;

    remove_str = PyString_FromString( "_remove" );
    if( !remove_str )
        return;

    if( PyType_Ready( &WeakMethod_Type ) )
        return;

    PyObjectPtr wm_type( reinterpret_cast<PyObject*>( &WeakMethod_Type ), true );
    PyModule_AddObject( mod, "WeakMethod", wm_type.release() );
}

} // extern "C"

