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

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif


namespace enaml
{

// POD struct - all member fields are considered private
struct CallableRef
{
	PyObject_HEAD
    PyObject* objref;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

    static bool TypeCheck( PyObject* ob );

};


namespace
{


PyObject*
CallableRef_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* obj;
    PyObject* cb = 0;
    static char* kwlist[] = { "method", "callback", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "O|O", kwlist, &obj, &cb ) )
        return 0;
    cppy::ptr crefptr( PyType_GenericNew( type, args, kwargs ) );
    if( !crefptr )
        return 0;
    CallableRef* cref = reinterpret_cast<CallableRef*>( crefptr.get() );
    cref->objref = PyWeakref_NewRef( obj, cb );
    if( !cref->objref )
        return 0;
    return crefptr.release();
}


void
CallableRef_clear( CallableRef* self )
{
    Py_CLEAR( self->objref );
}


int
CallableRef_traverse( CallableRef* self, visitproc visit, void* arg )
{
    Py_VISIT( self->objref );
    return 0;
}


void
CallableRef_dealloc( CallableRef* self )
{
    PyObject_GC_UnTrack( self );
    CallableRef_clear( self );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


PyObject*
CallableRef_call( CallableRef* self, PyObject* args, PyObject* kwargs )
{
    cppy::ptr objrefptr( cppy::incref( self->objref ) );
    cppy::ptr objptr( PyWeakref_GET_OBJECT( objrefptr.get() ) );
    if( objptr.is_none() )
        Py_RETURN_NONE;
    cppy::ptr argsptr( cppy::incref( args ) );
    cppy::ptr kwargsptr( cppy::incref( kwargs ) );
    return objptr.call( argsptr, kwargsptr );
}


PyObject*
CallableRef_richcompare( CallableRef* self, PyObject* other, int opid )
{
    if( opid == Py_EQ )
    {
        cppy::ptr sref( cppy::incref( self->objref ) );
        if( CallableRef::TypeCheck( other ) )
        {
            CallableRef* cref_other = reinterpret_cast<CallableRef*>( other );
            cppy::ptr oref( cppy::incref( cref_other->objref ) );
            if( sref.richcmp( oref, Py_EQ ) )
                Py_RETURN_TRUE;
            Py_RETURN_FALSE;
        }
        if( PyWeakref_CheckRef( other ) )
        {
            cppy::ptr oref( cppy::incref( other ) );
            if( sref.richcmp( oref, Py_EQ ) )
                Py_RETURN_TRUE;
            Py_RETURN_FALSE;
        }
        Py_RETURN_FALSE;
    }
    Py_RETURN_NOTIMPLEMENTED;
}


PyDoc_STRVAR(CallableRef__doc__,
"CallableRef(object[, callback])\n\n"
"This class is useful when weakrefs to callable objects need to be\n"
"used alongside regular callables. It exposes a callable interface\n"
"which will dereference the underlying callable before calling it.\n\n"
"Parameters\n"
"----------\n"
"obj : callable\n"
"    The callable object which should be weakly wrapped.\n\n"
"callback : callable or None\n"
"    An optional callable to invoke when the object has been\n"
"    garbage collected. It will be passed the weakref instance\n"
"    associated with the dead object.\n\n"
"Notes\n"
"-----\n"
"Instances of this class will compare equally to equivalent\n"
"CallableRef instances as well as weakref instances which\n"
"compare equally to the internal weakref.\n\n");


static PyType_Slot CallableRef_Type_slots[] = {
    { Py_tp_dealloc, void_cast( CallableRef_dealloc ) },          /* tp_dealloc */
    { Py_tp_traverse, void_cast( CallableRef_traverse) },         /* tp_traverse */
    { Py_tp_clear, void_cast( CallableRef_clear ) },              /* tp_clear */
    { Py_tp_call, void_cast( CallableRef_call ) },                /* tp_call */
    { Py_tp_doc, cast_py_tp_doc( CallableRef__doc__ ) },          /* tp_doc */
    { Py_tp_richcompare, void_cast( CallableRef_richcompare ) },  /* tp_methods */
    { Py_tp_new, void_cast( CallableRef_new ) },                  /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },            /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* CallableRef::TypeObject = NULL;


PyType_Spec CallableRef::TypeObject_Spec = {
	"enaml.callableref.CallableRef",     /* tp_name */
	sizeof( CallableRef ),               /* tp_basicsize */
	0,                                   /* tp_itemsize */
	Py_TPFLAGS_DEFAULT
    |Py_TPFLAGS_BASETYPE
    |Py_TPFLAGS_HAVE_GC,                 /* tp_flags */
    CallableRef_Type_slots               /* slots */
};


bool CallableRef::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


bool CallableRef::TypeCheck( PyObject* ob )
{
    return PyObject_TypeCheck( ob, TypeObject ) != 0;
}


// Module definition
namespace
{


int
callableref_modexec( PyObject *mod )
{
    if( !CallableRef::Ready() )
    {
        return -1;
    }

    // callableref
    cppy::ptr callableref( pyobject_cast(  CallableRef::TypeObject ) );
	if( PyModule_AddObject( mod, "CallableRef", callableref.get() ) < 0 )
	{
		return -1;
	}
    callableref.release();

    return 0;
}


PyMethodDef
callableref_methods[] = {
    { 0 } // Sentinel
};


PyModuleDef_Slot callableref_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( callableref_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "callableref",
        "callableref extension module",
        0,
        callableref_methods,
        callableref_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_callableref( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
