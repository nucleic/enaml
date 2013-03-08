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

// Type structure for CallableRef instances
typedef struct {
    PyObject_HEAD
    PyObject* objref;
} CallableRef;


static int
CallableRef_Check( PyObject* obj );


static PyObject*
CallableRef_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* obj;
    PyObject* cb = 0;
    static char* kwlist[] = { "method", "callback", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "O|O", kwlist, &obj, &cb ) )
        return 0;
    PyObjectPtr crefptr( PyType_GenericNew( type, args, kwargs ) );
    if( !crefptr )
        return 0;
    CallableRef* cref = reinterpret_cast<CallableRef*>( crefptr.get() );
    cref->objref = PyWeakref_NewRef( obj, cb );
    if( !cref->objref )
        return 0;
    return crefptr.release();
}


static void
CallableRef_clear( CallableRef* self )
{
    Py_CLEAR( self->objref );
}


static int
CallableRef_traverse( CallableRef* self, visitproc visit, void* arg )
{
    Py_VISIT( self->objref );
    return 0;
}


static void
CallableRef_dealloc( CallableRef* self )
{
    PyObject_GC_UnTrack( self );
    CallableRef_clear( self );
    self->ob_type->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
CallableRef_call( CallableRef* self, PyObject* args, PyObject* kwargs )
{
    PyWeakrefPtr objrefptr( self->objref, true );
    PyObjectPtr objptr( objrefptr.get_object() );
    if( objptr.is_None() )
        Py_RETURN_NONE;
    PyObjectPtr argsptr( args, true );
    PyObjectPtr kwargsptr( kwargs, true );
    return objptr( argsptr, kwargsptr ).release();
}


static PyObject*
CallableRef_richcompare( CallableRef* self, PyObject* other, int opid )
{
    if( opid == Py_EQ )
    {
        PyObjectPtr sref( self->objref, true );
        if( CallableRef_Check( other ) )
        {
            CallableRef* cref_other = reinterpret_cast<CallableRef*>( other );
            PyObjectPtr oref( cref_other->objref, true );
            if( sref.richcompare( oref, Py_EQ ) )
                Py_RETURN_TRUE;
            Py_RETURN_FALSE;
        }
        if( PyWeakref_CheckRef( other ) )
        {
            PyObjectPtr oref( other, true );
            if( sref.richcompare( oref, Py_EQ ) )
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
"which will dererence the underlying callable before calling it.\n\n"
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


PyTypeObject CallableRef_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "callableref.CallableRef",              /* tp_name */
    sizeof( CallableRef ),                  /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)CallableRef_dealloc,        /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)CallableRef_call,          /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC, /* tp_flags */
    CallableRef__doc__,                     /* Documentation string */
    (traverseproc)CallableRef_traverse,     /* tp_traverse */
    (inquiry)CallableRef_clear,             /* tp_clear */
    (richcmpfunc)CallableRef_richcompare,   /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)0,                 /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)CallableRef_new,               /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static int
CallableRef_Check( PyObject* obj )
{
    return PyObject_TypeCheck( obj, &CallableRef_Type );
}


static PyMethodDef
callableref_methods[] = {
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initcallableref( void )
{
    PyObject* mod = Py_InitModule( "callableref", callableref_methods );
    if( !mod )
        return;

    if( PyType_Ready( &CallableRef_Type ) )
        return;

    PyObjectPtr cr_type( reinterpret_cast<PyObject*>( &CallableRef_Type ), true );
    PyModule_AddObject( mod, "CallableRef", cr_type.release() );
}

} // extern "C"

