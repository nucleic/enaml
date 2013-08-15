#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .factories import (
    ReadScopeFactory, WriteScopeFactory, TracedReadScopeFactory,
    CodeTracerFactory, CodeInverterFactory,
)
from .standard_inverter import StandardInverter
from .standard_scopes import (
    StandardReadScope, StandardWriteScope, StandardTracedReadScope
)
from .standard_tracer import StandardTracer


class StandardReadScopeFactory(ReadScopeFactory):
    """ The standard implementation of a ReadScopeFactory.

    This factory generates dynamic scopes which are suitable for use
    with the standard '=' and '>>' operator semantics.

    """
    __slots__ = ('_scope_name', '_f_globals')

    def __init__(self, scope_name, f_globals):
        """ Initialize a StandardReadScopeFactory.

        Parameters
        ----------
        scope_name : str or None
            The key for the local scope mapping in the shared storage
            map for the declarative object, or None if no local scope
            is available.

        f_globals : dict
            The globals dictionary for the generated scope.

        """
        self._scope_name = scope_name
        self._f_globals = f_globals

    def __call__(self, owner, storage):
        """ Create and return an implementation of the scope.

        """
        if self._scope_name is not None:
            f_locals = storage[self._scope_name]
        else:
            f_locals = {}
        return StandardReadScope(owner, f_locals, self._f_globals)


class StandardWriteScopeFactory(WriteScopeFactory):
    """ The standard implementation of a WriteScopeFactory.

    This factory generates dynamic scopes which are suitable for use
    with the standard '::' operator semantics.

    """
    __slots__ = ('_scope_name', '_f_globals')

    def __init__(self, scope_name, f_globals):
        """ Initialize a StandardWriteScopeFactory.

        Parameters
        ----------
        scope_name : str or None
            The key for the local scope mapping in the shared storage
            map for the declarative object, or None if no local scope
            is available.

        f_globals : dict
            The globals dictionary for the generated scope.

        """
        self._scope_name = scope_name
        self._f_globals = f_globals

    def __call__(self, owner, storage, change):
        """ Create and return an implementation of the scope.

        """
        if self._scope_name is not None:
            f_locals = storage[self._scope_name]
        else:
            f_locals = {}
        return StandardWriteScope(owner, change, f_locals, self._f_globals)


class StandardTracedReadScopeFactory(TracedReadScopeFactory):
    """ The standard implementation of a TracedReadScopeFactory.

    This factory generates dynamic scopes which are suitable for use
    with the standard '<<' operator semantics.

    """
    __slots__ = ('_scope_name', '_f_globals')

    def __init__(self, scope_name, f_globals):
        """ Initialize a StandardTracedReadScopeFactory.

        Parameters
        ----------
        scope_name : str or None
            The key for the local scope mapping in the shared storage
            map for the declarative object, or None if no local scope
            is available.

        f_globals : dict
            The globals dictionary for the generated scope.

        """
        self._scope_name = scope_name
        self._f_globals = f_globals

    def __call__(self, owner, storage, tracer):
        """ Create and return an implementation of the scope.

        """
        if self._scope_name is not None:
            f_locals = storage[self._scope_name]
        else:
            f_locals = {}
        return StandardTracedReadScope(owner, tracer, f_locals, self._f_globals)


class StandardCodeTracerFactory(CodeTracerFactory):
    """ The standard implementation of a CodeTracerFactory.

    This factory generates code tracers which are suitable for use
    with the standard '<<' operator semantics.

    """
    __slots__ = ()

    def __call__(self, owner, name, storage):
        """ Create and return a code tracer.

        """
        return StandardTracer(owner, name, storage)


class StandardCodeInverterFactory(CodeInverterFactory):
    """ The standard implementation of a CodeInverterFactory.

    This factory generates code tracers which are suitable for use
    with the standard '>>' operator semantics.

    """
    __slots__ = ()

    def __call__(self, owner, name, storage):
        """ Create and return a code inverter.

        """
        return StandardInverter(owner)
