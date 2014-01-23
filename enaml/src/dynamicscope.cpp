/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "pythonhelpersex.h"


using namespace PythonHelpers;


static PyObject* parent_str;
static PyObject* dynamic_load_str;
static PyObject* UserKeyError;


typedef struct {
    PyObject_HEAD
    PyObject* owner;
    PyObject* tracer;
} Nonlocals;


typedef struct {
    PyObject_HEAD
    PyObject* owner;
    PyObject* change;
    PyObject* tracer;
    PyObject* f_locals;
    PyObject* f_globals;
    PyObject* f_builtins;
    PyObject* f_writes;
    PyObject* f_nonlocals;
} DynamicScope;


/*-----------------------------------------------------------------------------
| Utilities
|----------------------------------------------------------------------------*/
static int
test_dynamic_attr( PyObject* obj, PyObject* name )
{
    PyTypeObject* tp;
    PyObject** dictptr;
    PyObjectPtr descr;
    descrgetfunc descr_f;
    PyObjectPtr objptr( newref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers and _PyObject_GetDictPtr, and only test for
    // the presence of descriptors, not evaluate them.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data descriptor
        descr_f = 0;
        descr = xnewref( _PyType_Lookup( tp, name ) );
        if( descr && PyType_HasFeature( descr.get()->ob_type, Py_TPFLAGS_HAVE_CLASS ) )
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
static inline void
maybe_translate_key_error()
{
    if( PyErr_Occurred() && PyErr_ExceptionMatches( PyExc_KeyError ) )
    {
        PyObject* ptype;
        PyObject* pvalue;
        PyObject* ptraceback;
        PyErr_Fetch( &ptype, &pvalue, &ptraceback );
        PyErr_Restore( newref( UserKeyError ), pvalue, ptraceback );
        Py_DECREF( ptype );
    }
}


static inline bool
run_tracer( PyObject* tracer, PyObject* owner, PyObject* name, PyObject* value )
{
    PyObjectPtr handler( PyObject_GetAttr( tracer, dynamic_load_str ) );
    if( !handler )
        return false;
    PyTuplePtr args( PyTuple_New( 3 ) );
    if( !args )
        return false;
    args.initialize( 0, newref( owner ) );
    args.initialize( 1, newref( name ) );
    args.initialize( 2, newref( value ) );
    PyObjectPtr res( handler( args ) );
    if( !res )
        return false;
    return true;
}


static PyObject*
load_dynamic_attr( PyObject* obj, PyObject* name, PyObject* tracer=0 )
{
    PyTypeObject* tp;
    PyObject** dictptr;
    PyObjectPtr descr;
    descrgetfunc descr_f;
    PyObjectPtr objptr( newref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers and _PyObject_GetDictPtr, and run a tracer.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data descriptor
        descr_f = 0;
        descr = xnewref( _PyType_Lookup( tp, name ) );
        if( descr && PyType_HasFeature( descr.get()->ob_type, Py_TPFLAGS_HAVE_CLASS ) )
        {
            descr_f = descr.get()->ob_type->tp_descr_get;
            if( descr_f && PyDescr_IsData( descr.get() ) )
            {
                PyObjectPtr res(
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
                return newref( item );
            }
        }

        // Non-data descriptor
        if( descr_f )
        {
            PyObjectPtr res(
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


static int
set_dynamic_attr( PyObject* obj, PyObject* name, PyObject* value )
{
    PyTypeObject* tp;
    PyObject* dict;
    PyObject** dictptr;
    PyObjectPtr descr;
    descrsetfunc descr_f;
    PyObjectPtr objptr( newref( obj ) );

    // The body of this loop is PyObject_GenericGetAttr, modified to
    // use smart pointers.
    while( objptr.get() != Py_None )
    {
        tp = Py_TYPE( objptr.get() );

        // Data desciptor
        descr_f = 0;
        descr = xnewref( _PyType_Lookup( tp, name ) );
        if( descr && PyType_HasFeature( descr.get()->ob_type, Py_TPFLAGS_HAVE_CLASS ) )
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
                tp->tp_name, PyString_AS_STRING( name )
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
static void
Nonlocals_clear( Nonlocals* self )
{
    Py_CLEAR( self->owner );
    Py_CLEAR( self->tracer );
}


static int
Nonlocals_traverse( Nonlocals* self, visitproc visit, void* arg )
{
    Py_VISIT( self->owner );
    Py_VISIT( self->tracer );
    return 0;
}


static void
Nonlocals_dealloc( Nonlocals* self )
{
    PyObject_GC_UnTrack( self );
    Nonlocals_clear( self );
    self->ob_type->tp_free( pyobject_cast( self ) );
}


static PyObject*
Nonlocals_repr( Nonlocals* self )
{
    PyObjectPtr pystr( PyObject_Str( self->owner ) );
    if( !pystr )
        return 0;
    return PyString_FromFormat(
        "%s[%s]",
        self->ob_type->tp_name,
        PyString_AS_STRING( pystr.get() )
    );
}


static PyObject*
Nonlocals_call( Nonlocals* self, PyObject* args, PyObject* kwargs )
{
    unsigned int level;
    static char* kwlist[] = { "level", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "I", kwlist, &level ) )
        return 0;
    unsigned int offset = 0;
    PyObjectPtr parentptr;
    PyObjectPtr objptr( newref( self->owner ) );
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
    PyObject* res = PyType_GenericNew( self->ob_type, 0, 0 );
    if( res )
    {
        Nonlocals* nl = reinterpret_cast<Nonlocals*>( res );
        nl->owner = objptr.newref();
        nl->tracer = xnewref( self->tracer );
    }
    return res;
}


static PyObject*
Nonlocals_getattro( Nonlocals* self, PyObject* name )
{
    PyObject* res = load_dynamic_attr( self->owner, name, self->tracer );
    if( !res && !PyErr_Occurred() )
        PyErr_Format(
            PyExc_AttributeError,
            "'%.50s' object has no attribute '%.400s'",
            self->ob_type->tp_name,
            PyString_AS_STRING( name )
        );
    return res;
}


static int
Nonlocals_setattro( Nonlocals* self, PyObject* name, PyObject* value )
{
    int res = set_dynamic_attr( self->owner, name, value );
    if( res < 0 && !PyErr_Occurred() )
        PyErr_Format(
            PyExc_AttributeError,
            "'%.50s' object has no attribute '%.400s'",
            self->ob_type->tp_name,
            PyString_AS_STRING( name )
        );
    return res;
}


static PyObject*
Nonlocals_getitem( Nonlocals* self, PyObject* key )
{
    if( !PyString_CheckExact( key ) )
        return py_expected_type_fail( key, "str" );
    PyObject* res = load_dynamic_attr( self->owner, key, self->tracer );
    if( !res && !PyErr_Occurred() )
        PyErr_SetString( PyExc_KeyError, PyString_AS_STRING( key ) );
    return res;
}


static int
Nonlocals_setitem( Nonlocals* self, PyObject* key, PyObject* value )
{
    if( !PyString_CheckExact( key ) )
    {
        py_expected_type_fail( key, "str" );
        return -1;
    }
    int res = set_dynamic_attr( self->owner, key, value );
    if( res < 0 && !PyErr_Occurred() )
        PyErr_SetString( PyExc_KeyError, PyString_AS_STRING( key ) );
    return res;
}


static int
Nonlocals_contains( Nonlocals* self, PyObject* key )
{
    if( !PyString_CheckExact( key ) )
    {
        py_expected_type_fail( key, "str" );
        return -1;
    }
    return test_dynamic_attr( self->owner, key );
}


static PyMappingMethods
Nonlocals_as_mapping = {
    (lenfunc)0,                             /*mp_length*/
    (binaryfunc)Nonlocals_getitem,          /*mp_subscript*/
    (objobjargproc)Nonlocals_setitem,       /*mp_ass_subscript*/
};


static PySequenceMethods
Nonlocals_as_sequence = {
    0,                                  /* sq_length */
    0,                                  /* sq_concat */
    0,                                  /* sq_repeat */
    0,                                  /* sq_item */
    0,                                  /* sq_slice */
    0,                                  /* sq_ass_item */
    0,                                  /* sq_ass_slice */
    (objobjproc)Nonlocals_contains,     /* sq_contains */
    0,                                  /* sq_inplace_concat */
    0,                                  /* sq_inplace_repeat */
};


PyTypeObject Nonlocals_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "dynamicscope.Nonlocals",               /* tp_name */
    sizeof( Nonlocals ),                    /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)Nonlocals_dealloc,          /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)Nonlocals_repr,               /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)&Nonlocals_as_sequence, /* tp_as_sequence */
    (PyMappingMethods*)&Nonlocals_as_mapping, /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)Nonlocals_call,            /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)Nonlocals_getattro,       /* tp_getattro */
    (setattrofunc)Nonlocals_setattro,       /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)Nonlocals_traverse,       /* tp_traverse */
    (inquiry)Nonlocals_clear,               /* tp_clear */
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


/*-----------------------------------------------------------------------------
| DynamicScope
|----------------------------------------------------------------------------*/
static PyObject*
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
        return py_expected_type_fail( f_locals, "mapping" );
    if( !PyDict_CheckExact( f_globals ) )
        return py_expected_type_fail( f_globals, "dict" );
    if( !PyDict_CheckExact( f_builtins ) )
        return py_expected_type_fail( f_builtins, "dict" );
    PyObject* self = PyType_GenericNew( type, 0, 0 );
    if( !self )
        return 0;
    DynamicScope* scope = reinterpret_cast<DynamicScope*>( self );
    scope->owner = newref( owner );
    scope->f_locals = newref( f_locals );
    scope->f_globals = newref( f_globals );
    scope->f_builtins = newref( f_builtins );
    if( change && change != Py_None )
        scope->change = newref( change );
    if( tracer && tracer != Py_None )
        scope->tracer = newref( tracer );
    return self;
}


static void
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


static int
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


static void
DynamicScope_dealloc( DynamicScope* self )
{
    PyObject_GC_UnTrack( self );
    DynamicScope_clear( self );
    self->ob_type->tp_free( pyobject_cast( self ) );
}


static PyObject*
DynamicScope_getitem( DynamicScope* self, PyObject* key )
{
    if( !PyString_CheckExact( key ) )
        return py_expected_type_fail( key, "str" );

    PyObject* res;

    // value from the override scope
    if( self->f_writes )
    {
        res = PyDict_GetItem( self->f_writes, key );
        if( res )
            return newref( res );
    }

    // 'self' magic
    if( strcmp( PyString_AS_STRING( key ), "self" ) == 0 )
        return newref( self->owner );

    // 'change' magic
    if( self->change && strcmp( PyString_AS_STRING( key ), "change" ) == 0 )
        return newref( self->change );

    // 'nonlocals' magic
    if( strcmp( PyString_AS_STRING( key ), "nonlocals" ) == 0 )
    {
        if( !self->f_nonlocals )
        {
            self->f_nonlocals = PyType_GenericNew( &Nonlocals_Type, 0, 0 );
            if( !self->f_nonlocals )
                return 0;
            Nonlocals* nl = reinterpret_cast<Nonlocals*>( self->f_nonlocals );
            nl->owner = newref( self->owner );
            nl->tracer = xnewref( self->tracer );
        }
        return newref( self->f_nonlocals );
    }

    // __scope__ magic
    if( strcmp( PyString_AS_STRING( key ), "__scope__" ) == 0 )
        return newref( pyobject_cast( self ) );

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
        return newref( res );

    // value from the builtin scope
    res = PyDict_GetItem( self->f_builtins, key );
    if( res )
        return newref( res );

    res = load_dynamic_attr( self->owner, key, self->tracer );
    if( res )
        return res;
    if( PyErr_Occurred() )
        return 0;

    PyErr_SetString( PyExc_KeyError, PyString_AS_STRING( key ) );
    return 0;
}


static int
DynamicScope_setitem( DynamicScope* self, PyObject* key, PyObject* value )
{
    if( !PyString_CheckExact( key ) )
    {
        py_expected_type_fail( key, "str" );
        return -1;
    }
    if( !value )
    {
        if( self->f_writes )
            return PyDict_DelItem( self->f_writes, key );
        PyErr_SetString( PyExc_KeyError, PyString_AS_STRING( key ) );
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


static int
DynamicScope_contains( DynamicScope* self, PyObject* key )
{
    if( !PyString_CheckExact( key ) )
    {
        py_expected_type_fail( key, "str" );
        return -1;
    }

    // value from the override scope
    if( self->f_writes && PyDict_GetItem( self->f_writes, key ) )
        return 1;

    // 'self' magic
    if( strcmp( PyString_AS_STRING( key ), "self" ) == 0 )
        return 1;

    // 'change' magic
    if( self->change && strcmp( PyString_AS_STRING( key ), "change" ) == 0 )
        return 1;

    // 'nonlocals' magic
    if( strcmp( PyString_AS_STRING( key ), "nonlocals" ) == 0 )
        return 1;

    // __scope__ magic
    if( strcmp( PyString_AS_STRING( key ), "__scope__" ) == 0 )
        return 1;

    // value from the local scope
    PyObjectPtr item( PyObject_GetItem( self->f_locals, key ) );
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


static PyMappingMethods
DynamicScope_as_mapping = {
    (lenfunc)0,                             /*mp_length*/
    (binaryfunc)DynamicScope_getitem,       /*mp_subscript*/
    (objobjargproc)DynamicScope_setitem,    /*mp_ass_subscript*/
};


static PySequenceMethods
DynamicScope_as_sequence = {
    0,                                  /* sq_length */
    0,                                  /* sq_concat */
    0,                                  /* sq_repeat */
    0,                                  /* sq_item */
    0,                                  /* sq_slice */
    0,                                  /* sq_ass_item */
    0,                                  /* sq_ass_slice */
    (objobjproc)DynamicScope_contains,  /* sq_contains */
    0,                                  /* sq_inplace_concat */
    0,                                  /* sq_inplace_repeat */
};


PyTypeObject DynamicScope_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "dynamicscope.DynamicScope",            /* tp_name */
    sizeof( DynamicScope ),                 /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)DynamicScope_dealloc,       /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)&DynamicScope_as_sequence, /* tp_as_sequence */
    (PyMappingMethods*)&DynamicScope_as_mapping, /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)DynamicScope_traverse,    /* tp_traverse */
    (inquiry)DynamicScope_clear,            /* tp_clear */
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
    (newfunc)DynamicScope_new,              /* tp_new */
    (freefunc)PyObject_GC_Del,              /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
dynamicscope_methods[] = {
    { 0 } // sentinel
};


PyMODINIT_FUNC
initdynamicscope( void )
{
    PyObject* mod = Py_InitModule( "dynamicscope", dynamicscope_methods );
    if( !mod )
        return;
    parent_str = PyString_FromString( "_parent" );
    if( !parent_str )
        return;
    dynamic_load_str = PyString_FromString( "dynamic_load" );
    if( !dynamic_load_str )
        return;
    UserKeyError = PyErr_NewException( "dynamicscope.UserKeyError", 0, 0 );
    if( !UserKeyError )
        return;
    if( PyType_Ready( &Nonlocals_Type ) < 0 )
        return;
    if( PyType_Ready( &DynamicScope_Type ) < 0 )
        return;
    PyModule_AddObject( mod, "UserKeyError", newref( UserKeyError ) );
    PyModule_AddObject( mod, "DynamicScope", newref( pyobject_cast( &DynamicScope_Type ) ) );
}
