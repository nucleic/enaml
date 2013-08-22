#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager
from types import FunctionType

from .byteplay import (
    Code, LOAD_NAME, LOAD_FAST, STORE_NAME, STORE_FAST, DELETE_NAME,
    DELETE_FAST
)
from .code_tracing import inject_tracing, inject_inversion
from .standard_handlers import (
    StandardReadHandler, StandardWriteHandler, StandardTracedReadHandler,
    StandardInvertedWriteHandler
)


def optimize_locals(codelist):
    """ Optimize the given code object for fast locals access.

    All STORE_NAME opcodes will be replaced with STORE_FAST. Names which
    are stored and then loaded via LOAD_NAME are rewritten to LOAD_FAST
    and DELETE_NAME is rewritten to DELETE_FAST. This transformation is
    applied in-place.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    """
    fast_locals = set()
    for idx, (op, op_arg) in enumerate(codelist):
        if op == STORE_NAME:
            fast_locals.add(op_arg)
            codelist[idx] = (STORE_FAST, op_arg)
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_NAME and op_arg in fast_locals:
            codelist[idx] = (LOAD_FAST, op_arg)
        elif op == DELETE_NAME and op_arg in fast_locals:
            codelist[idx] = (DELETE_FAST, op_arg)


def op_simple(code, scope_key, f_globals):
    """ The default Enaml operator function for the `=` operator.

    """
    bp_code = Code.from_code(code)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    new_code = bp_code.to_code()
    func = FunctionType(new_code, f_globals)
    reader = StandardReadHandler(func=func, scope_key=scope_key)
    return (reader, None)


def op_notify(code, scope_key, f_globals):
    """ The default Enaml operator function for the `::` operator.

    """
    bp_code = Code.from_code(code)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    new_code = bp_code.to_code()
    func = FunctionType(new_code, f_globals)
    writer = StandardWriteHandler(func=func, scope_key=scope_key)
    return (None, writer)


def op_subscribe(code, scope_key, f_globals):
    """ The default Enaml operator function for the `<<` operator.

    """
    bp_code = Code.from_code(code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_tracing(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[tracer]',) + bp_code.args
    new_code = bp_code.to_code()
    func = FunctionType(new_code, f_globals)
    reader = StandardTracedReadHandler(func=func, scope_key=scope_key)
    return (reader, None)


def op_update(code, scope_key, f_globals):
    """ The default Enaml operator function for the `>>` operator.

    """
    bp_code = Code.from_code(code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_inversion(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[inverter]', '_[value]') + bp_code.args
    new_code = bp_code.to_code()
    func = FunctionType(new_code, f_globals)
    writer = StandardInvertedWriteHandler(func=func, scope_key=scope_key)
    return (None, writer)


def op_delegate(code, scope_key, f_globals):
    """ The default Enaml operator function for the `:=` operator.

    """
    reader = op_subscribe(code, scope_key, f_globals)[0]
    writer = op_update(code, scope_key, f_globals)[1]
    return (reader, writer)


DEFAULT_OPERATORS = {
    '=': op_simple,
    '::': op_notify,
    '>>': op_update,
    '<<': op_subscribe,
    ':=': op_delegate,
}


#: The internal stack of operators pushed by the operator context.
__operator_stack = []


@contextmanager
def operator_context(ops, union=False):
    """ Push operators onto the stack for the duration of the context.

    Parameters
    ----------
    ops : dict
        The dictionary of operators to push onto the stack.

    union : bool, optional
        Whether or to union the operators with the existing operators
        on the top of the stack. The default is False.

    """
    if union:
        new = dict(__get_operators())
        new.update(ops)
        ops = new
    __operator_stack.append(ops)
    yield
    __operator_stack.pop()


def __get_default_operators():
    """ Set the default operators.

    This function is for internal use only and may disappear at any time.

    """
    return DEFAULT_OPERATORS


def __set_default_operators(ops):
    """ Set the default operators.

    This function is for internal use only and may disappear at any time.

    """
    global DEFAULT_OPERATORS
    DEFAULT_OPERATORS = ops


def __get_operators():
    """ An internal routine used to get the operators for a given class.

    Operators resolution is performed in the following order:

        - The operators on the top of the operators stack.
        - The default operators via __get_default_operators()

    This function may disappear at any time.

    """
    if __operator_stack:
        return __operator_stack[-1]
    return __get_default_operators()
