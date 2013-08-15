#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .dynamiclookup import dynamic_lookup


#: A sentinel object used for testing for missing dict items.
_scope_sentinel = object()


class Nonlocals(object):
    pass


class DynamicLookupError(LookupError):
    pass


class StandardReadScope(object):
    """

    """
    __slots__ = ('_owner', '_f_locals', '_f_globals')

    def __init__(self, owner, f_locals, f_globals):
        """ Initialize a StandardReadScope.

        Parameters
        ----------
        owner : Declarative
            The declarative owner of the execution context.

        f_locals : mapping
            A mapping object containing the local scope.

        f_globals : dict
            The dict of globals for the scope. It must have a
            '__builtins__' key.

        """
        self._owner = owner
        self._f_locals = f_locals
        self._f_globals = f_globals

    def __getitem__(self, name):
        """ Lookup and return an item from the scope.

        Parameters
        ----------
        name : string
            The name of the item to retrieve from the scope.

        Raises
        ------
        KeyError
            The named item is not contained in the scope.

        """
        if name == 'self':
            return self._owner
        if name == 'nonlocals':
            return Nonlocals(self._owner)
        s = _scope_sentinel
        v = self._f_locals.get(name, s)
        if v is not s:
            return v
        v = self._f_globals.get(name, s)
        if v is not s:
            return v
        v = self._f_globals['__builtins__'].get(name, s)
        if v is not s:
            return v
        try:
            return dynamic_lookup(self._owner, name, DynamicLookupError)
        except DynamicLookupError:
            raise KeyError(name)
        except KeyError:
            raise RuntimeError


def __getitem__(self, name):
    """ Lookup and return an item from the scope.

    Parameters
    ----------
    name : string
        The name of the item to retrieve from the scope.

    Raises
    ------
    KeyError
        The named item is not contained in the scope.

    """
    s = self._sentinel
    v = self._overrides.get(name, s)
    if v is not s:
        return v
    v = self._f_locals.get(name, s)
    if v is not s:
        return v
    v = self._f_globals.get(name, s)
    if v is not s:
        return v
    v = self._f_globals['__builtins__'].get(name, s)
    if v is not s:
        return v
    parent = self._obj
    while parent is not None:
        try:
            value = getattr(parent, name)
        except AttributeError:
            parent = parent.parent
        else:
            listener = self._listener
            if listener is not None:
                listener.dynamic_load(parent, name, value)
            return value
    raise KeyError(name)

def __setitem__(self, name, value):
    """ Set an item in the scope.

    Parameters
    ----------
    name : string
        The name of the item to set in the scope.

    value : object
        The object to set in the scope.

    """
    # This method is required for pdb to function properly.
    self._overrides[name] = value

def __contains__(self, name):
    """ Returns True if the name is in scope, False otherwise.

    """
    # This method is required for pdb to function properly.
    if isinstance(name, basestring):
        # Temporarily disable the listener during scope testing.
        listener = self._listener
        self._listener = None
        try:
            self.__getitem__(name)
        except KeyError:
            res = False
        else:
            res = True
        finally:
            self._listener = listener
    else:
        res = False
    return res


class StandardWriteScope(object):
    """

    """


class StandardTracedReadScope(object):
    """

    """

