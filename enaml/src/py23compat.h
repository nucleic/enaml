/*-----------------------------------------------------------------------------
| Copyright (c) 2014, Nucleic
|
| Distributed under the terms of the BSD 3-Clause License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
#pragma once

#include <Python.h>

#if PY_MAJOR_VERSION >= 3

#define Py23Str_Check PyUnicode_Check
#define Py23Str_CheckExact PyUnicode_CheckExact
#define Py23Str_AS_STRING PyUnicode_AsUTF8
#define Py23Str_FromString PyUnicode_FromString
#define Py23Str_InternFromString PyUnicode_InternFromString
#define Py23Str_InternInPlace PyUnicode_InternInPlace
#define Py23Str_FromFormat PyUnicode_FromFormat
#define Py23Bytes_Check PyBytes_Check
#define Py23Bytes_AS_STRING PyBytes_AS_STRING
#define Py23Bytes_FromStringAndSize PyBytes_FromStringAndSize
#define Py23Int_Check PyLong_Check
#define Py23Int_FromLong PyLong_FromLong
#define Py23Int_AsLong PyLong_AsLong
#define Py23Number_Int PyNumber_Long
#define Py23Int_AsSsize_t PyLong_AsSsize_t
#define Py23Int_FromSsize_t PyLong_FromSsize_t

#define INITERROR return NULL
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)

#else

#define Py23Str_Check PyString_Check
#define Py23Str_CheckExact PyString_CheckExact
#define Py23Str_AS_STRING PyString_AS_STRING
#define Py23Str_FromString PyString_FromString
#define Py23Str_InternFromString PyString_InternFromString
#define Py23Str_InternInPlace PyString_InternInPlace
#define Py23Str_FromFormat PyString_FromFormat
#define Py23Bytes_Check PyString_Check
#define Py23Bytes_AS_STRING PyString_AS_STRING
#define Py23Bytes_FromStringAndSize PyString_FromStringAndSize
#define Py23Int_Check( ob ) ( PyInt_Check( ob ) || PyLong_Check( ob ) )
#define Py23Int_FromLong PyInt_FromLong
#define Py23Int_AsLong PyInt_AsLong
#define Py23Number_Int PyNumber_Int
#define Py23Int_AsSsize_t PyInt_AsSsize_t
#define Py23Int_FromSsize_t PyInt_FromSsize_t

#define INITERROR return
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)

#endif
