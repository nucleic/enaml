/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include <cppy/cppy.h>
#include <structmember.h>  // Included to access offsetof


namespace enaml
{

// POD struct - all member fields are considered private
struct WeakMethod
{
	PyObject_HEAD
    PyObject* weakreflist;  // weakrefs to this object
    PyObject* func;         // method.im_func
    PyObject* selfref;      // weakref.ref(method.im_self)
    PyObject* cls;          // method.im_class

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


namespace
{


// A dict where a key is weakref.ref(method.im_self) and the value is a
// list of WeakMethod instances for that object. This is initialized in
// the module init function. This is not declared as a PyObjectPtr since
// a destructor being run on dlclose() has the potential to call the
// tp_dealloc slot after interpreter shut down.
static PyObject* weak_methods;


// A preallocated string object to lookup the `_remove` staticmethod.
static PyObject* remove_str;


PyObject*
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

    cppy::ptr wmethods_ptr( cppy::incref( weak_methods ) );
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
    Py_ssize_t size = PyList_Size( items.get() );
    for( Py_ssize_t idx = 0; idx < size; idx++ )
    {
        cppy::ptr wmptr( cppy::incref( PyList_GET_ITEM( items.get(), idx ) ) );
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


void
WeakMethod_clear( WeakMethod* self )
{
    Py_CLEAR( self->func );
    Py_CLEAR( self->selfref );
    Py_CLEAR( self->cls );
}


int
WeakMethod_traverse( WeakMethod* self, visitproc visit, void* arg )
{
    Py_VISIT( self->func );
    Py_VISIT( self->selfref );
    Py_VISIT( self->cls );
    return 0;
}


void
WeakMethod_dealloc( WeakMethod* self )
{
    PyObject_GC_UnTrack( self );
    if( self->weakreflist )
        PyObject_ClearWeakRefs( pyobject_cast( self ) );
    WeakMethod_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
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
    return method.call( argsptr, kwargsptr );
}


// A staticmethod fired by the object underlyling a weakref used as the
// key in the weak_methods dict when it is garbage collected. This will
// remove the entry from the dict and allows the WeakMethod instances
// to be garbage collected.
PyObject*
WeakMethod__remove( PyObject* ignored, PyObject* wr_item )
{
    cppy::ptr wmethods_ptr( cppy::incref( weak_methods ) );
    cppy::ptr wrptr( cppy::incref( wr_item ) );
    if( !wmethods_ptr.delitem( wrptr ) )
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


static PyType_Slot WeakMethod_Type_slots[] = {
    { Py_tp_dealloc, void_cast( WeakMethod_dealloc ) },          /* tp_dealloc */
    { Py_tp_traverse, void_cast( WeakMethod_traverse ) },        /* tp_traverse */
    { Py_tp_clear, void_cast( WeakMethod_clear ) },              /* tp_clear */
    { Py_tp_methods, void_cast( WeakMethod_methods ) },          /* tp_doc */
    { Py_tp_doc, cast_py_tp_doc( WeakMethod__doc__ ) },          /* tp_doc */
    { Py_tp_call, void_cast( WeakMethod_call ) },                /* tp_call */
    { Py_tp_new, void_cast( WeakMethod_new ) },                  /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },           /* tp_alloc */
    /* tp_weaklistoffset cannot be in slots we will set after type creation
       cf https://github.com/pyside/pyside2-setup/blob/5.11/sources/shiboken2/libshiboken/pep384impl_doc.rst */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* WeakMethod::TypeObject = NULL;


PyType_Spec WeakMethod::TypeObject_Spec = {
	"enaml.weakmethod.WeakMethod",              /* tp_name */
	sizeof( WeakMethod ),                       /* tp_basicsize */
	0,                                          /* tp_itemsize */
	Py_TPFLAGS_DEFAULT
    |Py_TPFLAGS_BASETYPE
    |Py_TPFLAGS_HAVE_GC,                         /* tp_flags */
    WeakMethod_Type_slots                        /* slots */
};


bool WeakMethod::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    // Delayed setting of weaklistoffset
    TypeObject->tp_weaklistoffset = offsetof( WeakMethod, weakreflist );
    return true;
}


// Module definition
namespace
{


int
weakmethod_modexec( PyObject *mod )
{
    weak_methods = PyDict_New();
    if( !weak_methods )
    {
        return -1;
    }

    remove_str = PyUnicode_FromString( "_remove" );
    if( !remove_str )
    {
        return -1;
    }

    if( !WeakMethod::Ready() )
    {
        return -1;
    }

    // Signal
    cppy::ptr wmethod( pyobject_cast( WeakMethod::TypeObject ) );
	if( PyModule_AddObject( mod, "WeakMethod", wmethod.get() ) < 0 )
	{
		return -1;
	}
    wmethod.release();

    return 0;
}

static PyMethodDef
weakmethod_methods[] = {
    { 0 } // sentinel
};


PyModuleDef_Slot weakmethod_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( weakmethod_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "weakmethod",
        "weakmethod extension module",
        0,
        weakmethod_methods,
        weakmethod_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_weakmethod( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
