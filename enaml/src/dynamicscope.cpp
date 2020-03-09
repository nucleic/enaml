/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
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
struct Nonlocals
{
	PyObject_HEAD
    PyObject* owner;
    PyObject* tracer;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


// POD struct - all member fields are considered private
struct DynamicScope
{
	PyObject_HEAD
    PyObject* owner;
    PyObject* change;
    PyObject* tracer;
    PyObject* f_locals;
    PyObject* f_globals;
    PyObject* f_builtins;
    PyObject* f_writes;
    PyObject* f_nonlocals;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


namespace
{


static PyObject* parent_str;
static PyObject* dynamic_load_str;
static PyObject* UserKeyError;


/*-----------------------------------------------------------------------------
| Utilities
|----------------------------------------------------------------------------*/
int
test_dynamic_attr( PyObject* obj, PyObject* name )
{
    PyTypeObject* tp;
    PyObject** dictptr;
    cppy::ptr descr;
    descrgetfunc descr_f;
    cppy::ptr objptr( cppy::incref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers and _PyObject_GetDictPtr, and only test for
    // the presence of descriptors, not evaluate them.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data descriptor
        descr_f = 0;
        descr = cppy::xincref( _PyType_Lookup( tp, name ) );
        if( descr )
        {
            descr_f = descr.get()->ob_type->tp_descr_get;
            if( descr_f && PyDescr_IsData( descr.get() ) )
                return 1;
        }

        // Instance dictionary
        dictptr = _PyObject_GetDictPtr( objptr.get() );
        if( dictptr && *dictptr )
        {
            if( PyDict_GetItem( *dictptr, name ) )
                return 1;
        }

        // Non-data descriptor
        if( descr_f || descr )
            return 1;

        // Step up to the parent object
        objptr = PyObject_GetAttr( objptr.get(), parent_str );
        if( !objptr )
            return -1;
    }

    return 0;
}


// The evaluation of a descriptor can trigger arbitrary code to execute,
// such as an expression bound to an attribute. If that expression raises
// a key error, it would be treated as a scope miss instead of reporting
// the failure in the user code. This function is used to convert such an
// error into a UserKeyError, which does not derive from KeyError and so
// will not be trapped by the Python VM during expression eval.
inline void
maybe_translate_key_error()
{
    if( PyErr_Occurred() && PyErr_ExceptionMatches( PyExc_KeyError ) )
    {
        PyObject* ptype;
        PyObject* pvalue;
        PyObject* ptraceback;
        PyErr_Fetch( &ptype, &pvalue, &ptraceback );
        PyErr_Restore( cppy::incref( UserKeyError ), pvalue, ptraceback );
        Py_DECREF( ptype );
    }
}


inline bool
run_tracer( PyObject* tracer, PyObject* owner, PyObject* name, PyObject* value )
{
    cppy::ptr handler( PyObject_GetAttr( tracer, dynamic_load_str ) );
    if( !handler )
        return false;
    cppy::ptr args( PyTuple_New( 3 ) );
    if( !args )
        return false;
    PyTuple_SET_ITEM( args.get(), 0, cppy::incref( owner ) );
    PyTuple_SET_ITEM( args.get(), 1, cppy::incref( name ) );
    PyTuple_SET_ITEM( args.get(), 2, cppy::incref( value ) );
    cppy::ptr res( handler.call( args ) );
    if( !res )
        return false;
    return true;
}


PyObject*
load_dynamic_attr( PyObject* obj, PyObject* name, PyObject* tracer=0 )
{
    PyTypeObject* tp;
    PyObject** dictptr;
    cppy::ptr descr;
    descrgetfunc descr_f;
    cppy::ptr objptr( cppy::incref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers and _PyObject_GetDictPtr, and run a tracer.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data descriptor
        descr_f = 0;
        descr = cppy::xincref( _PyType_Lookup( tp, name ) );
        if( descr )
        {
            descr_f = descr.get()->ob_type->tp_descr_get;
            if( descr_f && PyDescr_IsData( descr.get() ) )
            {
                cppy::ptr res(
                    descr_f( descr.get(), objptr.get(), pyobject_cast( tp ) )
                );
                if( !res )
                    maybe_translate_key_error();
                else if( tracer && !run_tracer( tracer, objptr.get(), name, res.get() ) )
                    return 0;
                return res.release();
            }
        }

        // Instance dictionary
        dictptr = _PyObject_GetDictPtr( objptr.get() );
        if( dictptr && *dictptr )
        {
            PyObject* item = PyDict_GetItem( *dictptr, name );
            if( item )
            {
                if( tracer && !run_tracer( tracer, objptr.get(), name, item ) )
                    return 0;
                return cppy::incref( item );
            }
        }

        // Non-data descriptor
        if( descr_f )
        {
            cppy::ptr res(
                descr_f( descr.get(), objptr.get(), pyobject_cast( tp ) )
            );
            if( !res )
                maybe_translate_key_error();
            else if( tracer && !run_tracer( tracer, objptr.get(), name, res.get() ) )
                return 0;
            return res.release();
        }

        // Non-readable descriptor
        if( descr )
        {
            if( tracer && !run_tracer( tracer, objptr.get(), name, descr.get() ) )
                return 0;
            return descr.release();
        }

        // Step up to the parent object
        objptr = PyObject_GetAttr( objptr.get(), parent_str );
        if( !objptr )
            return 0;
    }

    return 0;
}


int
set_dynamic_attr( PyObject* obj, PyObject* name, PyObject* value )
{
    PyTypeObject* tp;
    PyObject* dict;
    PyObject** dictptr;
    cppy::ptr descr;
    descrsetfunc descr_f;
    cppy::ptr objptr( cppy::incref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data desciptor
        descr_f = 0;
        descr = cppy::xincref( _PyType_Lookup( tp, name ) );
        if( descr )
        {
            descr_f = descr.get()->ob_type->tp_descr_set;
            if( descr_f && PyDescr_IsData( descr.get() ) )
                return descr_f( descr.get(), objptr.get(), value );
        }

        // Instance dictionary
        dict = 0;
        dictptr = _PyObject_GetDictPtr( obj );
        if( dictptr )
        {
            dict = *dictptr;
            if( !dict && value )
            {
                dict = PyDict_New();
                if( !dict )
                    return -1;
                *dictptr = dict;
            }
        }
        if( dict )
        {
            if( value )
                return PyDict_SetItem( dict, name, value );
            if( PyDict_DelItem( dict, name ) == 0 )
                return 0;
            if( !PyErr_ExceptionMatches( PyExc_KeyError ) )
                return -1;
            PyErr_Clear();
        }

        // Non-data descriptor
        if( descr_f )
            return descr_f( descr.get(), objptr.get(), value );

        // Read-only descriptor
        if( descr )
            PyErr_Format(
                PyExc_AttributeError,
                "'%.50s' object attribute '%.400s' is read-only",
                tp->tp_name, PyUnicode_AsUTF8( name )
            );

        // Step up to the parent object
        objptr = PyObject_GetAttr( objptr.get(), parent_str );
        if( !objptr )
            return -1;
    }

    return -1;
}


/*-----------------------------------------------------------------------------
| Nonlocals
|----------------------------------------------------------------------------*/
void
Nonlocals_clear( Nonlocals* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->tracer );
}


int
Nonlocals_traverse( Nonlocals* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->tracer );
    return 0;
}


void
Nonlocals_dealloc( Nonlocals* self )
{
    PyObject_GC_UnTrack( self );
    Nonlocals_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
Nonlocals_repr( Nonlocals* self )
{
    cppy::ptr pystr( PyObject_Str( self->owner ) );
    if( !pystr )
        return 0;
    return PyUnicode_FromFormat(
        "%s[%s]",
        Py_TYPE(self)->tp_name,
        PyUnicode_AsUTF8( pystr.get() )
    );
}


PyObject*
Nonlocals_call( Nonlocals* self, PyObject* args, PyObject* kwargs )
{
    unsigned int level;
    static char* kwlist[] = { "level", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "I", kwlist, &level ) )
        return 0;
    unsigned int offset = 0;
    cppy::ptr parentptr;
    cppy::ptr objptr( cppy::incref( self->owner ) );
    while( offset != level )
    {
        parentptr = PyObject_GetAttr( objptr.get(), parent_str );
        if( !parentptr )
            return 0;
        if( parentptr.get() == Py_None )
            break;
        objptr = parentptr;
        ++offset;
    }
    if( offset != level )
    {
        PyErr_Format( PyExc_ValueError, "Scope level %u is out of range", level );
        return 0;
    }
    PyObject* res = PyType_GenericNew( Py_TYPE(self), 0, 0 );
    if( res )
    {
        Nonlocals* nl = reinterpret_cast<Nonlocals*>( res );
        nl->owner = cppy::incref( objptr.get() );
        nl->tracer = cppy::xincref( self->tracer );
    }
    return res;
}


PyObject*
Nonlocals_getattro( Nonlocals* self, PyObject* name )
{
    PyObject* res = load_dynamic_attr( self->owner, name, self->tracer );
    if( !res && !PyErr_Occurred() )
        PyErr_Format(
            PyExc_AttributeError,
            "'%.50s' object has no attribute '%.400s'",
            Py_TYPE(self)->tp_name,
            PyUnicode_AsUTF8( name )
        );
    return res;
}


int
Nonlocals_setattro( Nonlocals* self, PyObject* name, PyObject* value )
{
    int res = set_dynamic_attr( self->owner, name, value );
    if( res < 0 && !PyErr_Occurred() )
        PyErr_Format(
            PyExc_AttributeError,
            "'%.50s' object has no attribute '%.400s'",
            Py_TYPE(self)->tp_name,
            PyUnicode_AsUTF8( name )
        );
    return res;
}


PyObject*
Nonlocals_getitem( Nonlocals* self, PyObject* key )
{
    if( !PyUnicode_CheckExact( key ) )
        return cppy::type_error( key, "str" );
    PyObject* res = load_dynamic_attr( self->owner, key, self->tracer );
    if( !res && !PyErr_Occurred() )
        PyErr_SetObject( PyExc_KeyError, key );
    return res;
}


int
Nonlocals_setitem( Nonlocals* self, PyObject* key, PyObject* value )
{
    if( !PyUnicode_CheckExact( key ) )
    {
        cppy::type_error( key, "str" );
        return -1;
    }
    int res = set_dynamic_attr( self->owner, key, value );
    if( res < 0 && !PyErr_Occurred() )
        PyErr_SetObject( PyExc_KeyError, key );
    return res;
}


int
Nonlocals_contains( Nonlocals* self, PyObject* key )
{
    if( !PyUnicode_CheckExact( key ) )
    {
        cppy::type_error( key, "str" );
        return -1;
    }
    return test_dynamic_attr( self->owner, key );
}


static PyType_Slot Nonlocals_Type_slots[] = {
    { Py_tp_dealloc, void_cast( Nonlocals_dealloc ) },        /* tp_dealloc */
    { Py_tp_traverse, void_cast( Nonlocals_traverse ) },      /* tp_traverse */
    { Py_tp_clear, void_cast( Nonlocals_clear ) },            /* tp_clear */
    { Py_tp_call, void_cast( Nonlocals_call ) },              /* tp_call */
    { Py_tp_repr, void_cast( Nonlocals_repr ) },              /* tp_repr */
    { Py_tp_getattro, void_cast( Nonlocals_getattro ) },      /* tp_getattro */
    { Py_tp_setattro, void_cast( Nonlocals_setattro ) },      /* tp_setattro */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },        /* tp_alloc */
    { Py_tp_free, void_cast( PyObject_GC_Del ) },             /* tp_free */
    { Py_mp_subscript, void_cast( Nonlocals_getitem ) },      /* mp_subscript */
    { Py_mp_ass_subscript, void_cast( Nonlocals_setitem ) },  /* mp_ass_subscript */
    { Py_sq_contains, void_cast( Nonlocals_contains ) },      /* sq_contains */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* Nonlocals::TypeObject = NULL;


PyType_Spec Nonlocals::TypeObject_Spec = {
	"enaml.dynamicscope.Nonlocals",    /* tp_name */
	sizeof( Nonlocals ),               /* tp_basicsize */
	0,                                 /* tp_itemsize */
	Py_TPFLAGS_DEFAULT|
    Py_TPFLAGS_HAVE_GC,                /* tp_flags */
    Nonlocals_Type_slots               /* slots */
};


bool Nonlocals::Ready()
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


/*-----------------------------------------------------------------------------
| DynamicScope
|----------------------------------------------------------------------------*/
PyObject*
DynamicScope_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* owner;
    PyObject* f_locals;
    PyObject* f_globals;
    PyObject* f_builtins;
    PyObject* change = 0;
    PyObject* tracer = 0;
    static char* kwlist[] = {
        "owner", "f_locals", "f_globals", "f_builtins", "change", "tracer", 0
    };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "OOOO|OO:__new__", kwlist,
        &owner, &f_locals, &f_globals, &f_builtins, &change, &tracer ) )
        return 0;
    if( !PyMapping_Check( f_locals ) )
        return cppy::type_error( f_locals, "mapping" );
    if( !PyDict_CheckExact( f_globals ) )
        return cppy::type_error( f_globals, "dict" );
    if( !PyDict_CheckExact( f_builtins ) )
        return cppy::type_error( f_builtins, "dict" );
    PyObject* self = PyType_GenericNew( type, 0, 0 );
    if( !self )
        return 0;
    DynamicScope* scope = reinterpret_cast<DynamicScope*>( self );
    scope->owner = cppy::incref( owner );
    scope->f_locals = cppy::incref( f_locals );
    scope->f_globals = cppy::incref( f_globals );
    scope->f_builtins = cppy::incref( f_builtins );
    if( change && change != Py_None )
        scope->change = cppy::incref( change );
    if( tracer && tracer != Py_None )
        scope->tracer = cppy::incref( tracer );
    return self;
}


void
DynamicScope_clear( DynamicScope* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->change );
    Py_CLEAR( self->tracer );
    Py_CLEAR( self->f_locals );
    Py_CLEAR( self->f_globals );
    Py_CLEAR( self->f_builtins );
    Py_CLEAR( self->f_writes );
    Py_CLEAR( self->f_nonlocals );
}


int
DynamicScope_traverse( DynamicScope* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->change );
    Py_VISIT( self->tracer );
    Py_VISIT( self->f_locals );
    Py_VISIT( self->f_globals );
    Py_VISIT( self->f_builtins );
    Py_VISIT( self->f_writes );
    Py_VISIT( self->f_nonlocals );
    return 0;
}


void
DynamicScope_dealloc( DynamicScope* self )
{
    PyObject_GC_UnTrack( self );
    DynamicScope_clear( self );
    Py_TYPE(self)->tp_free( pyobject_cast( self ) );
}


PyObject*
DynamicScope_getitem( DynamicScope* self, PyObject* key )
{
    if( !PyUnicode_CheckExact( key ) )
        return cppy::type_error( key, "str" );

    PyObject* res;

    // value from the override scope
    if( self->f_writes )
    {
        res = PyDict_GetItem( self->f_writes, key );
        if( res )
            return cppy::incref( res );
    }

    // 'self' magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "self" ) == 0 )
        return cppy::incref( self->owner );

    // 'change' magic
    if( self->change && strcmp( (char *)PyUnicode_AsUTF8( key ), "change" ) == 0 )
        return cppy::incref( self->change );

    // 'nonlocals' magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "nonlocals" ) == 0 )
    {
        if( !self->f_nonlocals )
        {
            self->f_nonlocals = PyType_GenericNew( Nonlocals::TypeObject, 0, 0 );
            if( !self->f_nonlocals )
                return 0;
            Nonlocals* nl = reinterpret_cast<Nonlocals*>( self->f_nonlocals );
            nl->owner = cppy::incref( self->owner );
            nl->tracer = cppy::xincref( self->tracer );
        }
        return cppy::incref( self->f_nonlocals );
    }

    // __scope__ magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "__scope__" ) == 0 )
        return cppy::incref( pyobject_cast( self ) );

    // _[tracer] magic
    if( self->tracer && strcmp( (char *)PyUnicode_AsUTF8( key ), "_[tracer]" ) == 0 )
        return cppy::incref( pyobject_cast( self->tracer ) );

    // value from the local scope
    res = PyObject_GetItem( self->f_locals, key );
    if( res )
        return res;
    if( PyErr_Occurred() )
    {
        if( !PyErr_ExceptionMatches( PyExc_KeyError ) )
            return 0;
        PyErr_Clear();
    }

    // value from the global scope
    res = PyDict_GetItem( self->f_globals, key );
    if( res )
        return cppy::incref( res );

    // value from the builtin scope
    res = PyDict_GetItem( self->f_builtins, key );
    if( res )
        return cppy::incref( res );

    res = load_dynamic_attr( self->owner, key, self->tracer );
    if( res )
        return res;
    if( PyErr_Occurred() )
        return 0;

    PyErr_SetObject( PyExc_KeyError, key );
    return 0;
}

PyObject*
DynamicScope_get( DynamicScope* self, PyObject* args)
{
    PyObject *key;
    PyObject *default_value = NULL;

    if ( !PyArg_ParseTuple(args, "O|O", &key, &default_value) )
    {
        return 0;
    }

    PyObject* res = DynamicScope_getitem(self, key);
    if ( res )
    {
        return res; // Ref already incremented
    }

    if( PyErr_Occurred() )
    {
        if( !PyErr_ExceptionMatches( PyExc_KeyError ) )
        {
            return 0;
        }
        PyErr_Clear();
    }

    if ( !default_value )
    {
        Py_RETURN_NONE;
    }
    return cppy::incref( default_value );
}

int
DynamicScope_setitem( DynamicScope* self, PyObject* key, PyObject* value )
{
    if( !PyUnicode_CheckExact( key ) )
    {
        cppy::type_error( key, "str" );
        return -1;
    }
    if( !value )
    {
        if( self->f_writes )
            return PyDict_DelItem( self->f_writes, key );
        PyErr_SetObject( PyExc_KeyError, key );
        return -1;
    }
    if( !self->f_writes )
    {
        self->f_writes = PyDict_New();
        if( !self->f_writes )
            return -1;
    }
    return PyDict_SetItem( self->f_writes, key, value );
}


int
DynamicScope_contains( DynamicScope* self, PyObject* key )
{
    if( !PyUnicode_CheckExact( key ) )
    {
        cppy::type_error( key, "str" );
        return -1;
    }

    // value from the override scope
    if( self->f_writes && PyDict_GetItem( self->f_writes, key ) )
        return 1;

    // 'self' magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "self" ) == 0 )
        return 1;

    // 'change' magic
    if( self->change && strcmp( (char *)PyUnicode_AsUTF8( key ), "change" ) == 0 )
        return 1;

    // 'nonlocals' magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "nonlocals" ) == 0 )
        return 1;

    // __scope__ magic
    if( strcmp( (char *)PyUnicode_AsUTF8( key ), "__scope__" ) == 0 )
        return 1;

    // _[tracer] magic
    if( self->tracer && strcmp( (char *)PyUnicode_AsUTF8( key ), "_[tracer]" ) == 0 )
        return 1;

    // value from the local scope
    cppy::ptr item( PyObject_GetItem( self->f_locals, key ) );
    if( item )
        return 1;
    if( PyErr_Occurred() )
    {
        if( !PyErr_ExceptionMatches( PyExc_KeyError ) )
            return -1;
        PyErr_Clear();
    }

    // value from the global scope
    if( PyDict_GetItem( self->f_globals, key ) )
        return 1;

    // value from the builtin scope
    if( PyDict_GetItem( self->f_builtins, key ) )
        return 1;

    return test_dynamic_attr( self->owner, key );
}


static PyMethodDef DynamicScope_methods[] = {
    {"get",    reinterpret_cast<PyCFunction>(DynamicScope_get), METH_VARARGS, ""},
    { 0 }  // Sentinel
};

static PyType_Slot DynamicScope_Type_slots[] = {
    { Py_tp_dealloc, void_cast( DynamicScope_dealloc ) },           /* tp_dealloc */
    { Py_tp_traverse, void_cast( DynamicScope_traverse ) },         /* tp_traverse */
    { Py_tp_clear, void_cast( DynamicScope_clear ) },               /* tp_clear */
    { Py_tp_new, void_cast( DynamicScope_new ) },                /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },           /* tp_alloc */
    { Py_tp_free, void_cast( PyObject_GC_Del ) },                /* tp_free */
    { Py_tp_methods, void_cast( DynamicScope_methods ) },        /* tp_methods */
    { Py_mp_subscript, void_cast( DynamicScope_getitem ) },      /* mp_subscript */
    { Py_mp_ass_subscript, void_cast( DynamicScope_setitem ) },  /* mp_ass_subscript */
    { Py_sq_contains, void_cast( DynamicScope_contains ) },      /* sq_contains */
    { 0, 0 },
};

}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* DynamicScope::TypeObject = NULL;


PyType_Spec DynamicScope::TypeObject_Spec = {
	"enaml.dynamicscope.DynamicScope",    /* tp_name */
	sizeof( DynamicScope ),               /* tp_basicsize */
	0,                                    /* tp_itemsize */
	Py_TPFLAGS_DEFAULT
    |Py_TPFLAGS_HAVE_GC
    |Py_TPFLAGS_DICT_SUBCLASS,            /* tp_flags */
    DynamicScope_Type_slots               /* slots */
};


bool DynamicScope::Ready()
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
dynamicscope_modexec( PyObject *mod )
{
    parent_str = PyUnicode_FromString( "_parent" );
    if( !parent_str )
    {
        return -1;
    }
    dynamic_load_str = PyUnicode_FromString( "dynamic_load" );
    if( !dynamic_load_str )
    {
        return -1;
    }
    UserKeyError = PyErr_NewException( "dynamicscope.UserKeyError", 0, 0 );
    if( !UserKeyError )
    {
        return -1;
    }

    if( !Nonlocals::Ready() )
    {
        return -1;
    }
    if( !DynamicScope::Ready() )
    {
        return -1;
    }

    // DynamicScope
    cppy::ptr dynamicscope( pyobject_cast( DynamicScope::TypeObject ) );
	if( PyModule_AddObject( mod, "DynamicScope", dynamicscope.get() ) < 0 )
	{
		return -1;
	}
    dynamicscope.release();

    PyModule_AddObject( mod, "UserKeyError", UserKeyError );

    return 0;
}


static PyMethodDef
dynamicscope_methods[] = {
    { 0 }  // Sentinel
};


PyModuleDef_Slot dynamicscope_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( dynamicscope_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "dynamicscope",
        "dynamicscope extension module",
        0,
        dynamicscope_methods,
        dynamicscope_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_dynamicscope( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
