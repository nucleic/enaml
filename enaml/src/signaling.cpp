/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include <vector>
#include "pythonhelpers.h"
#include "py23compat.h"


#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif


using namespace PythonHelpers;

extern "C" {

typedef struct {
    PyObject_HEAD
} Signal;


typedef struct {
    PyObject_HEAD
    PyObject* owner;
    PyObject* objref;
} _Disconnector;


typedef struct {
    PyObject_HEAD
    PyObject* owner;
    PyObject* objref;
} BoundSignal;


#define FREELIST_MAX 128
static int numfree = 0;
static BoundSignal* freelist[ FREELIST_MAX ];


static PyObject* SignalsKey;
static PyObject* WeakMethod;
static PyObject* CallableRef;


static PyObject*
_Disconnector_New( PyObject* owner, PyObject* objref );


static PyObject*
_BoundSignal_New( PyObject* owner, PyObject* objref );


static int
BoundSignal_Check( PyObject* obj );


/*-----------------------------------------------------------------------------
| Signal
|----------------------------------------------------------------------------*/
static PyObject*
Signal_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyDictPtr kwargsptr( kwargs, true );
    if( ( kwargsptr ) && ( kwargsptr.size() > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "Signal() takes no keyword arguments (";
        ostr << kwargsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyTuplePtr argsptr( args, true );
    if( argsptr.size() > 0 )
    {
        std::ostringstream ostr;
        ostr << "Signal() takes no arguments (";
        ostr << argsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyObjectPtr self( PyType_GenericNew( type, args, kwargs ) );
    if( !self )
        return 0;

    return self.release();
}


static void
Signal_clear( Signal* self )
{
    // nothing to clear
}


static int
Signal_traverse( Signal* self, visitproc visit, void* arg )
{
    // nothing to traverse
    return 0;
}


static void
Signal_dealloc( Signal* self )
{
    PyObject_GC_UnTrack( self );
    Signal_clear( self );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
Signal__get__( PyObject* self, PyObject* obj, PyObject* type )
{
    PyObjectPtr selfptr( self, true );
    if( !obj )
        return selfptr.release();
    PyObjectPtr objref( PyWeakref_NewRef( obj, 0 ) );
    if( !objref )
        return 0;
    PyObjectPtr boundsig( _BoundSignal_New( self, objref.get() ) );
    if( !boundsig )
        return 0;
    return boundsig.release();
}


static int
Signal__set__( Signal* self, PyObject* obj, PyObject* value )
{
    if( value )
    {
        py_attr_fail( "can't set read only Signal" );
        return -1;
    }

    PyObjectPtr objptr( obj, true );
    PyDictPtr dict;
    if( !objptr.load_dict( dict ) )
    {
        py_no_attr_fail( objptr.get(), "__dict__" );
        return -1;
    }
    if( !dict )
        return 0;

    PyObjectPtr key( SignalsKey, true );
    PyDictPtr signals( dict.get_item( key ) );
    if( !signals )
        return 0;
    if( !signals.check_exact() )
    {
        py_expected_type_fail( signals.get(), "dict" );
        return -1;
    }

    PyObjectPtr owner( reinterpret_cast<PyObject*>( self ), true );
    if( signals.get_item( owner ) )
    {
        if( !signals.del_item( owner ) )
            return -1;
        if( signals.size() == 0 )
        {
            if( !dict.del_item( key ) )
                return -1;
        }
    }

    return 0;
}


static PyObject*
Signal_disconnect_all( PyObject* ignored, PyObject* obj )
{
    PyObjectPtr objptr( obj, true );
    PyDictPtr dict;
    if( !objptr.load_dict( dict ) )
        return py_no_attr_fail( obj, "__dict__" );
    if( !dict )
        return 0;
    PyObjectPtr key( SignalsKey, true );
    if( dict.get_item( key ) )
    {
        if( !dict.del_item( key ) )
            return 0;
    }
    Py_RETURN_NONE;
}


static PyMethodDef
Signal_methods[] = {
    { "disconnect_all", ( PyCFunction )Signal_disconnect_all, METH_O | METH_STATIC,
      "Disconnect all slots connected to all signals on an object." },
    { 0 } // sentinel
};


PyDoc_STRVAR(Signal__doc__,
"Signal()\n\n"
"A descriptor which provides notification functionality similar\n"
"to Qt signals.\n\n"
"A Signal is used by creating an instance in the body of a class\n"
"definition. Slots (callables) are connected to the signal through\n"
"the `connect` and `disconnect` methods. A signal can be emitted by\n"
"calling the `emit` method passing arbitrary positional and keyword\n"
"arguments.\n\n"
"If a bound method is connected to a signal, then that slot will be\n"
"automatically disconnected when the underlying object instance is\n"
"garbage collected.\n\n");


PyTypeObject Signal_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "signaling.Signal",                     /* tp_name */
    sizeof( Signal ),                       /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)Signal_dealloc,             /* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC, /* tp_flags */
    Signal__doc__,                          /* Documentation string */
    (traverseproc)Signal_traverse,          /* tp_traverse */
    (inquiry)Signal_clear,                  /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)Signal_methods,    /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)Signal__get__,            /* tp_descr_get */
    (descrsetfunc)Signal__set__,            /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)Signal_new,                    /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


/*-----------------------------------------------------------------------------
| _Disconnector
|----------------------------------------------------------------------------*/
static PyObject*
_Disconnector_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* owner;
    PyObject* objref;
    static char* kwlist[] = { "signal", "objref", 0 };
    // The C++ code for BoundSignal calls _Diconnector_New directly.
    // This new method will only be called by Python code, which should
    // not normally be creating _Disconnector instances. So, using the
    // slow but convenient arg parsing is fine here.
    int ok = PyArg_ParseTupleAndKeywords(
        args, kwargs, "O!O!", kwlist, &Signal_Type, &owner,
        &_PyWeakref_RefType, &objref
    );
    if( !ok )
        return 0;
    return _Disconnector_New( owner, objref );
}


static void
_Disconnector_clear( _Disconnector* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->objref );
}


static int
_Disconnector_traverse( _Disconnector* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->objref );
    return 0;
}


static void
_Disconnector_dealloc( _Disconnector* self )
{
    PyObject_GC_UnTrack( self );
    _Disconnector_clear( self );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
_Disconnector_call( _Disconnector* self, PyObject* args, PyObject* kwargs )
{
    PyDictPtr kwargsptr( kwargs, true );
    if( ( kwargsptr ) && ( kwargsptr.size() > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "_Disconnector.__call__() takes no keyword arguments (";
        ostr << kwargsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyTuplePtr argsptr( args, true );
    if( argsptr.size() != 1 )
    {
        std::ostringstream ostr;
        ostr << "_Disconnector.__call__() takes 1 argument (";
        ostr << argsptr.size() << " given)";
        return py_type_fail( ostr.str().c_str() );
    }

    PyWeakrefPtr objref( self->objref, true );
    PyObjectPtr obj( objref.get_object() );
    if( obj.is_None() )
        Py_RETURN_NONE;

    PyDictPtr dict;
    if( !obj.load_dict( dict ) )
        return py_no_attr_fail( obj.get(), "__dict__" );
    if( !dict )
        Py_RETURN_NONE;

    PyObjectPtr key( SignalsKey, true );
    PyDictPtr signals( dict.get_item( key ) );
    if( !signals )
        Py_RETURN_NONE;
    if( !signals.check_exact() )
        return py_expected_type_fail( signals.get(), "dict" );

    PyObjectPtr owner( self->owner, true );
    PyListPtr slots( signals.get_item( owner ) );
    if( !slots )
        Py_RETURN_NONE;
    if( !slots.check_exact() )
        return py_expected_type_fail( slots.get(), "list" );

    PyObjectPtr slot( argsptr.get_item( 0 ) );
    Py_ssize_t index = slots.index( slot );
    if( index != -1 )
    {
        if( !slots.del_item( index ) )
            return 0;
        // A _Disconnector is the first item in the list and is created
        // on demand. The list is deleted when that is the only item left.
        if( slots.size() == 1 )
        {
            if( !signals.del_item( owner ) )
                return 0;
            if( signals.size() == 0 )
            {
                if( !dict.del_item( key ) )
                    return 0;
            }
        }
    }

    Py_RETURN_NONE;
}


PyDoc_STRVAR(_Disconnector__doc__,
"_Disconnector(signal, objref)\n\n"
"An object which disconnects a slot from a signal when the slot\n"
"is garbage collected.\n\n"
"This class is a private implementation detail of signaling and is\n"
"not meant for public consumption.\n\n");


PyTypeObject _Disconnector_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "signaling._Disconnector",              /* tp_name */
    sizeof( _Disconnector ),                /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)_Disconnector_dealloc,      /* tp_dealloc */
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
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)_Disconnector_call,        /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC, /* tp_flags */
    _Disconnector__doc__,                   /* Documentation string */
    (traverseproc)_Disconnector_traverse,   /* tp_traverse */
    (inquiry)_Disconnector_clear,           /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
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
    (newfunc)_Disconnector_new,             /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyObject*
_Disconnector_New( PyObject* owner, PyObject* objref )
{
    PyObjectPtr ownerptr( owner, true );
    PyObjectPtr objrefptr( objref, true );
    PyObjectPtr self( PyType_GenericAlloc( &_Disconnector_Type, 0 ) );
    if( !self )
        return 0;
    _Disconnector* disc = reinterpret_cast<_Disconnector*>( self.get() );
    disc->owner = ownerptr.release();
    disc->objref = objrefptr.release();
    return self.release();
}


/*-----------------------------------------------------------------------------
| BoundSignal
|----------------------------------------------------------------------------*/
static PyObject*
BoundSignal_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* owner;
    PyObject* objref;
    static char* kwlist[] = { "signal", "objref", 0 };
    // The C++ code for Signal calls _BoundSignal_New directly. This
    // new method will only be called by Python code, which should not
    // normally be creating BoundSignal instances. So, using the slow
    // but convenient arg parsing is fine here.
    int ok = PyArg_ParseTupleAndKeywords(
        args, kwargs, "O!O!", kwlist, &Signal_Type, &owner,
        &_PyWeakref_RefType, &objref
    );
    if( !ok )
        return 0;
    return _BoundSignal_New( owner, objref );
}


static void
BoundSignal_clear( BoundSignal* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->objref );
}


static int
BoundSignal_traverse( BoundSignal* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->objref );
    return 0;
}


static void
BoundSignal_dealloc( BoundSignal* self )
{
    PyObject_GC_UnTrack( self );
    BoundSignal_clear( self );
    if( numfree < FREELIST_MAX )
        freelist[ numfree++ ] = self;
    else
        Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
BoundSignal_richcompare( BoundSignal* self, PyObject* other, int opid )
{
    if( opid == Py_EQ )
    {
        if( BoundSignal_Check( other ) )
        {
            BoundSignal* other_sig = reinterpret_cast<BoundSignal*>( other );
            if( self->owner == other_sig->owner )
            {
                PyObjectPtr sref( self->objref, true );
                PyObjectPtr oref( other_sig->objref, true );
                if( sref.richcompare( oref, Py_EQ ) )
                    Py_RETURN_TRUE;
            }
        }
        Py_RETURN_FALSE;
    }
    Py_RETURN_NOTIMPLEMENTED;
}


static PyObject*
BoundSignal_emit( BoundSignal* self, PyObject* args, PyObject* kwargs )
{
    PyWeakrefPtr objref( self->objref, true );
    PyObjectPtr obj( objref.get_object() );
    if( obj.is_None() )
        Py_RETURN_NONE;

    PyDictPtr dict;
    if( !obj.load_dict( dict ) )
        return py_no_attr_fail( obj.get(), "__dict__" );
    if( !dict )
        Py_RETURN_NONE;

    PyObjectPtr key( SignalsKey, true );
    PyDictPtr signals( dict.get_item( key ) );
    if( !signals )
        Py_RETURN_NONE;
    if( !signals.check_exact() )
        return py_expected_type_fail( signals.get(), "dict" );

    PyObjectPtr owner( self->owner, true );
    PyListPtr slots( signals.get_item( owner ) );
    if( !slots )
        Py_RETURN_NONE;
    if( !slots.check_exact() )
        return py_expected_type_fail( slots.get(), "list" );

    Py_ssize_t size = slots.size();
    if( size <= 1 ) // First item is a _Disconnector
        Py_RETURN_NONE;

    // Copy the list into a tuple before calling the slots. The act of
    // calling a slot may trigger connect/disconnect which will modify
    // the list. Copying into a tuple is faster than copying to a list
    // or an std::vector since Python maintains an internal freelist of
    // small tuples (size < 20) as an optimization to avoid frequent
    // heap allocations.
    PyTuplePtr cslots( PyTuple_New( size - 1 ) );
    if( !cslots )
        return 0;
    for( Py_ssize_t idx = 1; idx < size; idx++ )
    {
        PyObjectPtr slot( slots.get_item( idx ) );
        cslots.set_item( idx - 1, slot );
    }

    size--;
    PyTuplePtr argsptr( args, true );
    PyDictPtr kwargsptr( kwargs, true );
    for( Py_ssize_t idx = 0; idx < size; idx++ )
    {
        PyObjectPtr slot( cslots.get_item( idx ) );
        if( !slot( argsptr, kwargsptr ) )
            return 0;
    }

    Py_RETURN_NONE;
}


static PyObject*
BoundSignal_call( BoundSignal* self, PyObject* args, PyObject* kwargs )
{
    return BoundSignal_emit( self, args, kwargs );
}


static PyObject*
BoundSignal_connect( BoundSignal* self, PyObject* slot )
{
    PyWeakrefPtr objref( self->objref, true );
    PyObjectPtr obj( objref.get_object() );
    if( obj.is_None() )
        Py_RETURN_NONE;

    PyDictPtr dict;
    if( !obj.load_dict( dict, true ) )
        return py_no_attr_fail( obj.get(), "__dict__" );
    if( !dict )
        return 0;

    PyObjectPtr key( SignalsKey, true );
    PyDictPtr signals( dict.get_item( key ) );
    if( signals )
    {
        if( !signals.check_exact() )
            return py_expected_type_fail( signals.get(), "dict" );
    }
    else
    {
        signals = PyDict_New();
        if( !signals )
            return 0;
        if( !dict.set_item( key, signals ) )
            return 0;
    }

    PyObjectPtr owner( self->owner, true );
    PyListPtr slots( signals.get_item( owner ) );
    if( slots )
    {
        if( !slots.check_exact() )
            return py_expected_type_fail( slots.get(), "list" );
    }
    else
    {
        slots = PyList_New( 0 );
        if( !slots )
            return 0;
        if( !signals.set_item( owner, slots ) )
            return 0;
    }

    if( slots.size() == 0 )
    {
        PyObjectPtr disc( _Disconnector_New( owner.get(), objref.get() ) );
        if( !disc )
            return 0;
        if( !slots.append( disc ) )
            return 0;
    }

    PyObjectPtr slotptr( slot, true );
    if( PyMethod_Check( slot ) && PyMethod_GET_SELF( slot ) )
    {
        PyTuplePtr args( PyTuple_New( 1 ) );
        if( !args )
            return 0;
        args.set_item( 0, slotptr );
        PyObjectPtr wm_cls( WeakMethod, true );
        PyObjectPtr wm( wm_cls( args ) );
        if( !wm )
            return 0;
        args = PyTuple_New( 2 );
        if( !args )
            return 0;
        PyObjectPtr disc( slots.get_item( 0 ) );
        args.set_item( 0, wm );
        args.set_item( 1, disc );
        PyObjectPtr cr_cls( CallableRef, true );
        slotptr = cr_cls( args );
        if( !slotptr )
            return 0;
    }

    if( !slots.append( slotptr ) )
        return 0;

    Py_RETURN_NONE;
}


static PyObject*
BoundSignal_disconnect( BoundSignal* self, PyObject* slot )
{
    PyObjectPtr slotptr( slot, true );
    PyTuplePtr args( PyTuple_New( 1 ) );
    if( !args )
        return 0;
    if( PyMethod_Check( slot ) && PyMethod_GET_SELF( slot ) )
    {
        args.set_item( 0, slotptr );
        PyObjectPtr wm_cls( WeakMethod, true );
        PyObjectPtr wm( wm_cls( args ) );
        if( !wm )
            return 0;
        args.set_item( 0, wm );
        PyObjectPtr cr_cls( CallableRef, true );
        slotptr = cr_cls( args );
        if( !slotptr )
            return 0;
    }
    PyObjectPtr disc( _Disconnector_New( self->owner, self->objref ) );
    if( !disc )
        return 0;
    args.set_item( 0, slotptr );
    return disc( args ).release();
}


static PyMethodDef
BoundSignal_methods[] = {
    { "emit", ( PyCFunction )BoundSignal_emit, METH_KEYWORDS,
      "Emit the signal with the given arguments and keywords." },
    { "connect", ( PyCFunction )BoundSignal_connect, METH_O,
      "Connect the given slot to the signal" },
    { "disconnect", ( PyCFunction )BoundSignal_disconnect, METH_O,
      "Disconnect the given slot from the signal" },
    { 0 } // sentinel
};


PyDoc_STRVAR(BoundSignal__doc__,
"BoundSignal(signal, objref)\n\n"
"A bound Signal object.\n\n"
"Instances of this class are created on the fly by a Signal. This\n"
"class performs the actual work for connecting, disconnecting, and\n"
"emitting signals.\n\n");


PyTypeObject BoundSignal_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "signaling.BoundSignal",                /* tp_name */
    sizeof( BoundSignal ),                  /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)BoundSignal_dealloc,        /* tp_dealloc */
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
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)BoundSignal_call,          /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    BoundSignal__doc__,                     /* Documentation string */
    (traverseproc)BoundSignal_traverse,     /* tp_traverse */
    (inquiry)BoundSignal_clear,             /* tp_clear */
    (richcmpfunc)BoundSignal_richcompare,   /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)BoundSignal_methods, /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)BoundSignal_new,               /* tp_new */
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
BoundSignal_Check( PyObject* obj )
{
    return PyObject_TypeCheck( obj, &BoundSignal_Type );
}


static PyObject*
_BoundSignal_New( PyObject* owner, PyObject* objref )
{
    PyObjectPtr ownerptr( owner, true );
    PyObjectPtr objrefptr( objref, true );
    PyObjectPtr bsigptr;
    if( numfree > 0 )
    {
        PyObject* o = reinterpret_cast<PyObject*>( freelist[ --numfree ] );
        _Py_NewReference( o );
        bsigptr = o;
    }
    else
    {
        bsigptr = PyType_GenericAlloc( &BoundSignal_Type, 0 );
        if( !bsigptr )
            return 0;
    }
    BoundSignal* bsig = reinterpret_cast<BoundSignal*>( bsigptr.get() );
    bsig->owner = ownerptr.release();
    bsig->objref = objrefptr.release();
    return bsigptr.release();
}


/*-----------------------------------------------------------------------------
| Signaling Module
|----------------------------------------------------------------------------*/
struct module_state {
    PyObject *error;
};


static PyMethodDef
signaling_methods[] = {
    { 0 } // Sentinel
};

#if PY_MAJOR_VERSION >= 3

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int signaling_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int signaling_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "signaling",
        NULL,
        sizeof(struct module_state),
        signaling_methods,
        NULL,
        signaling_traverse,
        signaling_clear,
        NULL
};

#else

#define GETSTATE(m) (&_state)
static struct module_state _state;

#endif

MOD_INIT_FUNC(signaling)
{
#if PY_MAJOR_VERSION >= 3
    PyObjectPtr mod( PyModule_Create(&moduledef), true );
#else
    PyObjectPtr mod( Py_InitModule( "signaling", signaling_methods ), true );
#endif
    if( !mod )
        INITERROR;
    PyObject* mod_dict = PyModule_GetDict( mod.get() );

    PyObjectPtr wm_mod( PyImport_ImportModuleLevel( "weakmethod", mod_dict, 0, 0 , 1) );
    if( !wm_mod)
        INITERROR;
    PyObjectPtr wm_cls( wm_mod.get_attr( "WeakMethod" ) );
    if( !wm_cls )
        INITERROR;

    PyObjectPtr cr_mod( PyImport_ImportModuleLevel( "callableref", mod_dict, 0, 0, 1 ) );
    if( !cr_mod )
        INITERROR;
    PyObjectPtr cr_cls( cr_mod.get_attr( "CallableRef" ) );
    if( !cr_cls )
        INITERROR;

    PyObjectPtr key( Py23Str_FromString( "_[signals]" ) );
    if( !key )
        INITERROR;

    SignalsKey = key.release();
    WeakMethod = wm_cls.release();
    CallableRef = cr_cls.release();

    if( PyType_Ready( &Signal_Type ) )
        INITERROR;
    if( PyType_Ready( &_Disconnector_Type ) )
        INITERROR;
    if( PyType_Ready( &BoundSignal_Type ) )
        INITERROR;

    PyObjectPtr sig_type( reinterpret_cast<PyObject*>( &Signal_Type ), true );
    if( PyModule_AddObject( mod.get(), "Signal", sig_type.release() ) == -1 )
        INITERROR;
    PyObjectPtr disc_type( reinterpret_cast<PyObject*>( &_Disconnector_Type ), true );
    if( PyModule_AddObject( mod.get(), "_Disconnector", disc_type.release() ) == -1 )
        INITERROR;
    PyObjectPtr bsig_type( reinterpret_cast<PyObject*>( &BoundSignal_Type ), true );
    if( PyModule_AddObject( mod.get(), "BoundSignal", bsig_type.release() ) == -1 )
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return mod.get();
#endif
}

} // extern "C"

