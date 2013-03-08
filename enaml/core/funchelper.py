#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import FunctionType
from ctypes import (
    pythonapi, py_object, c_int, c_size_t, Structure, ARRAY, c_void_p
)


PyEval_EvalCodeEx = pythonapi.PyEval_EvalCodeEx
PyEval_EvalCodeEx.restype = py_object
PyEval_EvalCodeEx.argtypes = [
    py_object,      # code object
    py_object,      # globals dict
    py_object,      # locals mapping
    c_void_p,       # args array (PyObject**)
    c_int,          # num args
    c_void_p,       # keywords array (PyObject**)
    c_int,          # num keywords
    c_void_p,       # defaults array (PyObject**)
    c_int,          # num defaults
    py_object,      # closure
]


class PyTupleObject(Structure):
    _fields_ = [
        ('ob_refcnt', c_size_t),
        ('ob_type', py_object),
        ('ob_size', c_size_t),
        ('ob_item', ARRAY(py_object, 1)),
    ]
OB_ITEM_OFFSET = PyTupleObject.ob_item.offset


def call_func(func, args, kwargs, f_locals=None):
    """ Call a function which has been modified by the Enaml compiler
    to support tracing and dynamic scoping.

    Parameters
    ----------
    func : types.FunctionType
        The Python function to call.

    args : tuple
        The tuple of arguments to pass to the function.

    kwargs : dict
        The dictionary of keywords to pass to the function.

    f_locals : mapping, optional
        An optional locals mapping to use with the function.

    Returns
    -------
    result : object
        The result of calling the function.

    """
    if not isinstance(func, FunctionType):
        raise TypeError('function must be a Python function')

    if not isinstance(args, tuple):
        raise TypeError('arguments must be a tuple')

    if not isinstance(kwargs, dict):
        raise TypeError('keywords must be a dict')

    if f_locals is None:
        f_locals = py_object()
    elif not hasattr(f_locals, '__getitem__'):
        raise TypeError('locals must be a mapping')

    num_args = len(args)
    args_array = c_void_p(id(args) + OB_ITEM_OFFSET)

    if kwargs:
        keywords = []
        for key, value in kwargs.iteritems:
            keywords.append(key)
            keywords.append(value)
        keywords = tuple(keywords)
        num_keywords = len(keywords) / 2
    else:
        keywords = ()
        num_keywords = 0
    keywords_array = c_void_p(id(keywords) + OB_ITEM_OFFSET)

    defaults = func.func_defaults or ()
    num_defaults = len(defaults)
    defaults_array = c_void_p(id(defaults) + OB_ITEM_OFFSET)

    result = PyEval_EvalCodeEx(
        func.func_code,
        func.func_globals,
        f_locals,
        args_array,
        num_args,
        keywords_array,
        num_keywords,
        defaults_array,
        num_defaults,
        func.func_closure
    )

    return result


# Use the faster version of `call_func` if it's available.
try:
    from enaml.extensions.funchelper import call_func
except ImportError:
    pass

