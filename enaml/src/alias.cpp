/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
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

static PyObject* storage_str;


// POD struct - all member fields are considered private
struct Alias
{
	PyObject_HEAD
    PyObject* target;
    PyObject* chain;
    PyObject* key;
    bool canset;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


namespace
{


PyObject*
Alias_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* target;
    PyObject* chain;
    PyObject* key;
    if( !PyArg_ParseTuple( args, "OOO", &target, &chain, &key ) )
        return 0;
    if( !PyTuple_CheckExact( chain ) )
        return cppy::type_error( "argument 2 must be a tuple" );
    PyObject* self = PyType_GenericNew( type, 0, 0 );
    if( !self )
        return 0;
    Alias* alias = reinterpret_cast<Alias*>( self );
    alias->target = cppy::incref( target );
    alias->chain = cppy::incref( chain );
    alias->key = cppy::incref( key );
    alias->canset = false;
    return self;
}


void
Alias_dealloc( Alias* self )
{
    Py_CLEAR( self->target );
    Py_CLEAR( self->chain );
    Py_CLEAR( self->key );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
alias_load_fail( Alias* self )
{
    std::ostringstream ostr;
    cppy::ptr pystr( PyObject_Str( self->target ) );
    if( !pystr )
        return 0;
    ostr << PyUnicode_AsUTF8( pystr.get() );
    Py_ssize_t size = PyTuple_GET_SIZE( self->chain );
    for( Py_ssize_t i = 0; i < size; ++i )
    {
        pystr = PyObject_Str( PyTuple_GET_ITEM( self->chain, i ) );
        if( !pystr )
            return 0;
        ostr << "." << PyUnicode_AsUTF8( pystr.get() );
    }
    PyErr_Format(
        PyExc_RuntimeError,
        "failed to load alias '%s'",
        ostr.str().c_str()
    );
    return 0;
}


int
alias_load_set_fail( Alias* self )
{
    alias_load_fail( self );
    return -1;
}


PyObject*
Alias__get__( Alias* self, PyObject* object, PyObject* type )
{
    if( !object )
        return cppy::incref( pyobject_cast( self ) );
    cppy::ptr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return 0;
    cppy::ptr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return 0;
    cppy::ptr target( PyObject_GetItem( f_locals.get(), self->target ) );
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


int
Alias__set__( Alias* self, PyObject* object, PyObject* value )
{
    if( !self->canset )
    {
        PyErr_Format(
            PyExc_AttributeError, "can't %s alias", value ? "set" : "delete"
        );
        return -1;
    }
    cppy::ptr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return -1;
    cppy::ptr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return -1;
    cppy::ptr target( PyObject_GetItem( f_locals.get(), self->target ) );
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


PyObject*
Alias_resolve( Alias* self, PyObject* object )
{
    cppy::ptr storage( PyObject_GetAttr( object, storage_str ) );
    if( !storage )
        return 0;
    cppy::ptr f_locals( PyObject_GetItem( storage.get(), self->key ) );
    if( !f_locals )
        return 0;
    cppy::ptr target( PyObject_GetItem( f_locals.get(), self->target ) );
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


PyObject*
Alias_get_target( Alias* self, void* ctxt )
{
    return cppy::incref( self->target );
}


PyObject*
Alias_get_chain( Alias* self, void* ctxt )
{
    return cppy::incref( self->chain );
}


PyObject*
Alias_get_key( Alias* self, void* ctxt )
{
    return cppy::incref( self->key );
}


PyObject*
Alias_get_canset( Alias* self, void* ctxt )
{
    return cppy::incref( self->canset ? Py_True : Py_False );
}


int
Alias_set_canset( Alias* self, PyObject* value, void* ctxt )
{
    if( !PyBool_Check( value ) )
    {
        cppy::type_error( value, "bool" );
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


static PyType_Slot Alias_Type_slots[] = {
    { Py_tp_dealloc, void_cast( Alias_dealloc ) },        /* tp_dealloc */
    { Py_tp_methods, void_cast( Alias_methods ) },        /* tp_methods */
    { Py_tp_getset, void_cast( Alias_getset ) },          /* tp_getset */
    { Py_tp_descr_get, void_cast( Alias__get__ ) },       /* tp_descr_get */
    { Py_tp_descr_set, void_cast( Alias__set__ ) },       /* tp_descr_set */
    { Py_tp_new, void_cast( Alias_new ) },                /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },    /* tp_alloc */
    { Py_tp_free, void_cast( PyObject_Del ) },            /* tp_free */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* Alias::TypeObject = NULL;


PyType_Spec Alias::TypeObject_Spec = {
	"enaml.alias.Alias",                 /* tp_name */
	sizeof( Alias ),                     /* tp_basicsize */
	0,                                   /* tp_itemsize */
	Py_TPFLAGS_DEFAULT,                  /* tp_flags */
    Alias_Type_slots                     /* slots */
};


bool Alias::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


// Module definition
namespace
{


int
alias_modexec( PyObject *mod )
{
    storage_str = PyUnicode_FromString( "_d_storage" );
    if( !storage_str )
    {
        return -1;
    }

    if( !Alias::Ready() )
    {
        return -1;
    }

    // alias
    cppy::ptr alias( pyobject_cast( Alias::TypeObject ) );
	if( PyModule_AddObject( mod, "Alias", alias.get() ) < 0 )
	{
		return -1;
	}
    alias.release();

    return 0;
}


static PyMethodDef
alias_methods[] = {
    { 0 } // Sentinel
};


PyModuleDef_Slot alias_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( alias_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "alias",
        "alias extension module",
        0,
        alias_methods,
        alias_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_alias( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
