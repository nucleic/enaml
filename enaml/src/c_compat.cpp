/*-----------------------------------------------------------------------------
| Copyright (c) 2017-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include <cppy/cppy.h>

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif


namespace
{


/* The following three functions are taken from CPython import.c implementation
*/
void
update_code_filenames(PyCodeObject *co, PyObject *oldname, PyObject *newname)
{
    PyObject *constants, *tmp;
    Py_ssize_t i, n;

    if (PyUnicode_Compare(co->co_filename, oldname))
        return;

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

void
update_compiled_module(PyCodeObject *co, PyObject *newname)
{
    PyObject *oldname;

    if (PyUnicode_Compare(co->co_filename, newname) == 0)
        return;

    oldname = co->co_filename;
    Py_INCREF(oldname);
    update_code_filenames(co, oldname, newname);
    Py_DECREF(oldname);
}

/*End of the end extracted from CPython import.c*/

PyObject *
_imp__fix_co_filename_impl(PyObject *module, PyObject* args, PyObject* kwargs )
{
    PyObject* code;
    PyObject* path;
    static char *kwlist[] = { "code", "path", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "OO", kwlist, &code, &path ) )
        return 0;
    if( !PyCode_Check( code ) )
        return cppy::type_error( code, "CodeType" );
    if( !PyUnicode_Check( path ) )
        return cppy::type_error( path, "str" );
    PyCodeObject* cc = reinterpret_cast<PyCodeObject*>( code );
    update_compiled_module(cc, path);

    Py_RETURN_NONE;
}


// Module definition
int
c_compat_modexec( PyObject *mod )
{
    return 0;
}

static PyMethodDef
c_compat_methods[] = {
    {"_fix_co_filename", ( PyCFunction )_imp__fix_co_filename_impl,
     METH_VARARGS | METH_KEYWORDS, "Fix co_filename of a code object"},
    { 0 } // sentinel
};


PyModuleDef_Slot c_compat_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( c_compat_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "c_compat",
        "c_compat extension module",
        0,
        c_compat_methods,
        c_compat_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


PyMODINIT_FUNC PyInit_c_compat( void )
{
    return PyModuleDef_Init( &moduledef );
}
