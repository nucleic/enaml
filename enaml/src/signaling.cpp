/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
#include <iostream>
#include <sstream>
#include <vector>
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
struct Signal
{
	PyObject_HEAD

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


// POD struct - all member fields are considered private
struct _Disconnector
{
	PyObject_HEAD
    PyObject* owner;
    PyObject* objref;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

    static PyObject* New( PyObject* owner, PyObject* objref );

};


// POD struct - all member fields are considered private
struct BoundSignal
{
	PyObject_HEAD
    PyObject* owner;
    PyObject* objref;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

    static PyObject* New( PyObject* owner, PyObject* objref );

    static int TypeCheck( PyObject* obj );

};

namespace
{

#define FREELIST_MAX 128
static int numfree = 0;
static BoundSignal* freelist[ FREELIST_MAX ];


static PyObject* SignalsKey;
static PyObject* WeakMethod;
static PyObject* CallableRef;


inline bool load_obj_dict( cppy::ptr& objptr, cppy::ptr& out, bool forcecreate=false )
{
    PyObject** dict = _PyObject_GetDictPtr( objptr.get() );
    if( !dict )
        return false;
    if( forcecreate && !*dict )
        *dict = PyDict_New();
    out = cppy::ptr( cppy::incref( *dict ) );
    return true;
}


/*-----------------------------------------------------------------------------
| Signal
|----------------------------------------------------------------------------*/
PyObject*
Signal_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    cppy::ptr kwargsptr( kwargs, true );
    if( ( kwargsptr ) && ( PyDict_Size( kwargsptr.get() ) > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "Signal() takes no keyword arguments (";
        ostr << PyDict_Size( kwargsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr argsptr( args, true );
    if( PyTuple_Size( argsptr.get() ) > 0 )
    {
        std::ostringstream ostr;
        ostr << "Signal() takes no arguments (";
        ostr << PyTuple_Size( argsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr self( PyType_GenericNew( type, args, kwargs ) );
    if( !self )
        return 0;

    return self.release();
}


void
Signal_clear( Signal* self )
{
    // nothing to clear
}


int
Signal_traverse( Signal* self, visitproc visit, void* arg )
{
    // nothing to traverse
    return 0;
}


void
Signal_dealloc( Signal* self )
{
    PyObject_GC_UnTrack( self );
    Signal_clear( self );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


PyObject*
Signal__get__( PyObject* self, PyObject* obj, PyObject* type )
{
    cppy::ptr selfptr( cppy::incref( self ) );
    if( !obj )
        return selfptr.release();
    cppy::ptr objref( PyWeakref_NewRef( obj, 0 ) );
    if( !objref )
        return 0;
    cppy::ptr boundsig( BoundSignal::New( self, objref.get() ) );
    if( !boundsig )
        return 0;
    return boundsig.release();
}


int
Signal__set__( Signal* self, PyObject* obj, PyObject* value )
{
    if( value )
    {
        cppy::attribute_error( "can't set read only Signal" );
        return -1;
    }

    cppy::ptr objptr( cppy::incref( obj ) );
    cppy::ptr dict;
    if( !load_obj_dict( objptr, dict ) )
    {
        cppy::attribute_error( objptr.get(), "__dict__" );
        return -1;
    }
    if( !dict )
        return 0;

    cppy::ptr key( cppy::incref( SignalsKey ) );
    cppy::ptr signals( dict.getitem( key ) );
    if( !signals )
        return 0;
    if( !PyDict_CheckExact( signals.get() ) )
    {
        cppy::type_error( signals.get(), "dict" );
        return -1;
    }

    cppy::ptr owner( cppy::incref( pyobject_cast( self ) ) );
    if( signals.getitem( owner ) )
    {
        if( !signals.delitem( owner ) )
            return -1;
        if( PyDict_Size( signals.get() ) == 0 )
        {
            if( !dict.delitem( key ) )
                return -1;
        }
    }

    return 0;
}


PyObject*
Signal_disconnect_all( PyObject* ignored, PyObject* obj )
{
    cppy::ptr objptr( cppy::incref( obj ) );
    cppy::ptr dict;
    if( !load_obj_dict( objptr, dict ) )
        return cppy::attribute_error( obj, "__dict__" );
    if( !dict )
        return 0;
    cppy::ptr key( cppy::incref( SignalsKey ) );
    if( dict.getitem( key ) )
    {
        if( !dict.delitem( key ) )
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


static PyType_Slot Signal_Type_slots[] = {
    { Py_tp_dealloc, void_cast( Signal_dealloc ) },       /* tp_dealloc */
    { Py_tp_traverse, void_cast( Signal_traverse ) },     /* tp_dealloc */
    { Py_tp_clear, void_cast( Signal_clear ) },           /* tp_dealloc */
    { Py_tp_doc, cast_py_tp_doc( Signal__doc__ ) },       /* tp_doc */
    { Py_tp_methods, void_cast( Signal_methods ) },       /* tp_methods */
    { Py_tp_descr_get, void_cast( Signal__get__ ) },      /* tp_descr_get */
    { Py_tp_descr_set, void_cast( Signal__set__ ) },      /* tp_descr_set */
    { Py_tp_new, void_cast( Signal_new ) },               /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },    /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* Signal::TypeObject = NULL;


PyType_Spec Signal::TypeObject_Spec = {
	"enaml.signaling.Signal",            /* tp_name */
	sizeof( Signal ),                     /* tp_basicsize */
	0,                                   /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_BASETYPE|
    Py_TPFLAGS_HAVE_GC,                  /* tp_flags */
    Signal_Type_slots                     /* slots */
};


bool Signal::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


/*-----------------------------------------------------------------------------
| _Disconnector
|----------------------------------------------------------------------------*/
namespace
{

PyObject*
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
        args, kwargs, "O!O!", kwlist, Signal::TypeObject, &owner,
        &_PyWeakref_RefType, &objref
    );
    if( !ok )
        return 0;
    return _Disconnector::New( owner, objref );
}


void
_Disconnector_clear( _Disconnector* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->objref );
}


int
_Disconnector_traverse( _Disconnector* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->objref );
    return 0;
}


void
_Disconnector_dealloc( _Disconnector* self )
{
    PyObject_GC_UnTrack( self );
    _Disconnector_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
_Disconnector_call( _Disconnector* self, PyObject* args, PyObject* kwargs )
{
    cppy::ptr kwargsptr( kwargs, true );
    if( ( kwargsptr ) && ( PyDict_Size( kwargsptr.get() ) > 0 ) )
    {
        std::ostringstream ostr;
        ostr << "_Disconnector.__call__() takes no keyword arguments (";
        ostr << PyDict_Size( kwargsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr argsptr( args, true );
    if( PyTuple_Size( argsptr.get() ) != 1 )
    {
        std::ostringstream ostr;
        ostr << "_Disconnector.__call__() takes 1 argument (";
        ostr << PyTuple_Size( argsptr.get() ) << " given)";
        return cppy::type_error( ostr.str().c_str() );
    }

    cppy::ptr objref( cppy::incref( self->objref ) );
    cppy::ptr obj( cppy::incref( PyWeakref_GET_OBJECT( objref.get() ) ) );
    if( obj.is_none() )
        Py_RETURN_NONE;

    cppy::ptr dict;
    if( !load_obj_dict( obj, dict ) )
        return cppy::attribute_error( obj.get(), "__dict__" );
    if( !dict )
        Py_RETURN_NONE;

    cppy::ptr key( cppy::incref( SignalsKey ) );
    cppy::ptr signals( dict.getitem( key ) );
    if( !signals )
        Py_RETURN_NONE;
    if( !PyDict_CheckExact( signals.get() ) )
        return cppy::type_error( signals.get(), "dict" );

    cppy::ptr owner( cppy::incref( self->owner ) );
    cppy::ptr slots( signals.getitem( owner ) );
    if( !slots )
        Py_RETURN_NONE;
    if( !PyDict_CheckExact( slots.get() ) )
        return cppy::type_error( slots.get(), "list" );

    cppy::ptr slot( cppy::incref( PyTuple_GET_ITEM( argsptr.get(), 0 ) ) );
    Py_ssize_t index = -1;
    Py_ssize_t maxidx = PyList_Size( slots.get() );
    for( Py_ssize_t idx = 0; idx < maxidx; idx++ )
    {
        PyObject* other = PyList_GET_ITEM( slots.get(), idx );
        if( slot.richcmp( other, Py_EQ ) )
        {
            index = idx;
            break;
        }
    }

    if( index != -1 )
    {
        if( PySequence_DelItem( slots.get(), index ) != 0 )
            return 0;
        // A _Disconnector is the first item in the list and is created
        // on demand. The list is deleted when that is the only item left.
        if( PyList_Size( slots.get() ) == 1 )
        {
            if( !signals.delitem( owner ) )
                return 0;
            if( PyDict_Size( signals.get() ) == 0 )
            {
                if( !dict.delitem( key ) )
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


static PyType_Slot _Disconnector_Type_slots[] = {
    { Py_tp_dealloc, void_cast( _Disconnector_dealloc ) },       /* tp_dealloc */
    { Py_tp_traverse, void_cast( _Disconnector_traverse ) },     /* tp_traverse */
    { Py_tp_clear, void_cast( _Disconnector_clear ) },           /* tp_clear */
    { Py_tp_doc, cast_py_tp_doc( _Disconnector__doc__ ) },       /* tp_doc */
    { Py_tp_call, void_cast( _Disconnector_call ) },             /* tp_call */
    { Py_tp_new, void_cast( _Disconnector_new ) },               /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },           /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* _Disconnector::TypeObject = NULL;


PyType_Spec _Disconnector::TypeObject_Spec = {
	"enaml.signaling._Disconnector",            /* tp_name */
	sizeof( _Disconnector ),                     /* tp_basicsize */
	0,                                          /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_HAVE_GC,                         /* tp_flags */
    _Disconnector_Type_slots                           /* slots */
};


bool _Disconnector::Ready()
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
_Disconnector::New( PyObject* owner, PyObject* objref )
{
    cppy::ptr ownerptr( cppy::incref( owner ) );
    cppy::ptr objrefptr( cppy::incref( objref ) );
    cppy::ptr self( PyType_GenericAlloc( _Disconnector::TypeObject, 0 ) );
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
namespace
{


PyObject*
BoundSignal_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* owner;
    PyObject* objref;
    static char* kwlist[] = { "signal", "objref", 0 };
    // The C++ code for Signal calls BoundSignal::New directly. This
    // new method will only be called by Python code, which should not
    // normally be creating BoundSignal instances. So, using the slow
    // but convenient arg parsing is fine here.
    int ok = PyArg_ParseTupleAndKeywords(
        args, kwargs, "O!O!", kwlist, Signal::TypeObject, &owner,
        &_PyWeakref_RefType, &objref
    );
    if( !ok )
        return 0;
    return BoundSignal::New( owner, objref );
}


void
BoundSignal_clear( BoundSignal* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->objref );
}


int
BoundSignal_traverse( BoundSignal* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->objref );
    return 0;
}


void
BoundSignal_dealloc( BoundSignal* self )
{
    PyObject_GC_UnTrack( self );
    BoundSignal_clear( self );
    if( numfree < FREELIST_MAX )
        freelist[ numfree++ ] = self;
    else
        Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
BoundSignal_richcompare( BoundSignal* self, PyObject* other, int opid )
{
    if( opid == Py_EQ )
    {
        if( BoundSignal::TypeCheck( other ) )
        {
            BoundSignal* other_sig = reinterpret_cast<BoundSignal*>( other );
            if( self->owner == other_sig->owner )
            {
                cppy::ptr sref( cppy::incref( self->objref ) );
                cppy::ptr oref( cppy::incref( other_sig->objref ) );
                if( sref.richcmp( oref, Py_EQ ) )
                    Py_RETURN_TRUE;
            }
        }
        Py_RETURN_FALSE;
    }
    Py_RETURN_NOTIMPLEMENTED;
}


PyObject*
BoundSignal_emit( BoundSignal* self, PyObject* args, PyObject* kwargs )
{
    cppy::ptr objref( cppy::incref( self->objref ) );
    cppy::ptr obj( cppy::incref( PyWeakref_GET_OBJECT( objref.get() ) ) );
    if( obj.is_none() )
        Py_RETURN_NONE;
    cppy::ptr dict;
    if( !load_obj_dict( obj, dict ) )
        return cppy::attribute_error( obj.get(), "__dict__" );
    if( !dict )
        Py_RETURN_NONE;

    cppy::ptr key( cppy::incref( SignalsKey ) );
    cppy::ptr signals( dict.getitem( key ) );
    if( !signals )
        Py_RETURN_NONE;
    if( !PyDict_CheckExact( signals.get() ) )
        return cppy::type_error( signals.get(), "dict" );

    cppy::ptr owner( cppy::incref( self->owner ) );
    cppy::ptr slots( signals.getitem( owner ) );
    if( !slots )
        Py_RETURN_NONE;
    if( !PyList_CheckExact( slots.get() ) )
        return cppy::type_error( slots.get(), "list" );

    Py_ssize_t size = PyList_Size( slots.get() );
    if( size <= 1 ) // First item is a _Disconnector
        Py_RETURN_NONE;

    // Copy the list into a tuple before calling the slots. The act of
    // calling a slot may trigger connect/disconnect which will modify
    // the list. Copying into a tuple is faster than copying to a list
    // or an std::vector since Python maintains an internal freelist of
    // small tuples (size < 20) as an optimization to avoid frequent
    // heap allocations.
    cppy::ptr cslots( PyTuple_New( size - 1 ) );
    if( !cslots )
        return 0;
    for( Py_ssize_t idx = 1; idx < size; idx++ )
    {
        cppy::ptr slot( cppy::incref( PyList_GET_ITEM( slots.get(), idx ) ) );
        PyTuple_SET_ITEM( cslots.get(), idx - 1, slot.release() );
    }

    size--;
    cppy::ptr argsptr( cppy::incref( args ) );
    cppy::ptr kwargsptr( cppy::incref( kwargs ) );
    for( Py_ssize_t idx = 0; idx < size; idx++ )
    {
        cppy::ptr slot( cppy::incref( PyTuple_GET_ITEM( cslots.get(), idx ) ) );
        if( !slot.call( argsptr, kwargsptr ) )
            return 0;
    }

    Py_RETURN_NONE;
}


PyObject*
BoundSignal_call( BoundSignal* self, PyObject* args, PyObject* kwargs )
{
    return BoundSignal_emit( self, args, kwargs );
}


PyObject*
BoundSignal_connect( BoundSignal* self, PyObject* slot )
{
    cppy::ptr objref( cppy::incref( self->objref ) );
    cppy::ptr obj( PyWeakref_GET_OBJECT( objref.get() ) );
    if( obj.is_none() )
        Py_RETURN_NONE;

    cppy::ptr dict;
    if( !load_obj_dict( obj, dict, true ) )
        return cppy::attribute_error( obj.get(), "__dict__" );
    if( !dict )
        return 0;

    cppy::ptr key( cppy::incref( SignalsKey ) );
    cppy::ptr signals( dict.getitem( key ) );
    if( signals )
    {
        if( !PyDict_CheckExact( signals.get() ) )
            return cppy::type_error( signals.get(), "dict" );
    }
    else
    {
        signals = PyDict_New();
        if( !signals )
            return 0;
        if( !dict.setitem( key, signals ) )
            return 0;
    }

    cppy::ptr owner( cppy::incref( self->owner ) );
    cppy::ptr slots( signals.getitem( owner ) );
    if( slots )
    {
        if( !PyList_CheckExact( slots.get() ) )
            return cppy::type_error( slots.get(), "list" );
    }
    else
    {
        slots = PyList_New( 0 );
        if( !slots )
            return 0;
        if( !signals.setitem( owner, slots ) )
            return 0;
    }

    if( PyList_Size( slots.get() ) == 0 )
    {
        cppy::ptr disc( _Disconnector::New( owner.get(), objref.get() ) );
        if( !disc )
            return 0;
        if( PyList_Append( slots.get(), disc.get() ) != 0 )
            return 0;
        disc.release();
    }

    cppy::ptr slotptr( cppy::incref( slot ) );
    if( PyMethod_Check( slot ) && PyMethod_GET_SELF( slot ) )
    {
        cppy::ptr args( PyTuple_New( 1 ) );
        if( !args )
            return 0;
        PyTuple_SET_ITEM( args.get(), 0, slotptr.release() );
        cppy::ptr wm_cls( cppy::incref( WeakMethod ) );
        cppy::ptr wm( wm_cls.call( args ) );
        if( !wm )
            return 0;
        args = PyTuple_New( 2 );
        if( !args )
            return 0;
        cppy::ptr disc( slots.getitem( 0 ) );
        PyTuple_SET_ITEM( args.get(), 0, wm.release() );
        PyTuple_SET_ITEM( args.get(), 1, disc.release() );
        cppy::ptr cr_cls( cppy::incref( CallableRef ) );
        slotptr = cr_cls.call( args );
        if( !slotptr )
            return 0;
    }

    if( !PyList_Append( slots.get(), slotptr.get() ) )
        return 0;
    slotptr.release();

    Py_RETURN_NONE;
}


PyObject*
BoundSignal_disconnect( BoundSignal* self, PyObject* slot )
{
    cppy::ptr slotptr( cppy::incref( slot ) );
    cppy::ptr args( PyTuple_New( 1 ) );
    if( !args )
        return 0;
    if( PyMethod_Check( slot ) && PyMethod_GET_SELF( slot ) )
    {
        args.setitem( 0, slotptr.get() );
        cppy::ptr wm_cls( cppy::incref( WeakMethod ) );
        cppy::ptr wm( wm_cls.call( args ) );
        if( !wm )
            return 0;
        args.setitem( 0, wm );
        cppy::ptr cr_cls( cppy::incref( CallableRef ) );
        slotptr = cr_cls.call( args );
        if( !slotptr )
            return 0;
    }
    cppy::ptr disc( _Disconnector::New( self->owner, self->objref ) );
    if( !disc )
        return 0;
    PyTuple_SET_ITEM( args.get(), 0, slotptr.release() );
    return disc.call( args );
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


static PyType_Slot BoundSignal_Type_slots[] = {
    { Py_tp_dealloc, void_cast( BoundSignal_dealloc ) },          /* tp_dealloc */
    { Py_tp_traverse, void_cast( BoundSignal_traverse ) },        /* tp_traverse */
    { Py_tp_clear, void_cast( BoundSignal_clear ) },              /* tp_clear */
    { Py_tp_methods, void_cast( BoundSignal_methods ) },          /* tp_doc */
    { Py_tp_doc, cast_py_tp_doc( BoundSignal__doc__ ) },          /* tp_doc */
    { Py_tp_call, void_cast( BoundSignal_call ) },                /* tp_call */
    { Py_tp_richcompare, void_cast( BoundSignal_richcompare ) },  /* tp_richcompare */
    { Py_tp_new, void_cast( BoundSignal_new ) },                  /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },            /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* BoundSignal::TypeObject = NULL;


PyType_Spec BoundSignal::TypeObject_Spec = {
	"enaml.signaling.BoundSignal",              /* tp_name */
	sizeof( BoundSignal ),                     /* tp_basicsize */
	0,                                          /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_HAVE_GC,                         /* tp_flags */
    BoundSignal_Type_slots                           /* slots */
};


bool BoundSignal::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


int
BoundSignal::TypeCheck( PyObject* obj )
{
    return PyObject_TypeCheck( obj, BoundSignal::TypeObject );
}


PyObject*
BoundSignal::New( PyObject* owner, PyObject* objref )
{
    cppy::ptr ownerptr( cppy::incref( owner ) );
    cppy::ptr objrefptr( cppy::incref( objref ) );
    cppy::ptr bsigptr;
    if( numfree > 0 )
    {
        PyObject* o = pyobject_cast( freelist[ --numfree ] );
        _Py_NewReference( o );
        bsigptr = o;
    }
    else
    {
        bsigptr = PyType_GenericAlloc( BoundSignal::TypeObject, 0 );
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

// Module definition
namespace
{


int
signaling_modexec( PyObject *mod )
{
    // Borrowed reference
    PyObject* mod_dict = PyModule_GetDict( mod );

    // Other module objects required for operation
    cppy::ptr wm_mod( PyImport_ImportModuleLevel( "weakmethod", mod_dict, 0, 0 , 1) );
    if( !wm_mod)
    {
        return -1;
    }
    cppy::ptr wm_cls( wm_mod.getattr( "WeakMethod" ) );
    if( !wm_cls )
    {
        return -1;
    }

    cppy::ptr cr_mod( PyImport_ImportModuleLevel( "callableref", mod_dict, 0, 0, 1 ) );
    if( !cr_mod )
    {
        return -1;
    }
    cppy::ptr cr_cls( cr_mod.getattr( "CallableRef" ) );
    if( !cr_cls )
    {
        return -1;
    }

    cppy::ptr key( PyUnicode_FromString( "_[signals]" ) );
    if( !key )
    {
        return -1;
    }

    SignalsKey = key.release();
    WeakMethod = wm_cls.release();
    CallableRef = cr_cls.release();

    if( !Signal::Ready() )
    {
        return -1;
    }
    if( !_Disconnector::Ready() )
    {
        return -1;
    }
    if( !BoundSignal::Ready() )
    {
        return -1;
    }

    // Signal
    cppy::ptr signal( pyobject_cast( Signal::TypeObject ) );
	if( PyModule_AddObject( mod, "Signal", signal.get() ) < 0 )
	{
		return -1;
	}
    signal.release();
    // _Disconnector
    cppy::ptr _disc( pyobject_cast( _Disconnector::TypeObject ) );
	if( PyModule_AddObject( mod, "_Disconnector", _disc.get() ) < 0 )
	{
		return -1;
	}
    _disc.release();
    // BoundSignal
    cppy::ptr bsignal( pyobject_cast( BoundSignal::TypeObject ) );
	if( PyModule_AddObject( mod, "BoundSignal", bsignal.get() ) < 0 )
	{
		return -1;
	}
    bsignal.release();

    return 0;
}

static PyMethodDef
signaling_methods[] = {
    { 0 } // sentinel
};


PyModuleDef_Slot signaling_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( signaling_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "signaling",
        "signaling extension module",
        0,
        signaling_methods,
        signaling_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_signaling( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
