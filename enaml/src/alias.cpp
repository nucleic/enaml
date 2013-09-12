/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "pythonhelpersex.h"


using namespace PythonHelpers;


static PyObject* storage_str;


typedef struct {
    PyObject_HEAD
    PyObject* target;
    PyObject* attr;
    PyObject* key;
} Alias;


static PyObject*
Alias_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* target;
    PyObject* attr;
    PyObject* key;
    static char* kwlist[] = { "target", "attr", "key", 0 };
    if( !PyArg_ParseTupleAndKeywords(
        args, kwargs, "SSO:__new__", kwlist, &target, &attr, &key ) )
        return 0;
    PyObject* self = PyType_GenericNew( type, 0, 0 );
    if( !self )
        return 0;
    Alias* alias = reinterpret_cast<Alias*>( self );
    alias->target = newref( target );
    alias->attr = newref( attr );
    alias->key = newref( key );
    return self;
}


static void
Alias_dealloc( Alias* self )
{
    Py_CLEAR( self->target );
    Py_CLEAR( self->attr );
    Py_CLEAR( self->key );
    self->ob_type->tp_free( pyobject_cast( self ) );
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
        return 0;
    if( PyString_GET_SIZE( self->attr ) == 0 )
        return target.release();
    return PyObject_GetAttr( target.get(), self->attr );
}


static int
Alias__set__( Alias* self, PyObject* object, PyObject* value )
{
    if( PyString_GET_SIZE( self->attr ) == 0 )
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
        return -1;
    return PyObject_SetAttr( target.get(), self->attr, value );
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
        return 0;
    return PyTuple_Pack( 2, target.get(), self->attr );
}


static PyObject*
Alias_get_target( Alias* self, void* ctxt )
{
    return newref( self->target );
}


static PyObject*
Alias_get_key( Alias* self, void* ctxt )
{
    return newref( self->key );
}


static PyObject*
Alias_get_attr( Alias* self, void* ctxt )
{
    return newref( self->attr );
}


static PyGetSetDef
Alias_getset[] = {
    { "target", ( getter )Alias_get_target, 0,
      "Get the name of the target for the alias." },
    { "attr", ( getter )Alias_get_attr, 0,
      "Get the target attribute for the alias." },
    { "key", ( getter )Alias_get_key, 0,
      "Get the scope key for the alias." },
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
