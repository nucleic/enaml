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
struct DFunc
{
	PyObject_HEAD
    PyObject* im_func;  // always a function
    PyObject* im_key;   // anything

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


// POD struct - all member fields are considered private
struct BoundDMethod
{
	PyObject_HEAD
    PyObject* im_func;  // always a function
    PyObject* im_self;  // anything
    PyObject* im_key;   // anything

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

    static PyObject* New( PyObject* im_func, PyObject* im_self, PyObject* im_key );

};


namespace
{


static PyObject* DynamicScope;
static PyObject* call_func;
static PyObject* super_disallowed;


#define FREELIST_MAX 128
static int numfree = 0;
static BoundDMethod* freelist[ FREELIST_MAX ];


PyObject*
_SuperDisallowed( PyObject* mod, PyObject* args, PyObject* kwargs)
{
    return cppy::type_error( "super() is not allowed in a declarative function, "
                             " use SomeClass.some_method(self, ...) instead." );
}


/* Internal function used whan calling a DeclarativeFunc or
BoundDeclarativeMethod */
PyObject*
_Invoke( PyObject* func, PyObject* key, PyObject* self, PyObject* args,
         PyObject* kwargs )
{
    cppy::ptr pfunc( cppy::incref( func ) );
    cppy::ptr f_globals( pfunc.getattr( "__globals__" ) );
    if( !f_globals )
        return cppy::attribute_error( pfunc.get(), "__globals__" );
    cppy::ptr f_builtins( PyDict_GetItemString( f_globals.get(), "__builtins__" ) );
    if( !f_builtins ){
        PyErr_Format(
            PyExc_KeyError,
            "'%s'.__globals__ object has no key '%s'",
            Py_TYPE( func )->tp_name, "__builtins__"
        );
        return 0;
    }
    cppy::ptr pself( cppy::incref( self ) );
    cppy::ptr d_storage( pself.getattr( "_d_storage" ) );
    if( !d_storage )
        return cppy::attribute_error( pself.get(), "_d_storage" );

    cppy::ptr empty( PyDict_New() );
    cppy::ptr f_locals( PyObject_CallMethod( d_storage.get(), "get", "OO", key, empty.get() ) );
    cppy::ptr scope(
        PyObject_CallFunctionObjArgs( DynamicScope, self, f_locals.get(),
                                      f_globals.get(),
                                      f_builtins.get(), 0 )
        );
    if( PyMapping_SetItemString( scope.get(), "super", cppy::incref( super_disallowed ) ) == -1 )
        return cppy::system_error( "Failed to set key super in dynamic scope" );

    cppy::ptr pkw( cppy::xincref( kwargs ) );
    if( !pkw )
        pkw.set( PyDict_New() );
    return PyObject_CallFunctionObjArgs( call_func, func, args, pkw.get(), scope.get(), 0 );
}


PyObject*
DFunc_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* self = PyType_GenericNew( type, args, kwargs );
    if( !self )
        return 0;
    PyObject* im_func;
    PyObject* im_key;
    static char *kwlist[] = { "im_func", "im_key", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "OO:__new__", kwlist, &im_func, &im_key ) )
        return 0;
    if( !PyFunction_Check( im_func ) )
        return cppy::type_error( im_func, "function" );
    DFunc* df = reinterpret_cast<DFunc*>( self );
    df->im_func = cppy::incref( im_func );
    df->im_key = cppy::incref( im_key );
    return self;
}


void
DFunc_clear( DFunc* self )
{
    Py_CLEAR( self->im_func );
    Py_CLEAR( self->im_key );
}


int
DFunc_traverse( DFunc* self, visitproc visit, void* arg )
{
    Py_VISIT( self->im_func );
    Py_VISIT( self->im_key );
    return 0;
}


void
DFunc_dealloc( DFunc* self )
{
    DFunc_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
DFunc_repr( DFunc* self )
{
    std::ostringstream ostr;
    ostr << "<declarative function ";
    cppy::ptr mod( PyObject_GetAttrString( self->im_func, "__module__" ) );
    if( mod && PyUnicode_Check( mod.get() ) )
        ostr << PyUnicode_AsUTF8( mod.get() ) << ".";
    cppy::ptr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && PyUnicode_Check( name.get() ) )
        ostr << PyUnicode_AsUTF8( name.get() );
    ostr << ">";
    return PyUnicode_FromString( ostr.str().c_str() );
}


PyObject*
DFunc__get__( DFunc* self, PyObject* im_self, PyObject* type )
{
    if( !im_self )
        return cppy::incref( pyobject_cast( self ) );
    return BoundDMethod::New( self->im_func, im_self, self->im_key );
}


PyObject*
DFunc__call__( DFunc* self, PyObject* args, PyObject* kwargs )
{
    cppy::ptr argsptr( cppy::incref( args ) );
    Py_ssize_t args_size = PyTuple_GET_SIZE( argsptr.get() );
    if( args_size == 0 )
    {
        std::ostringstream ostr;
        ostr << "DeclarativeFunction.__call__() takes at least 1 argument (";
        ostr << args_size << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }
    cppy::ptr pself( cppy::incref( PyTuple_GET_ITEM( argsptr.get(), 0 ) ) );
    cppy::ptr pargs( PyTuple_GetSlice( argsptr.get(), 1, args_size ) );
    if( !pargs )
        return cppy::system_error( "DeclarativeFunction.__call__ failed to "
                                   "slice arguments." );
    return _Invoke( self->im_func, self->im_key, pself.get(), pargs.get(), kwargs );
}


PyObject*
DFunc_get_func( DFunc* self, void* ctxt )
{
    return cppy::incref( self->im_func );
}


PyObject*
DFunc_get_key( DFunc* self, void* ctxt )
{
    return cppy::incref( self->im_key );
}

PyObject*
DFunc_get_d_func( DFunc* self, void* ctxt )
{
    Py_INCREF(Py_True);
    return Py_True;
}


PyGetSetDef
DFunc_getset[] = {
    { "__func__", ( getter )DFunc_get_func, 0,
      "Get the function invoked by this declarative function." },
    { "__key__", ( getter )DFunc_get_key, 0,
      "Get the scope key for this declarative function." },
    {"_d_func", ( getter )DFunc_get_d_func, 0,
     " An internal compiler metadata flag.\n\n"
     "This allows the function to be overridden from Enaml syntax.\n"},
    { 0 } // sentinel
};


static PyType_Slot DFunc_Type_slots[] = {
    { Py_tp_dealloc, void_cast( DFunc_dealloc ) },        /* tp_dealloc */
    { Py_tp_traverse, void_cast( DFunc_traverse ) },      /* tp_traverse */
    { Py_tp_clear, void_cast( DFunc_clear ) },            /* tp_clear */
    { Py_tp_getset, void_cast( DFunc_getset ) },          /* tp_getset */
    { Py_tp_descr_get, void_cast( DFunc__get__ ) },       /* tp_descr_get */
    { Py_tp_call, void_cast( DFunc__call__ ) },           /* tp_call */
    { Py_tp_repr, void_cast( DFunc_repr ) },              /* tp_repr */
    { Py_tp_new, void_cast( DFunc_new ) },                /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },    /* tp_alloc */
    { Py_tp_free, void_cast( PyObject_GC_Del ) },         /* tp_free */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* DFunc::TypeObject = NULL;


PyType_Spec DFunc::TypeObject_Spec = {
	"enaml.declarative_function.DeclarativeFunction",    /* tp_name */
	sizeof( DFunc ),                                     /* tp_basicsize */
	0,                                                   /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_HAVE_GC,                                  /* tp_flags */
    DFunc_Type_slots                                     /* slots */
};


bool DFunc::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


namespace
{


void
BoundDMethod_clear( BoundDMethod* self )
{
    Py_CLEAR( self->im_func );
    Py_CLEAR( self->im_self );
    Py_CLEAR( self->im_key );
}


int
BoundDMethod_traverse( BoundDMethod* self, visitproc visit, void* arg )
{
    Py_VISIT( self->im_func );
    Py_VISIT( self->im_self );
    Py_VISIT( self->im_key );
    return 0;
}


void
BoundDMethod_dealloc( BoundDMethod* self )
{
    PyObject_GC_UnTrack( self );
    BoundDMethod_clear( self );
    if( numfree < FREELIST_MAX )
        freelist[ numfree++ ] = self;
    else
        Py_TYPE( self )->tp_free( pyobject_cast( self ) );
}


PyObject*
BoundDMethod_repr( BoundDMethod* self )
{
    std::ostringstream ostr;
    ostr << "<bound declarative method ";
    cppy::ptr cls( PyObject_GetAttrString(
        pyobject_cast( Py_TYPE( self->im_self ) ), "__name__" ) );
    if( cls && PyUnicode_Check( cls.get() ) )
        ostr << PyUnicode_AsUTF8( cls.get() ) << ".";
    cppy::ptr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && PyUnicode_Check( name.get() ) )
        ostr << PyUnicode_AsUTF8( name.get() );
    cppy::ptr obj( PyObject_Repr( self->im_self ) );
    if( obj && PyUnicode_Check( obj.get() ) )
        ostr << " of " << PyUnicode_AsUTF8( obj.get() );
    ostr << ">";
    return PyUnicode_FromString( ostr.str().c_str() );
}


PyObject*
BoundDMethod__call__( BoundDMethod* self, PyObject* args, PyObject* kwargs )
{
    return _Invoke( self->im_func, self->im_key, self->im_self, args, kwargs );
}


PyObject*
BoundDMethod_get_func( BoundDMethod* self, void* ctxt )
{
    return cppy::incref( self->im_func );
}


PyObject*
BoundDMethod_get_self( BoundDMethod* self, void* ctxt )
{
    return cppy::incref( self->im_self );
}


PyObject*
BoundDMethod_get_key( BoundDMethod* self, void* ctxt )
{
    return cppy::incref( self->im_key );
}


static PyGetSetDef
BoundDMethod_getset[] = {
    { "__func__", ( getter )BoundDMethod_get_func, 0,
      "Get the function invoked by this declarative method." },
    { "__self__", ( getter )BoundDMethod_get_self, 0,
      "Get the self reference for this declarative method." },
    { "__key__", ( getter )BoundDMethod_get_key, 0,
      "Get the scope key for this declarative method." },
    { 0 } // sentinel
};


static PyType_Slot BoundDMethod_Type_slots[] = {
    { Py_tp_dealloc, void_cast( BoundDMethod_dealloc ) },        /* tp_dealloc */
    { Py_tp_traverse, void_cast( BoundDMethod_traverse ) },      /* tp_traverse */
    { Py_tp_clear, void_cast( BoundDMethod_clear ) },            /* tp_clear */
    { Py_tp_getset, void_cast( BoundDMethod_getset ) },          /* tp_getset */
    { Py_tp_call, void_cast( BoundDMethod__call__ ) },              /* tp_call */
    { Py_tp_repr, void_cast( BoundDMethod_repr ) },              /* tp_repr */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },           /* tp_alloc */
    { Py_tp_free, void_cast( PyObject_GC_Del ) },                /* tp_free */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* BoundDMethod::TypeObject = NULL;


PyType_Spec BoundDMethod::TypeObject_Spec = {
	"enaml.declarative_function.BoundDeclarativeMethod",    /* tp_name */
	sizeof( BoundDMethod ),                                 /* tp_basicsize */
	0,                                                      /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_HAVE_GC,                                     /* tp_flags */
    BoundDMethod_Type_slots                                 /* slots */
};


bool BoundDMethod::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}

PyObject*
BoundDMethod::New( PyObject* im_func, PyObject* im_self, PyObject* im_key )
{
    PyObject* pymethod;
    if( numfree > 0 )
    {
        pymethod = pyobject_cast( freelist[ --numfree ] );
        _Py_NewReference( pymethod );
    }
    else
    {
        pymethod = PyType_GenericAlloc( BoundDMethod::TypeObject, 0 );
        if( !pymethod )
            return 0;
    }
    BoundDMethod* method = reinterpret_cast<BoundDMethod*>( pymethod );
    method->im_func = cppy::incref( im_func );
    method->im_self = cppy::incref( im_self );
    method->im_key = cppy::incref( im_key );
    return pymethod;
}


// Module definition
namespace
{


int
declarative_function_modexec( PyObject *mod )
{
    // Borrowed reference
    PyObject* mod_dict = PyModule_GetDict( mod );

    cppy::ptr dm_mod( PyImport_ImportModuleLevel( "dynamicscope", mod_dict, 0, 0 , 1) );
    if( !dm_mod)
    {
        return -1;
    }
    cppy::ptr dm_cls( dm_mod.getattr( "DynamicScope" ) );
    if( !dm_cls )
    {
        return -1;
    }

    cppy::ptr fh_mod( PyImport_ImportModuleLevel( "funchelper", mod_dict, 0, 0, 1 ) );
    if( !fh_mod )
    {
        return -1;
    }
    cppy::ptr fh_cls( fh_mod.getattr( "call_func" ) );
    if( !fh_cls )
    {
        return -1;
    }

    cppy::ptr sup( PyObject_GetAttrString( mod, "_super_disallowed" ) );
    if( !sup )
    {
        return -1;
    }

    if( !DFunc::Ready() )
    {
        return -1;
    }
    if( !BoundDMethod::Ready() )
    {
        return -1;
    }

    // DFunc
    cppy::ptr dfunc( pyobject_cast( DFunc::TypeObject ) );
	if( PyModule_AddObject( mod, "DeclarativeFunction", dfunc.get() ) < 0 )
	{
		return -1;
	}
    dfunc.release();

    // BoundDMethod
    cppy::ptr bdfunc( pyobject_cast( BoundDMethod::TypeObject ) );
	if( PyModule_AddObject( mod, "BoundDeclarativeMethod", bdfunc.get() ) < 0 )
	{
		return -1;
	}
    bdfunc.release();

    DynamicScope = dm_cls.release();
    call_func = fh_cls.release();
    super_disallowed = sup.release();

    return 0;
}


static PyMethodDef
declarative_function_methods[] = {
    {"_super_disallowed", ( PyCFunction )_SuperDisallowed,
     METH_VARARGS | METH_KEYWORDS, "Forbid use of super in declarative function"},
    { 0 }  // Sentinel
};


PyModuleDef_Slot declarative_function_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( declarative_function_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "declarative_function",
        "declarative_function extension module",
        0,
        declarative_function_methods,
        declarative_function_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_declarative_function( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
