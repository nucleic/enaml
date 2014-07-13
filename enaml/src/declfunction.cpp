/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif

#include <iostream>
#include <sstream>
#include "pythonhelpersex.h"


using namespace PythonHelpers;


PyObject* DynamicScope;
PyObject* builtins_str;
PyObject* dstorage_str;


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
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
DFunc_repr( DFunc* self )
{
    std::ostringstream ostr;
    ostr << "<declarative function ";
    PyObjectPtr mod( PyObject_GetAttrString( self->im_func, "__module__" ) );
    if( mod && PyString_Check( mod.get() ) )
        ostr << PyString_AS_STRING( mod.get() ) << ".";
    PyObjectPtr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && PyString_Check( name.get() ) )
        ostr << PyString_AS_STRING( name.get() );
    ostr << ">";
    return PyString_FromString( ostr.str().c_str() );
}


static PyObject*
DFunc__get__( DFunc* self, PyObject* im_self, PyObject* type )
{
    if( !im_self )
        return newref( pyobject_cast( self ) );
    return BoundDMethod_New( self->im_func, im_self, self->im_key );
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


static PyGetSetDef
DFunc_getset[] = {
    { "__func__", ( getter )DFunc_get_func, 0,
      "Get the function invoked by this declarative function." },
    { "__key__", ( getter )DFunc_get_key, 0,
      "Get the scope key for this declarative function." },
    { 0 } // sentinel
};


PyTypeObject DFunc_Type = {
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    "funchelper.DeclarativeFunction",       /* tp_name */
    sizeof( DFunc ),                        /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)DFunc_dealloc,              /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)DFunc_repr,                   /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
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
        self->ob_type->tp_free( pyobject_cast( self ) );
}


static PyObject*
BoundDMethod_repr( BoundDMethod* self )
{
    std::ostringstream ostr;
    ostr << "<bound declarative method ";
    PyObjectPtr cls( PyObject_GetAttrString(
        pyobject_cast( self->im_self->ob_type ), "__name__" ) );
    if( cls && PyString_Check( cls.get() ) )
        ostr << PyString_AS_STRING( cls.get() ) << ".";
    PyObjectPtr name( PyObject_GetAttrString( self->im_func, "__name__" ) );
    if( name && PyString_Check( name.get() ) )
        ostr << PyString_AS_STRING( name.get() );
    PyObjectPtr obj( PyObject_Repr( self->im_self ) );
    if( obj && PyString_Check( obj.get() ) )
        ostr << " of " << PyString_AS_STRING( obj.get() );
    ostr << ">";
    return PyString_FromString( ostr.str().c_str() );
}


static PyObject*
BoundDMethod__call__( BoundDMethod* self, PyObject* args, PyObject* kwargs )
{
    std::cout << "called" << std::endl;
    Py_RETURN_NONE;
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
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    "funchelper.BoundDeclarativeMethod",    /* tp_name */
    sizeof( BoundDMethod ),                 /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)BoundDMethod_dealloc,       /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
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
