/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include <cppy/cppy.h>


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
    cppy::ptr kwargsptr( cppy::incref( kwargs ) );
    if( ( kwargsptr ) && ( PyDict_Size( kwargsptr.get() ) > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "WeakMethod() takes no keyword arguments (";
        ostr << PyDict_Size( kwargsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr argsptr( cppy::incref( args ) );
    if( PyTuple_Size( argsptr.get() ) != 1 )
    {
        std::ostringstream ostr;
        ostr << "WeakMethod() takes 1 argument (";
        ostr << PyTuple_Size( argsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr method( argsptr.getitem( 0 ) );
    if( !PyMethod_Check( method.get() ) )
        return cppy::type_error( method.get(), "MethodType" );

    cppy::ptr self( cppy::incref( PyMethod_GET_SELF( method.get() ) ) );
    cppy::ptr cls( pyobject_cast( Py_TYPE(self.get() ) ) );
    cppy::ptr func( cppy::incref( PyMethod_GET_FUNCTION( method.get() ) ) );
    if( !self )
        return cppy::type_error( "Expected a bound method. Got unbound method instead." );

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

    cppy::ptr selfref( PyWeakref_NewRef( self.get(), 0 ) );
    if( !selfref )
        return 0;

    cppy::ptr wmethods_ptr( cppy::ptr( weak_methods ) );
    cppy::ptr items( wmethods_ptr.getitem( selfref ) );
    if( !items )
    {
        items = PyList_New( 0 );
        if( !items )
            return 0;
        cppy::ptr wm_type( cppy::incref( pyobject_cast( type ) ) );
        cppy::ptr _remove_str( cppy::incref( remove_str ) );
        cppy::ptr _remove( wm_type.getattr( _remove_str ) );
        if( !_remove )
            return 0;
        cppy::ptr selfrefcb( PyWeakref_NewRef( self.get(), _remove.get() ) );
        if( !selfrefcb )
            return 0;
        if( !wmethods_ptr.setitem( selfrefcb, items ) )
            return 0;
    }

    WeakMethod* pywm = 0;
    Py_ssize_t size = items.size();
    for( Py_ssize_t idx = 0; idx < size; idx++ )
    {
        cppy::ptr wmptr( items.getitem( idx ) );
        pywm = reinterpret_cast<WeakMethod*>( wmptr.get() );
        if( ( func.get() == pywm->func ) && ( cls.get() == pywm->cls ) )
            return wmptr.release();
    }

    cppy::ptr wm( PyType_GenericNew( type, args, kwargs ) );
    if( !wm )
        return 0;

    pywm = reinterpret_cast<WeakMethod*>( wm.get() );
    pywm->func = func.release();
    pywm->selfref = selfref.release();
    pywm->cls = cls.release();

    if( !PyList_Append( items.get(), wm.get() ) )
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
        PyObject_ClearWeakRefs( pyobject_cast( self ) );
    WeakMethod_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


static PyObject*
WeakMethod_call( WeakMethod* self, PyObject* args, PyObject* kwargs )
{
    cppy::ptr selfref( cppy::incref( self->selfref ) );
    cppy::ptr mself( cppy::incref( PyWeakref_GET_OBJECT( selfref.get() ) ) );
    if( mself.is_none() )
        Py_RETURN_NONE;
    cppy::ptr method( PyMethod_New( self->func, mself.get() ) );
    if( !method )
        return 0;
    cppy::ptr argsptr( cppy::incref( args ) );
    cppy::ptr kwargsptr( cppy::incref( kwargs ) );
    return method.call( argsptr, kwargsptr ).release();
}


// A staticmethod fired by the object underlyling a weakref used as the
// key in the weak_methods dict when it is garbage collected. This will
// remove the entry from the dict and allows the WeakMethod instances
// to be garbage collected.
static PyObject*
WeakMethod__remove( PyObject* ignored, PyObject* wr_item )
{
    cppy::ptr wmethods_ptr( cppy::incref( weak_methods ) );
    cppy:::ptr wrptr( cppy::incref( wr_item ) );
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
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "enaml.weakmethod.WeakMethod",             /* tp_name */
    sizeof( WeakMethod ),                      /* tp_basicsize */
    0,                                         /* tp_itemsize */
    ( destructor )WeakMethod_dealloc,          /* tp_dealloc */
    ( printfunc )0,                            /* tp_print */
    ( getattrfunc )0,                          /* tp_getattr */
    ( setattrfunc )0,                          /* tp_setattr */
	( PyAsyncMethods* )0,                      /* tp_as_async */
    ( reprfunc )0,                             /* tp_repr */
    ( PyNumberMethods* )0,                     /* tp_as_number */
    ( PySequenceMethods* )0,                   /* tp_as_sequence */
    ( PyMappingMethods* )0,                    /* tp_as_mapping */
    ( hashfunc )0,                             /* tp_hash */
    ( ternaryfunc )WeakMethod_call,            /* tp_call */
    ( reprfunc )0,                             /* tp_str */
    ( getattrofunc )0,                         /* tp_getattro */
    ( setattrofunc )0,                         /* tp_setattro */
    ( PyBufferProcs* )0,                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT
    |Py_TPFLAGS_BASETYPE
    |Py_TPFLAGS_HAVE_GC,                       /* tp_flags */
    WeakMethod__doc__,                         /* Documentation string */
    ( traverseproc )WeakMethod_traverse,       /* tp_traverse */
    ( inquiry )WeakMethod_clear,               /* tp_clear */
    ( richcmpfunc )0,                          /* tp_richcompare */
    offsetof( WeakMethod, weakreflist ),       /* tp_weaklistoffset */
    ( getiterfunc )0,                          /* tp_iter */
    ( iternextfunc )0,                         /* tp_iternext */
    ( struct PyMethodDef* )WeakMethod_methods, /* tp_methods */
    ( struct PyMemberDef* )0,                  /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    ( descrgetfunc )0,                         /* tp_descr_get */
    ( descrsetfunc )0,                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    ( initproc )0,                             /* tp_init */
    ( allocfunc )PyType_GenericAlloc,          /* tp_alloc */
    ( newfunc )WeakMethod_new,                 /* tp_new */
    ( freefunc )0,                             /* tp_free */
    ( inquiry )0,                              /* tp_is_gc */
    0,                                         /* tp_bases */
    0,                                         /* tp_mro */
    0,                                         /* tp_cache */
    0,                                         /* tp_subclasses */
    0,                                         /* tp_weaklist */
    ( destructor )0                            /* tp_del */
};

struct module_state {
    PyObject *error;
};


static PyMethodDef
weakmethod_methods[] = {
    { 0 } // Sentinel
};


#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int weakmethod_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int weakmethod_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "weakmethod",
        NULL,
        sizeof(struct module_state),
        weakmethod_methods,
        NULL,
        weakmethod_traverse,
        weakmethod_clear,
        NULL
};


PyMODINIT_FUNC PyInit_weakmethod( void )
{
    cppy::ptr mod( PyModule_Create(&moduledef) );
    if( !mod )
        return NULL;
    weak_methods = PyDict_New();
    if( !weak_methods )
        return NULL;

    remove_str = PyUnicode_FromString( "_remove" );
    if( !remove_str )
        return NULL;

    if( PyType_Ready( &WeakMethod_Type ) )
        return NULL;

    cppy::ptr wm_type( cppy::incref( pyobject_cast( &WeakMethod_Type ) ) );
    PyModule_AddObject( mod.get(), "WeakMethod", wm_type.release() );

    return mod;
}

} // extern "C"

