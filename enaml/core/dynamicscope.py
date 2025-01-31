# ------------------------------------------------------------------------------
# Copyright (c) 2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
from functools import partial
from itertools import chain, repeat
from enaml.core.declarative import Declarative
from enaml.core._dynamicscope import _DynamicScope, UserKeyError


def d_iter(owner: Declarative):
    """Iterate attribute names of the declarative and it's ancestors.

    Parameters
    ----------
    owner: Declarative
        The declarative to walk.

    Yields
    ------
    name: string
        The attribute name

    """
    while owner is not None:
        for name in dir(owner):
            yield name
        owner = owner._parent


def include_key(key: str, used: set) -> bool:
    """Filter function to determine whether the key should be included in the
    dynamicscope's iter results.

    Parameters
    ----------
    key: string
        The scope key.
    used: set[str]
        The set of keys already seen.

    Returns
    -------
    result: bool
        Whether the key should be included.
    """
    if key.startswith("_") or key in used:
        return False
    used.add(key)
    return True


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
        used = set()
        fwrites_it = iter(self._f_writes or ())
        self_it = repeat("self", 1)
        change_it = repeat("change", 1 if self._change else 0)
        flocals_it = iter(self._f_locals)
        fglobals_it = iter(self._f_globals)
        fbuiltins_it = iter(self._f_builtins)
        fields_it = d_iter(self._owner)
        unique_scope_keys = partial(include_key, used=used)
        return filter(
            unique_scope_keys,
            chain(
                fwrites_it,
                self_it,
                change_it,
                flocals_it,
                fglobals_it,
                fbuiltins_it,
                fields_it,
            )
        )

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
