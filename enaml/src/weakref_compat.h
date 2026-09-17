/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2025, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/

#ifndef ENAML_WEAKREF_COMPAT_H
#define ENAML_WEAKREF_COMPAT_H

#include <Python.h>

#if PY_VERSION_HEX < 0x030D0000
// Can be removed when Python < 3.13 is no longer supported.
static inline int PyWeakref_GetRef(PyObject *ref, PyObject **pobj) {
    PyObject *obj = PyWeakref_GET_OBJECT(ref);
    *pobj = obj;
    Py_XINCREF(*pobj);
    return 1;
}
#endif

namespace enaml
{

inline PyObject*
weakref_get_object( PyObject* ref )
{
    PyObject* obj = nullptr;
#if PY_VERSION_HEX >= 0x030D0000
    int result = PyWeakref_GetRef( ref, &obj );
    if( result < 0 )
        return nullptr;
    if( result == 0 )
    {
        Py_INCREF( Py_None );
        return Py_None;
    }
    return obj;
#else
    obj = PyWeakref_GET_OBJECT( ref );
    if( obj == nullptr )
    {
        Py_INCREF( Py_None );
        return Py_None;
    }
    Py_INCREF( obj );
    return obj;
#endif
}

} // namespace enaml

#endif // ENAML_WEAKREF_COMPAT_H
