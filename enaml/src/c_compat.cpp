/*-----------------------------------------------------------------------------
| Copyright (c) 2017, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/

#include "pythonhelpersex.h"
#include "py23compat.h"

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif

using namespace PythonHelpers;

PyObject* _fix_co_filename;

/* The following three functions are taken from CPython import.c implementation
*/
static void
update_code_filenames(PyCodeObject *co, PyObject *oldname, PyObject *newname)
{
    PyObject *constants, *tmp;
    Py_ssize_t i, n;

    #if PY_MAJOR_VERSION >= 3
    if (PyUnicode_Compare(co->co_filename, oldname))
        return;
    #else
    if (!_PyString_Eq(co->co_filename, oldname))
        return;
    #endif

    tmp = co->co_filename;
    co->co_filename = newname;
    Py_INCREF(co->co_filename);
    Py_DECREF(tmp);

    constants = co->co_consts;
    n = PyTuple_GET_SIZE(constants);
    for (i = 0; i < n; i++) {
        tmp = PyTuple_GET_ITEM(constants, i);
        if (PyCode_Check(tmp))
            update_code_filenames((PyCodeObject *)tmp,
                                  oldname, newname);
    }
}

static void
update_compiled_module(PyCodeObject *co, PyObject *newname)
{
    PyObject *oldname;

    #if PY_MAJOR_VERSION >= 3
    if (PyUnicode_Compare(co->co_filename, newname) == 0)
        return;
    #else
    if (!_PyString_Eq(co->co_filename, newname) == 0)
        return;
    #endif

    oldname = co->co_filename;
    Py_INCREF(oldname);
    update_code_filenames(co, oldname, newname);
    Py_DECREF(oldname);
}

/*End of the end extracted from CPython import.c*/

static PyObject *
_imp__fix_co_filename_impl(PyObject *module, PyObject* args, PyObject* kwargs )
{
    PyObject* code;
    PyObject* path;
    static char *kwlist[] = { "code", "path", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "OO", kwlist, &code, &path ) )
        return 0;
    if( !PyCode_Check( code ) )
        return py_expected_type_fail( code, "CodeType" );
    if( !Py23Str_Check( path ) )
        return py_expected_type_fail( path, "str" );
    PyCodeObject* cc = reinterpret_cast<PyCodeObject*>( code );
    update_compiled_module(cc, path);

    Py_RETURN_NONE;
}



struct module_state {
    PyObject *error;
};

static PyMethodDef
c_compat_methods[] = {
    {"_fix_co_filename", ( PyCFunction )_imp__fix_co_filename_impl,
     METH_VARARGS | METH_KEYWORDS, "Fix co_filename of a code object"},
    { 0 } // sentinel
};

#if PY_MAJOR_VERSION >= 3

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int c_compat_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int c_compat_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "c_compat",
        NULL,
        sizeof(struct module_state),
        c_compat_methods,
        NULL,
        c_compat_traverse,
        c_compat_clear,
        NULL
};

#else

#define GETSTATE(m) (&_state)
static struct module_state _state;

#endif

MOD_INIT_FUNC(c_compat)
{
#if PY_MAJOR_VERSION >= 3
    PyObjectPtr mod( xnewref( PyModule_Create(&moduledef) ) );
#else
    PyObjectPtr mod( xnewref( Py_InitModule( "c_compat", c_compat_methods ) ) );
#endif
    if( !mod )
        INITERROR;
    PyObject* mod_dict = PyModule_GetDict( mod.get() );


    PyObjectPtr up( mod.getattr( "_fix_co_filename" ) );
    if( !up )
        INITERROR;
    _fix_co_filename = up.release();

#if PY_MAJOR_VERSION >= 3
    return mod.get();
#endif
}
