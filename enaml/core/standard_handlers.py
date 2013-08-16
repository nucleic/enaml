#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .dynamicscope import DynamicScope
from .expression_engine import ReadHandler, WriteHandler
from .funchelper import call_func
from .standard_inverter import StandardInverter
from .standard_tracer import StandardTracer


class StandardReadHandler(ReadHandler):
    """ An expression read handler for simple read semantics.

    This handler is used in conjuction with the standard '=' operator.

    """
    __slots__ = ('_func', '_scope_name')

    def __init__(self, func, scope_name):
        """ Initialize a StandardReadHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements simple read semantics.

        scope_name : str
            The key for the local scope in the storage map.

        """
        self._func = func
        self._scope_name = scope_name

    def __call__(self, owner, name, storage):
        """ Evaluate and return the expression value.

        """
        func = self._func
        f_globals = func.func_globals
        f_builtins = f_globals['__builtins__']
        f_locals = storage.get(self._scope_name) or {}
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins)
        return call_func(func, (), {}, scope)


class StandardWriteHandler(WriteHandler):
    """ An expression write handler for simple write semantics.

    This handler is used in conjuction with the standard '::' operator.

    """
    __slots__ = ('_func', '_scope_name')

    def __init__(self, func, scope_name):
        """ Initialize a StandardWriteHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements simple write semantics.

        scope_name : str
            The key for the local scope in the storage map.

        """
        self._func = func
        self._scope_name = scope_name

    def __call__(self, owner, name, storage, change):
        """ Write the change to the expression.

        """
        func = self._func
        f_globals = func.func_globals
        f_builtins = f_globals['__builtins__']
        f_locals = storage.get(self._scope_name) or {}
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins, change)
        call_func(func, (), {}, scope)


class StandardTracedReadHandler(ReadHandler):
    """ An expression read handler which traces code execution.

    This handler is used in conjuction with the standard '<<' operator.

    """
    __slots__ = ('_func', '_scope_name')

    def __init__(self, func, scope_name):
        """ Initialize a StandardTracedReadHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements traced read semantics.

        scope_name : str
            The key for the local scope in the storage map.

        """
        self._func = func
        self._scope_name = scope_name

    def __call__(self, owner, name, storage):
        """ Evaluate and return the expression value.

        """
        func = self._func
        f_globals = func.func_globals
        f_builtins = f_globals['__builtins__']
        f_locals = storage.get(self._scope_name) or {}
        tr = StandardTracer(owner, name, storage)
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins, None, tr)
        return call_func(func, (tr,), {}, scope)


class StandardInvertedWriteHandler(WriteHandler):
    """ An expression writer which writes an expression value.

    This handler is used in conjuction with the standard '>>' operator.

    """
    __slots__ = ('_func', '_scope_name')

    def __init__(self, func, scope_name):
        """ Initialize a StandardInvertedWriteHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements inverted write semantics.

        scope_name : str
            The key for the local scope in the storage map.

        """
        self._func = func
        self._scope_name = scope_name

    def __call__(self, owner, name, storage, change):
        """ Write the change to the expression.

        """
        func = self._func
        f_globals = func.func_globals
        f_builtins = f_globals['__builtins__']
        f_locals = storage.get(self._scope_name) or {}
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins)
        inverter = StandardInverter(scope)
        return call_func(func, (inverter, change['value']), {}, scope)
