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


/* This is a dynamic scope lookup function. It reproduces the behavior
of PyObject_GenericGetAttr on every ancestor in the tree until it finds
an attribute with the given name. If the tree is exhausted, the provided
exception class is raised. */
static PyObject*
dynamic_lookup( PyObject* mod, PyObject* args )
{
    PyObject* _owner;
    PyObject* _name;
    PyObject* _exc_class;
    if( !PyArg_ParseTuple( args, "OSO", &_owner, &_name, &_exc_class ) )
        return 0;

    PyObjectPtr ownerptr( newref( _owner ) );
    PyObjectPtr nameptr( newref( _name ) );
    PyObjectPtr descr;
    PyObjectPtr dict;

    PyTypeObject* owner_type;
    PyObject** dictptr;

    descrgetfunc descr_f;
    Py_ssize_t dictoffset;

    while( ownerptr.get() != Py_None )
    {
        owner_type = Py_TYPE( ownerptr.get() );

        // Data descriptor
        descr_f = 0;
        descr = xnewref( _PyType_Lookup( owner_type, nameptr.get() ) );
        if( descr && PyType_HasFeature( descr.get()->ob_type, Py_TPFLAGS_HAVE_CLASS ) )
        {
            descr_f = descr.get()->ob_type->tp_descr_get;
            if( descr_f && PyDescr_IsData( descr.get() ) )
                return descr_f( descr.get(), ownerptr.get(), pyobject_cast( owner_type ) );
        }

        // Instance dictionary
        dict = 0;
        dictoffset = owner_type->tp_dictoffset;
        if( dictoffset )
        {
            if( dictoffset < 0 )
            {
                Py_ssize_t tsize = reinterpret_cast<PyVarObject*>( ownerptr.get() )->ob_size;
                if( tsize < 0 )
                    tsize = -tsize;
                size_t size = _PyObject_VAR_SIZE( owner_type, tsize );
                dictoffset += static_cast<long>( size );
            }
            dictptr = reinterpret_cast<PyObject**>(
                reinterpret_cast<char*>( ownerptr.get() ) + dictoffset
            );
            dict = xnewref( *dictptr );
        }
        if( dict )
        {
            PyObject* res = PyDict_GetItem( dict.get(), nameptr.get() );
            if( res )
                return newref( res );
        }

        // Non-data descriptor
        if( descr_f )
            return descr_f( descr.get(), ownerptr.get(), pyobject_cast( owner_type ) );

        if( descr )
            return descr.release();

        ownerptr = PyObject_GenericGetAttr( ownerptr.get(), parent_str );
        if( !ownerptr )
            return 0;
    }

    PyErr_Format( _exc_class, "'%s'", PyString_AS_STRING( nameptr.get() ) );
    return 0;
}


static PyMethodDef
dynamiclookup_methods[] = {
    { "dynamic_lookup", ( PyCFunction )dynamic_lookup, METH_VARARGS,
      "dynamic_lookup(owner, name)" },
    { 0 } // sentinel
};


PyMODINIT_FUNC
initdynamiclookup( void )
{
    PyObject* mod = Py_InitModule( "dynamiclookup", dynamiclookup_methods );
    if( !mod )
        return;

    parent_str = PyString_FromString( "_parent" );
}
