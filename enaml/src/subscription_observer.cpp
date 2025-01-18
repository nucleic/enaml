/*-----------------------------------------------------------------------------
 * | Copyright (c) 2025, Nucleic Development Team.
 * |
 * | Distributed under the terms of the Modified BSD License.
 * |
 * | The full license is in the file LICENSE, distributed with this software.
 * |----------------------------------------------------------------------------*/
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

// ptr to atom.api.atomref
static PyObject* atomref;
static PyObject* d_engine_str;
static PyObject* update_str;

// POD struct - all member fields are considered private
struct SubscriptionObserver
{
    PyObject_HEAD
    PyObject* ref;
    PyObject* name;

    static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

    static bool Ready();

    static bool TypeCheck( PyObject* ob );

};


namespace
{


PyObject*
SubscriptionObserver_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* owner;
    PyObject* name;
    static char* kwlist[] = { "owner", "name", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "OU", kwlist, &owner, &name ) )
    {
        return 0;
    }
    cppy::ptr ptr( PyType_GenericNew( type, args, kwargs ) );
    if( !ptr )
    {
        return 0;
    }
    SubscriptionObserver* self = reinterpret_cast<SubscriptionObserver*>( ptr.get() );

    self->ref = PyObject_CallOneArg(atomref, owner);
    if( !self->ref )
    {
        return 0;
    }
    self->name =  cppy::incref( name );
    return ptr.release();
}


void
SubscriptionObserver_clear( SubscriptionObserver* self )
{
    Py_CLEAR( self->ref );
    Py_CLEAR( self->name );
}


int
SubscriptionObserver_traverse( SubscriptionObserver* self, visitproc visit, void* arg )
{
    Py_VISIT( self->ref );
    return 0;
}


void
SubscriptionObserver_dealloc( SubscriptionObserver* self )
{
    PyObject_GC_UnTrack( self );
    SubscriptionObserver_clear( self );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


int
SubscriptionObserver__bool__( SubscriptionObserver* self )
{
    return PyObject_IsTrue( self->ref );
}


/*
 * Calls engine update with the owner and name
 * if self.ref:
 *     owner = self.ref()
 *     engine = owner._d_engine
 *      if engine is not None:
 *         engine.update(owner, self.name)
 */
PyObject*
SubscriptionObserver_call( SubscriptionObserver* self, PyObject* args, PyObject* kwargs )
{

    if( PyObject_IsTrue( self->ref ) )
    {
        cppy::ptr owner( PyObject_CallNoArgs( self->ref ) );
        if ( !owner )
            return 0;
        cppy::ptr engine( owner.getattr( d_engine_str ) );
        if ( !engine )
            return 0;
        if ( !engine.is_none() )
        {
            cppy::ptr update_args( PyTuple_New( 2 ) );
            if( !update_args )
                return 0;
            PyTuple_SET_ITEM( update_args.get(), 0, cppy::incref( owner.get() ) );
            PyTuple_SET_ITEM( update_args.get(), 1, cppy::incref( self->name ) );
            cppy::ptr update( engine.getattr( update_str ) );
            if ( !update )
                return 0;
            return update.call( update_args );
        }
    }
    Py_RETURN_NONE;
}


PyDoc_STRVAR(SubscriptionObserver__doc__,
    "SubscriptionObserver(owner, name)\n\n"
    "An observer object which manages a tracer subscription.\n"
    "Parameters\n"
    "----------\n"
    "owner : Declarative\n"
    "    The declarative owner of interest.\n\n"
    "name : string\n"
    "    The name to which the operator is bound\n");


PyObject*
SubscriptionObserver_get_ref( SubscriptionObserver* self, void* context )
{
    return cppy::incref( self->ref );
}


PyObject*
SubscriptionObserver_set_ref( SubscriptionObserver* self, PyObject* value, void* context )
{
    if( value != Py_None )
        return cppy::type_error("ref can only be set to None");
    cppy::replace( &self->ref, Py_None );
    return 0;
}


PyObject*
SubscriptionObserver_get_name( SubscriptionObserver* self, void* context )
{
    return cppy::incref( self->name );
}


static PyGetSetDef
SubscriptionObserver_getset[] = {
    { "ref", ( getter )SubscriptionObserver_get_ref, ( setter )SubscriptionObserver_set_ref,
      "Get and set the ref for the observer." },
    { "name", ( getter )SubscriptionObserver_get_name, 0,
      "Get the name for the observer." },
    { 0 } // sentinel
};


static PyType_Slot SubscriptionObserver_Type_slots[] = {
    { Py_tp_dealloc, void_cast( SubscriptionObserver_dealloc ) },          /* tp_dealloc */
    { Py_tp_traverse, void_cast( SubscriptionObserver_traverse) },         /* tp_traverse */
    { Py_tp_clear, void_cast( SubscriptionObserver_clear ) },              /* tp_clear */
    { Py_tp_call, void_cast( SubscriptionObserver_call ) },                /* tp_call */
    { Py_tp_doc, cast_py_tp_doc( SubscriptionObserver__doc__ ) },          /* tp_doc */
    { Py_nb_bool, void_cast( SubscriptionObserver__bool__ ) },             /* nb_bool */
    { Py_tp_getset, void_cast( SubscriptionObserver_getset ) },            /* tp_getset */
    { Py_tp_new, void_cast( SubscriptionObserver_new ) },                  /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },                     /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* SubscriptionObserver::TypeObject = NULL;


PyType_Spec SubscriptionObserver::TypeObject_Spec = {
    "enaml.core.subscription_observer.SubscriptionObserver",     /* tp_name */
    sizeof( SubscriptionObserver ),               /* tp_basicsize */
    0,                                   /* tp_itemsize */
    Py_TPFLAGS_DEFAULT
    |Py_TPFLAGS_BASETYPE
    |Py_TPFLAGS_HAVE_GC,                 /* tp_flags */
    SubscriptionObserver_Type_slots               /* slots */
};


bool SubscriptionObserver::Ready()
{
    // The reference will be handled by the module to which we will add the type
    TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


bool SubscriptionObserver::TypeCheck( PyObject* ob )
{
    return PyObject_TypeCheck( ob, TypeObject ) != 0;
}


// Module definition
namespace
{


    int
    subscription_observer_modexec( PyObject *mod )
    {
        if( !SubscriptionObserver::Ready() )
        {
            return -1;
        }

        update_str = PyUnicode_FromString("update");
        if ( !update_str )
            return -1;

        d_engine_str = PyUnicode_FromString("_d_engine");
        if ( !d_engine_str )
            return -1;

        cppy::ptr atom_api( PyImport_ImportModule("atom.api") );
        if ( !atom_api )
        {
            PyErr_SetString( PyExc_ImportError, "Could not import atom.api" );
            return -1;
        }
        atomref = atom_api.getattr("atomref");
        if ( !atomref )
        {
            PyErr_SetString( PyExc_ImportError, "Could not import atom.api.atomref" );
            return -1;
        }

        // subscription_observer
        cppy::ptr subscription_observer( pyobject_cast(  SubscriptionObserver::TypeObject ) );
        if( PyModule_AddObject( mod, "SubscriptionObserver", subscription_observer.get() ) < 0 )
        {
            return -1;
        }
        subscription_observer.release();

        return 0;
    }


    PyMethodDef
    subscription_observer_methods[] = {
        { 0 } // Sentinel
    };


    PyModuleDef_Slot subscription_observer_slots[] = {
        {Py_mod_exec, reinterpret_cast<void*>( subscription_observer_modexec ) },
        {0, NULL}
    };


    struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "subscription_observer",
        "subscription_observer extension module",
        0,
        subscription_observer_methods,
        subscription_observer_slots,
        NULL,
        NULL,
        NULL
    };


}  // module namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_subscription_observer( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
