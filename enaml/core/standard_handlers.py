#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .expression_engine import ReadHandler, WriteHandler
from .funchelper import call_func


class StandardReadHandler(ReadHandler):
    """ An expression read handler for simple read semantics.

    This handler is used in conjuction with the standard '=' operator.

    """
    __slots__ = ('_func', '_scope_factory')

    def __init__(self, func, scope_factory):
        """ Initialize a SimpleReadHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements simple read semantics.

        scope_factory: ReadScopeFactory
            A factory which will be called to retrieve the read scope
            for evaluation.

        """
        self._func = func
        self._scope_factory = scope_factory

    def __call__(self, owner, name, storage):
        """ Evaluate and return the expression value.

        """
        scope = self._scope_factory(owner, storage)
        return call_func(self._func, (), {}, scope)


class StandardWriteHandler(WriteHandler):
    """ An expression write handler for simple write semantics.

    This handler is used in conjuction with the standard '::' operator.

    """
    __slots__ = ('_func', '_scope_factory')

    def __init__(self, func, scope_factory):
        """ Initialize a SimpleWriteHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements simple write semantics.

        scope_factory: WriteScopeFactory
            A factory which will be called to retrieve the write scope
            for evaluation.

        """
        self._func = func
        self._scope_factory = scope_factory

    def __call__(self, owner, name, storage, change):
        """ Write the change to the expression.

        """
        scope = self._scope_factory(owner, storage, change)
        call_func(self._func, (), {}, scope)


class StandardTracedReadHandler(ReadHandler):
    """ An expression read handler which traces code execution.

    """
    __slots__ = ('_func', '_scope_factory', '_tracer_factory')

    def __init__(self, func, scope_factory, tracer_factory):
        """ Initialize a TracedReadHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements traced read semantics.

        scope_factory: TracedReadScopeFactory
            A factory which will be called to retrieve the traced read
            scope for evaluation.

        tracer_factory : CodeTracerFactory
            A factory which will be called to retrive a code tracer
            for evaluation.

        """
        self._func = func
        self._scope_factory = scope_factory
        self._tracer_factory = tracer_factory

    def __call__(self, owner, name, storage):
        """ Evaluate and return the expression value.

        """
        tracer = self._tracer_factory(owner, name, storage)
        scope = self._scope_factory(owner, storage, tracer)
        return call_func(self._func, (tracer,), {}, scope)


class StandardInvertedWriteHandler(WriteHandler):
    """ An expression writer which writes an expression value.

    """
    __slots__ = ('_func', '_scope_factory', '_inverter_factory')

    def __init__(self, func, scope_factory, inverter_factory):
        """ Initialize a TracedReadHandler.

        Parameters
        ----------
        func : FunctionType
            A function object which implements traced read semantics.

        scope_factory: ReadScopeFactory
            A factory which will be called to retrieve the read scope
            for evaluation.

        inverter_factory : CodeInverterFactory
            A factory which will be called to retrive a code tracer
            for evaluation.

        """
        self._func = func
        self._scope_factory = scope_factory
        self._inverter_factory = inverter_factory

    def __call__(self, owner, name, storage, change):
        """ Write the change to the expression.

        """
        inverter = self._inverter_factory(owner, name, storage)
        scope = self._scope_factory(owner, storage)
        return call_func(self._func, (inverter, change['value']), {}, scope)
