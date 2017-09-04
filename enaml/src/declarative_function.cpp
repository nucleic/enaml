/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include "pythonhelpersex.h"
#include "py23compat.h"

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif

using namespace PythonHelpers;


PyObject* DynamicScope;
PyObject* call_func;
PyObject* super_disallowed;


typedef struct {
    PyObject_HEAD
    PyObject* im_func;  // always a function
    PyObject* im_key;   // anything
} DFunc;


typedef struct {
    PyObject_HEAD
    PyObject* im_func;  // always a function
    PyObject* im_self;  // anything
    PyObject* im_key;   // anything
} BoundDMethod;


#define FREELIST_MAX 128
static int numfree = 0;
static BoundDMethod* freelist[ FREELIST_MAX ];


static PyObject*
_SuperDisallowed( PyObject* mod, PyObject* args, PyObject* kwargs)
{
    return py_type_fail( "super() is not allowed in a declarative function, "
                         " use SomeClass.some_method(self, ...) instead." );
}


/*Internal function used whan calling a DeclarativeFunc or
BoundDeclarativeMethod*/
static PyObject*
_Invoke( PyObject* func, PyObject* key, PyObject* self, PyObject* args,
         PyObject* kwargs )
{
    PyObjectPtr pfunc( newref( func ) );
    PyDictPtr f_globals( pfunc.getattr("__globals__") );
    if( !f_globals )
        return py_no_attr_fail( pfunc.get(), "__globals__" );
    PyObjectPtr f_builtins( f_globals.get_item( "__builtins__" ) );
    if( !f_builtins ){
        PyErr_Format(
            PyExc_KeyError,
            "'%s'.__globals__ object has no key '%s'",
            Py_TYPE( func )->tp_name, "__builtins__"
        );
        return 0;
    }
    PyObjectPtr pself( newref( self ) );
    PyDictPtr d_storage( pself.getattr("_d_storage") );
    if( !d_storage )
        return py_no_attr_fail( pself.get(), "_d_storage" );

    PyObjectPtr empty( PyDict_New() );
    PyObjectPtr f_locals( PyObject_CallMethod( d_storage.get(), "get", "OO", key, empty.get() ) );
    PyObjectPtr scope(
        PyObject_CallFunctionObjArgs( DynamicScope, self, f_locals.get(),
                                      f_globals.get(),
                                      f_builtins.get(), 0 )
        );
    if( PyMapping_SetItemString( scope.get(), "super", newref( super_disallowed ) ) == -1 )
        return py_bad_internal_call("Failed to set key super in dynamic scope");

    PyObjectPtr pkw( xnewref( kwargs ) );
    if( !pkw )
        pkw.set( PyDict_New() );
    return PyObject_CallFunctionObjArgs( call_func, func, args, pkw.get(), scope.get(), 0 );
}


static PyObject*
BoundDMethod_New( PyObject* im_func, PyObject* im_self, PyObject* im_key );


static PyObject*
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
        return py_expected_type_fail( im_func, "function" );
    DFunc* df = reinterpret_cast<DFunc*>( self );
    df->im_func = newref( im_func );
    df->im_key = newref( im_key );
    return self;
}


static void
DFunc_clear( DFunc* self )
{
    Py_CLEAR( self->im_func );
    Py_CLEAR( self->im_key );
}


static int
DFunc_traverse( DFunc* self, visitproc visit, void* arg )
{
    Py_VISIT( self->im_func );
    Py_VISIT( self->im_key );
    return 0;
}


static void
DFunc_dealloc( DFunc* self )
{
    DFunc_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


static PyObject*
DFunc_repr( DFunc* self )
{
    std::ostringstream ostr;
    ostr << "<declarative function ";
    PyObjectPtr mod( PyObject_GetAttrString( self->im_func, "__module__" ) );
    if( mod && Py23Str_Check( mod.get() ) )
        ostr << Py23Str_AS_STRING( mod.get() ) << ".";
    PyObjectPtr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && Py23Str_Check( name.get() ) )
        ostr << Py23Str_AS_STRING( name.get() );
    ostr << ">";
    return Py23Str_FromFormat( ostr.str().c_str() );
}


static PyObject*
DFunc__get__( DFunc* self, PyObject* im_self, PyObject* type )
{
    if( !im_self )
        return newref( pyobject_cast( self ) );
    return BoundDMethod_New( self->im_func, im_self, self->im_key );
}


static PyObject*
DFunc__call__( DFunc* self, PyObject* args, PyObject* kwargs )
{
    PyTuplePtr argsptr( args );
    if( argsptr.size() == 0 )
    {
        std::ostringstream ostr;
        ostr << "DeclarativeFunction.__call__() takes at least 1 argument (";
        ostr << argsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }
    PyObjectPtr pself( argsptr.get_item(0) );
    PyTuplePtr pargs( PyTuple_GetSlice( argsptr.get(), 1, argsptr.size() ) );
    if( !pargs )
        return py_bad_internal_call("DeclarativeFunction.__call__ failed to "
                                    "slice arguments.");
    return _Invoke( self->im_func, self->im_key, pself.get(), pargs.get(), kwargs );
}


static PyObject*
DFunc_get_func( DFunc* self, void* ctxt )
{
    return newref( self->im_func );
}


static PyObject*
DFunc_get_key( DFunc* self, void* ctxt )
{
    return newref( self->im_key );
}

static PyObject*
DFunc_get_d_func( DFunc* self, void* ctxt )
{
    Py_INCREF(Py_True);
    return Py_True;
}


static PyGetSetDef
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


PyTypeObject DFunc_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "declarative_function.DeclarativeFunction",       /* tp_name */
    sizeof( DFunc ),                        /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)DFunc_dealloc,              /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
#if PY_VERSION_HEX >= 0x03050000
	( PyAsyncMethods* )0,                   /* tp_as_async */
#elif PY_VERSION_HEX >= 0x03000000
	( void* ) 0,                            /* tp_reserved */
#else
	( cmpfunc )0,                           /* tp_compare */
#endif
    (reprfunc)DFunc_repr,                   /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)DFunc__call__,             /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)DFunc_traverse,           /* tp_traverse */
    (inquiry)DFunc_clear,                   /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)0,                 /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    DFunc_getset,                           /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)DFunc__get__,             /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)DFunc_new,                     /* tp_new */
    (freefunc)PyObject_GC_Del,              /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static void
BoundDMethod_clear( BoundDMethod* self )
{
    Py_CLEAR( self->im_func );
    Py_CLEAR( self->im_self );
    Py_CLEAR( self->im_key );
}


static int
BoundDMethod_traverse( BoundDMethod* self, visitproc visit, void* arg )
{
    Py_VISIT( self->im_func );
    Py_VISIT( self->im_self );
    Py_VISIT( self->im_key );
    return 0;
}


static void
BoundDMethod_dealloc( BoundDMethod* self )
{
    PyObject_GC_UnTrack( self );
    BoundDMethod_clear( self );
    if( numfree < FREELIST_MAX )
        freelist[ numfree++ ] = self;
    else
        Py_TYPE( self )->tp_free( pyobject_cast( self ) );
}


static PyObject*
BoundDMethod_repr( BoundDMethod* self )
{
    std::ostringstream ostr;
    ostr << "<bound declarative method ";
    PyObjectPtr cls( PyObject_GetAttrString(
        pyobject_cast( Py_TYPE( self->im_self ) ), "__name__" ) );
    if( cls && Py23Str_Check( cls.get() ) )
        ostr << Py23Str_AS_STRING( cls.get() ) << ".";
    PyObjectPtr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && Py23Str_Check( name.get() ) )
        ostr << Py23Str_AS_STRING( name.get() );
    PyObjectPtr obj( PyObject_Repr( self->im_self ) );
    if( obj && Py23Str_Check( obj.get() ) )
        ostr << " of " << Py23Str_AS_STRING( obj.get() );
    ostr << ">";
    return Py23Str_FromString( ostr.str().c_str() );
}


static PyObject*
BoundDMethod__call__( BoundDMethod* self, PyObject* args, PyObject* kwargs )
{
    return _Invoke( self->im_func, self->im_key, self->im_self, args, kwargs );
}


static PyObject*
BoundDMethod_get_func( BoundDMethod* self, void* ctxt )
{
    return newref( self->im_func );
}


static PyObject*
BoundDMethod_get_self( BoundDMethod* self, void* ctxt )
{
    return newref( self->im_self );
}


static PyObject*
BoundDMethod_get_key( BoundDMethod* self, void* ctxt )
{
    return newref( self->im_key );
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


PyTypeObject BoundDMethod_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "declarative_function.BoundDeclarativeMethod",  /* tp_name */
    sizeof( BoundDMethod ),                 /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)BoundDMethod_dealloc,       /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
#if PY_VERSION_HEX >= 0x03050000
	( PyAsyncMethods* )0,                 /* tp_as_async */
#elif PY_VERSION_HEX >= 0x03000000
	( void* ) 0,                          /* tp_reserved */
#else
	( cmpfunc )0,                         /* tp_compare */
#endif
    (reprfunc)BoundDMethod_repr,            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)BoundDMethod__call__,      /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)BoundDMethod_traverse,    /* tp_traverse */
    (inquiry)BoundDMethod_clear,            /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)0,                 /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    BoundDMethod_getset,                    /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)0,                             /* tp_new */
    (freefunc)PyObject_GC_Del,              /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyObject*
BoundDMethod_New( PyObject* im_func, PyObject* im_self, PyObject* im_key )
{
    PyObject* pymethod;
    if( numfree > 0 )
    {
        pymethod = pyobject_cast( freelist[ --numfree ] );
        _Py_NewReference( pymethod );
    }
    else
    {
        pymethod = PyType_GenericAlloc( &BoundDMethod_Type, 0 );
        if( !pymethod )
            return 0;
    }
    BoundDMethod* method = reinterpret_cast<BoundDMethod*>( pymethod );
    method->im_func = newref( im_func );
    method->im_self = newref( im_self );
    method->im_key = newref( im_key );
    return pymethod;
}


struct module_state {
    PyObject *error;
};


static PyMethodDef
declarative_function_methods[] = {
    {"_super_disallowed", ( PyCFunction )_SuperDisallowed,
     METH_VARARGS | METH_KEYWORDS, "Forbid use of super in declarative function"},
    { 0 }  // Sentinel
};

#if PY_MAJOR_VERSION >= 3

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int declarative_function_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int declarative_function_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "declarative_function",
        NULL,
        sizeof(struct module_state),
        declarative_function_methods,
        NULL,
        declarative_function_traverse,
        declarative_function_clear,
        NULL
};

#else

#define GETSTATE(m) (&_state)
static struct module_state _state;

#endif

MOD_INIT_FUNC(declarative_function)
{
#if PY_MAJOR_VERSION >= 3
    PyObjectPtr mod( xnewref( PyModule_Create(&moduledef) ) );
#else
    PyObjectPtr mod( xnewref( Py_InitModule( "declarative_function", declarative_function_methods ) ) );
#endif
    if( !mod )
        INITERROR;
    PyObject* mod_dict = PyModule_GetDict( mod.get() );

    PyObjectPtr dm_mod( PyImport_ImportModuleLevel( "dynamicscope", mod_dict, 0, 0 , 1) );
    if( !dm_mod)
        INITERROR;
    PyObjectPtr dm_cls( dm_mod.getattr( "DynamicScope" ) );
    if( !dm_cls )
        INITERROR;

    PyObjectPtr fh_mod( PyImport_ImportModuleLevel( "funchelper", mod_dict, 0, 0, 1 ) );
    if( !fh_mod )
        INITERROR;
    PyObjectPtr fh_cls( fh_mod.getattr( "call_func" ) );
    if( !fh_cls )
        INITERROR;

    PyObjectPtr sup( mod.getattr( "_super_disallowed" ) );
    if( !sup )
        INITERROR;

    DynamicScope = dm_cls.release();
    call_func = fh_cls.release();
    super_disallowed = sup.release();

    if( PyType_Ready( &DFunc_Type ) < 0 )
        INITERROR;
    if( PyType_Ready( &BoundDMethod_Type ) < 0 )
        INITERROR;

    if( PyModule_AddObject( mod.get(), "DeclarativeFunction", newref( pyobject_cast( &DFunc_Type ) ) ) == -1 )
        INITERROR;
    if( PyModule_AddObject( mod.get(), "BoundDeclarativeMethod", newref( pyobject_cast( &BoundDMethod_Type ) ) ) == -1 )
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return mod.get();
#endif
}
