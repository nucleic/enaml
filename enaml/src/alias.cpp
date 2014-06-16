/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <sstream>
#include "pythonhelpersex.h"


using namespace PythonHelpers;


static PyObject* storage_str;


typedef struct {
    PyObject_HEAD
    PyObject* target;
    PyObject* chain;
    PyObject* key;
    bool canset;
} Alias;


static PyObject*
Alias_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* target;
    PyObject* chain;
    PyObject* key;
    if( !PyArg_ParseTuple( args, "OOO", &target, &chain, &key ) )
        return 0;
    if( !PyTuple_CheckExact( chain ) )
        return py_type_fail( "argument 2 must be a tuple" );
    PyObject* self = PyType_GenericNew( type, 0, 0 );
    if( !self )
        return 0;
    Alias* alias = reinterpret_cast<Alias*>( self );
    alias->target = newref( target );
    alias->chain = newref( chain );
    alias->key = newref( key );
    alias->canset = false;
    return self;
}


static void
Alias_dealloc( Alias* self )
{
    Py_CLEAR( self->target );
    Py_CLEAR( self->chain );
    Py_CLEAR( self->key );
    self->ob_type->tp_free( pyobject_cast( self ) );
}


static PyObject*
alias_load_fail( Alias* self )
{
    std::ostringstream ostr;
    PyObjectPtr pystr( PyObject_Str( self->target ) );
    if( !pystr )
        return 0;
    ostr << PyString_AS_STRING( pystr.get() );
    Py_ssize_t size = PyTuple_GET_SIZE( self->chain );
    for( Py_ssize_t i = 0; i < size; ++i )
    {
        pystr = PyObject_Str( PyTuple_GET_ITEM( self->chain, i ) );
        if( !pystr )
            return 0;
        ostr << "." << PyString_AS_STRING( pystr.get() );
    }
    PyErr_Format(
        PyExc_RuntimeError,
        "failed to load alias '%s'",
        ostr.str().c_str()
    );
    return 0;
}


static int
alias_load_set_fail( Alias* self )
{
    alias_load_fail( self );
    return -1;
}


static PyObject*
Alias__get__( Alias* self, PyObject* object, PyObject* type )
{
    if( !object )
        return newref( pyobject_cast( self ) );
    PyObjectPtr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return 0;
    PyObjectPtr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return 0;
    PyObjectPtr target( PyObject_GetItem( f_locals.get(), self->target ) );
    if( !target )
    {
        if( PyErr_ExceptionMatches( PyExc_KeyError ) )
            return alias_load_fail( self );
        return 0;
    }
    PyObject* name;
    Py_ssize_t size = PyTuple_GET_SIZE( self->chain );
    for( Py_ssize_t i = 0; i < size; ++i )
    {
        name = PyTuple_GET_ITEM( self->chain, i );
        target = PyObject_GetAttr( target.get(), name );
        if( !target )
            return 0;
    }
    return target.release();
}


static int
Alias__set__( Alias* self, PyObject* object, PyObject* value )
{
    if( !self->canset )
    {
        PyErr_Format(
            PyExc_AttributeError, "can't %s alias", value ? "set" : "delete"
        );
        return -1;
    }
    PyObjectPtr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return -1;
    PyObjectPtr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return -1;
    PyObjectPtr target( PyObject_GetItem( f_locals.get(), self->target ) );
    if( !target )
    {
        if( PyErr_ExceptionMatches( PyExc_KeyError ) )
            return alias_load_set_fail( self );
        return -1;
    }
    PyObject* name;
    Py_ssize_t last = PyTuple_GET_SIZE( self->chain ) - 1;
    for( Py_ssize_t i = 0; i < last; ++i )
    {
        name = PyTuple_GET_ITEM( self->chain, i );
        target = PyObject_GetAttr( target.get(), name );
        if( !target )
            return -1;
    }
    name = PyTuple_GET_ITEM( self->chain, last );
    return PyObject_SetAttr( target.get(), name, value );
}


static PyObject*
Alias_resolve( Alias* self, PyObject* object )
{
    PyObjectPtr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return 0;
    PyObjectPtr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return 0;
    PyObjectPtr target( PyObject_GetItem( f_locals.get(), self->target ) );
    if( !target )
    {
        if( PyErr_ExceptionMatches( PyExc_KeyError ) )
            return alias_load_fail( self );
        return 0;
    }
    PyObject* name;
    Py_ssize_t size = PyTuple_GET_SIZE( self->chain );
    if( self->canset )
        --size;
    for( Py_ssize_t i = 0; i < size; ++i )
    {
        name = PyTuple_GET_ITEM( self->chain, i );
        target = PyObject_GetAttr( target.get(), name );
        if( !target )
            return 0;
    }
    if( self->canset )
        name = PyTuple_GET_ITEM( self->chain, size );
    else
        name = Py_None;
    return PyTuple_Pack( 2, target.get(), name );
}


static PyObject*
Alias_get_target( Alias* self, void* ctxt )
{
    return newref( self->target );
}


static PyObject*
Alias_get_chain( Alias* self, void* ctxt )
{
    return newref( self->chain );
}


static PyObject*
Alias_get_key( Alias* self, void* ctxt )
{
    return newref( self->key );
}


static PyObject*
Alias_get_canset( Alias* self, void* ctxt )
{
    return newref( self->canset ? Py_True : Py_False );
}


static int
Alias_set_canset( Alias* self, PyObject* value, void* ctxt )
{
    if( !PyBool_Check( value ) )
    {
        py_expected_type_fail( value, "bool" );
        return -1;
    }
    self->canset = value == Py_True ? true : false;
    return 0;
}


static PyGetSetDef
Alias_getset[] = {
    { "target", ( getter )Alias_get_target, 0,
      "Get the target of the alias" },
    { "chain", ( getter )Alias_get_chain, 0,
      "Get the name chain for the alias." },
    { "key", ( getter )Alias_get_key, 0,
      "Get the scope key for the alias." },
    { "canset", ( getter )Alias_get_canset, ( setter )Alias_set_canset,
      "Get whether or not the alias is settable" },
    { 0 } // sentinel
};


static PyMethodDef
Alias_methods[] = {
    { "resolve", ( PyCFunction )Alias_resolve, METH_O,
      "Resolve the alias target object and attribute." },
    { 0 } // sentinel
};


PyTypeObject Alias_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "alias.Alias",                          /* tp_name */
    sizeof( Alias ),                        /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)Alias_dealloc,              /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                     /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)0,                        /* tp_traverse */
    (inquiry)0,                             /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)Alias_methods,     /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    Alias_getset,                           /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)Alias__get__,             /* tp_descr_get */
    (descrsetfunc)Alias__set__,             /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)Alias_new,                     /* tp_new */
    (freefunc)PyObject_Del,                 /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
alias_methods[] = {
    { 0 } // sentinel
};


PyMODINIT_FUNC
initalias( void )
{
    PyObject* mod = Py_InitModule( "alias", alias_methods );
    if( !mod )
        return;
    storage_str = PyString_FromString( "_d_storage" );
    if( !storage_str )
        return;
    if( PyType_Ready( &Alias_Type ) < 0 )
        return;
    PyModule_AddObject( mod, "Alias", newref( pyobject_cast( &Alias_Type ) ) );
}
