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

namespace enaml
{

inline PyObject*
weakref_get_object( PyObject* ref )
{
#if PY_VERSION_HEX >= 0x030D0000
    PyObject* obj = nullptr;
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
    return PyWeakref_GET_OBJECT( ref );
#endif
}

} // namespace enaml

#endif // ENAML_WEAKREF_COMPAT_H
