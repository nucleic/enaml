# ------------------------------------------------------------------------------
# Copyright (c) 2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
from collections.abc import Iterable
from enaml.core.declarative import Declarative
from enaml.core._dynamicscope import _DynamicScope, UserKeyError


class DynamicScope(_DynamicScope):
    """_DynamicScope is a C++ class which exposes the following attributes:

    _owner
    _change
    _f_writes
    _f_locals
    _f_globals
    _f_builtins

    """
    def __iter__(self):
        """Iterate the keys available in the dynamicscope."""
        keys = _generate_keys(self)
        return _filter_keys(keys)

    def keys(self):
        """Iterate the keys available in the dynamicscope."""
        return iter(self)

    def values(self):
        """Iterate the values available in the dynamicscope."""
        return (self[key] for key in self)

    def items(self):
        """Iterate the (key, value) pairs available in the dynamicscope."""
        return ((key, self[key]) for key in self)

    def update(self, scope):
        """Update the dynamicscope with a mapping of items."""
        for key, value in scope.items():
            self[key] = value


def _generate_keys(scope: DynamicScope):
    """ Generate *all* of the attributes names available from a dynamic scope.

    Parameters
    ----------
    scope: DynamicScope
        The scope object of interest

    Yields
    ------
    All of the attribute names accesible by code running in a dynamic scope,
    in the order that they would be found during expression execution.

    """
    # The first names to yield are any assigned local variables.
    if scope._f_writes is not None:
        yield from scope._f_writes

    # The next name to yield is the magic `self` object.
    yield 'self'

    # The next name to yield is the magic `change` object, if it exists.
    if scope._change is not None:
        yield 'change'

    # Next, yield the names from the real local scope.
    yield from scope._f_locals

    # Then, the module globals.
    yield from scope._f_globals

    # Then, the normal builtins.
    yield from scope._f_builtins

    # Lastly, traverse the parent hiearchy and yield their attribute names.
    owner = scope._owner
    while owner is not None:
        yield from dir(owner)
        owner = owner._parent


def _filter_keys(keys: Iterable[str]):
    """ Filter an iterable of keys for duplicates and private names.

    Parameters
    ----------
    keys: Iterable[string]
        The keys to filter.

    Yields
    ------
    The input keys filtered for private `_` names and duplicates.

    """
    seen = set()
    for key in keys:
        if key.startswith('_') or key in seen:
            continue
        seen.add(key)
        yield key

