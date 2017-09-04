/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <Python.h>
#include "py23compat.h"


extern "C" {

/* Call a function with an optional locals mapping.

This allows Enaml to generate bytecode with the LOAD_GLOBAL opcode
replace with LOAD_NAME and use a custom locals mapping to implement
dynamic scoping. The code below is a slightly tweaked `function_call`
from Python's funcobject.c

*/
static PyObject*
call_func( PyObject* mod, PyObject* args )
{
    PyObject* func;
    PyObject* func_args;
    PyObject* func_kwargs;
    PyObject* func_locals = Py_None;

    if( !PyArg_UnpackTuple( args, "call_func", 3, 4, &func, &func_args, &func_kwargs, &func_locals ) )
    {
        return 0;
    }

    if( !PyFunction_Check( func ) )
    {
        PyErr_SetString( PyExc_TypeError, "function must be a Python function" );
        return 0;
    }

    if( !PyTuple_Check( func_args ) )
    {
        PyErr_SetString( PyExc_TypeError, "arguments must be a tuple" );
        return 0;
    }

    if( !PyDict_Check( func_kwargs ) )
    {
        PyErr_SetString( PyExc_TypeError, "keywords must be a dict" );
        return 0;
    }

    if( func_locals != Py_None && !PyMapping_Check( func_locals ) )
    {
        PyErr_SetString( PyExc_TypeError, "locals must be a mapping" );
        return 0;
    }
    if( func_locals == Py_None )
        func_locals = 0;

    PyObject** defaults = 0;
    Py_ssize_t num_defaults = 0;
    PyObject* argdefs = PyFunction_GET_DEFAULTS( func );
    if( ( argdefs ) && PyTuple_Check( argdefs ) )
    {
        defaults = &PyTuple_GET_ITEM( reinterpret_cast<PyTupleObject*>( argdefs ), 0 );
        num_defaults = PyTuple_Size( argdefs );
    }

    PyObject** keywords = 0;
    Py_ssize_t num_keywords = PyDict_Size( func_kwargs );
    if( num_keywords > 0 )
    {
        keywords = PyMem_NEW( PyObject*, 2 * num_keywords );
        if( !keywords )
        {
            PyErr_NoMemory();
            return 0;
        }
        Py_ssize_t i = 0;
        Py_ssize_t pos = 0;
        while( PyDict_Next( func_kwargs, &pos, &keywords[ i ], &keywords[ i + 1 ] ) )
            i += 2;
        num_keywords = i / 2;
        /* XXX This is broken if the caller deletes dict items! */
    }

#if PY_MAJOR_VERSION >= 3
    PyObject* result = PyEval_EvalCodeEx(
        PyFunction_GET_CODE( func ),
        PyFunction_GET_GLOBALS( func ),
        func_locals,
        &PyTuple_GET_ITEM( func_args, 0 ),
        PyTuple_Size( func_args ),
        keywords, num_keywords, defaults, num_defaults,
        NULL, PyFunction_GET_CLOSURE( func )
    );
#else
    PyObject* result = PyEval_EvalCodeEx(
        reinterpret_cast<PyCodeObject*>( PyFunction_GET_CODE( func ) ),
        PyFunction_GET_GLOBALS( func ),
        func_locals,
        &PyTuple_GET_ITEM( func_args, 0 ),
        PyTuple_Size( func_args ),
        keywords, num_keywords, defaults, num_defaults,
        PyFunction_GET_CLOSURE( func )
        );
#endif

    if( keywords )
        PyMem_DEL( keywords );

    return result;
 }

struct module_state {
    PyObject *error;
};


static PyMethodDef
funchelper_methods[] = {
    { "call_func", ( PyCFunction )call_func, METH_VARARGS,
      "call_func(func, args, kwargs[, locals])" },
    { 0 } // sentinel
};

#if PY_MAJOR_VERSION >= 3

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int funchelper_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int funchelper_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "funchelper",
        NULL,
        sizeof(struct module_state),
        funchelper_methods,
        NULL,
        funchelper_traverse,
        funchelper_clear,
        NULL
};

#else

#define GETSTATE(m) (&_state)
static struct module_state _state;

#endif

MOD_INIT_FUNC(funchelper)
{
#if PY_MAJOR_VERSION >= 3
    PyObject *mod = PyModule_Create(&moduledef);
    return mod;
#else
    PyObject* mod = Py_InitModule( "funchelper", funchelper_methods );
#endif
}

} // extern "C"

