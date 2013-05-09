#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import os

#------------------------------------------------------------------------------
# Abstract Scope Listener
#------------------------------------------------------------------------------
class AbstractScopeListener(object):
    """ An abstract interface definition for scope listeners.

    A scope listener will be notified when an attribute is accessed via
    dynamic scoping.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def dynamic_load(self, obj, name, value):
        """ Called after the scope dynamically loads an attribute.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        name : string
            The name of the attribute loaded.

        value : object
            The value of the loaded attribute.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Dynamic Scope
#------------------------------------------------------------------------------
class DynamicScope(object):
    """ A custom mapping object that implements Enaml's dynamic scope.

    The __getitem__ method of this object is called when LOAD_NAME
    opcode is encountered in a code object which has been transformed
    by the Enaml compiler chain.

    Notes
    -----
    Strong references are kept to all objects passed to the constructor,
    so these scope objects should be created as needed and discarded in
    order to avoid unnecessary reference cycles.

    """
    def __init__(self, obj, f_locals, overrides, f_globals, listener):
        """ Initialize a DynamicScope.

        Parameters
        ----------
        obj : Declarative
            The Declarative object which owns the executing code.

        f_locals : dict
            The locals available to the executing code.

        overrides : dict
            A dict of objects which should have higher precedence than
            the f_locals.

        f_globals : dict
            The dict or globals to use for lookup up scope. This dict
            should have a '__builtins__' key.

        listener : DynamicScopeListener or None
            A listener which should be notified when a name is loaded
            via dynamic scoping.

        """
        self._obj = obj
        self._f_locals = f_locals
        self._overrides = overrides
        self._f_globals = f_globals
        self._listener = listener

    #: A sentinel used for testing for missing dict items.
    _sentinel = object()

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


#------------------------------------------------------------------------------
# Nonlocals
#------------------------------------------------------------------------------
class Nonlocals(object):
    """ An object which implements userland dynamic scoping.

    An instance of this object is made available with the `nonlocals`
    magic name in the scope of an expression.

    """
    def __init__(self, obj, listener):
        """ Initialize a nonlocal scope.

        Parameters
        ----------
        obj : Declarative
            The Declarative object which owns the executing code.

        listener : DynamicScopeListener or None
            A listener which should be notified when a name is loaded
            via dynamic scoping.

        """
        # avoid the call to the overidden __setattr__
        self.__dict__['_nls_obj'] = obj
        self.__dict__['_nls_listener'] = listener

    def __repr__(self):
        """ A pretty representation of the NonlocalScope.

        """
        return 'Nonlocals[%s]' % self._nls_obj

    def __call__(self, level=0):
        """ Get a new nonlocals object for the given offset.

        Parameters
        ----------
        level : int, optional
            The number of levels up the tree to offset. The default is
            zero and indicates no offset. The level must be >= 0.

        """
        if not isinstance(level, int) or level < 0:
            msg = ('The nonlocal scope level must be an int >= 0. '
                   'Got %r instead.')
            raise ValueError(msg % level)
        offset = 0
        target = self._nls_obj
        while target is not None and offset != level:
            target = target.parent
            offset += 1
        if offset != level:
            msg = 'Scope level %s is out of range'
            raise ValueError(msg % level)
        return Nonlocals(target, self._nls_listener)

    def __getattr__(self, name):
        """ A convenience method which allows accessing items in the
        scope via getattr instead of getitem.

        """
        try:
            return self.__getitem__(name)
        except KeyError:
            msg = "%s has no attribute '%s'" % (self, name)
            raise AttributeError(msg)

    def __setattr__(self, name, value):
        """ A convenience method which allows setting items in the
        scope via setattr instead of setitem.

        """
        if name == '_nls_obj' or name == '_nls_listener':
            self.__dict__[name] = value
        else:
            try:
                self.__setitem__(name, value)
            except KeyError:
                msg = "%s has no attribute '%s'" % (self, name)
                raise AttributeError(msg)

    def __getitem__(self, name):
        """ Lookup and return an item from the nonlocals.

        Parameters
        ----------
        name : string
            The name of the item to retrieve from the nonlocals.

        Raises
        ------
        KeyError
            The named item is not contained in the nonlocals.

        """
        parent = self._nls_obj
        while parent is not None:
            try:
                value = getattr(parent, name)
            except AttributeError:
                parent = parent.parent
            else:
                listener = self._nls_listener
                if listener is not None:
                    listener.dynamic_load(parent, name, value)
                return value
        raise KeyError(name)

    def __setitem__(self, name, value):
        """ Sets the value of the nonlocal.

        Parameters
        ----------
        name : string
            The name of the item to set in the nonlocals.

        value : object
            The value to set in the nonlocals.

        Raises
        ------
        KeyError
            The named item is not contained in the nonlocals.

        """
        parent = self._nls_obj
        while parent is not None:
            try:
                setattr(parent, name, value)
                return
            except AttributeError:
                parent = parent.parent
        raise KeyError(name)

    def __contains__(self, name):
        """ True if the name is in the nonlocals, False otherwise.

        """
        if isinstance(name, basestring):
            # Temporarily disable the listener during scope testing.
            listener = self._nls_listener
            self._nls_listener = None
            try:
                self.__getitem__(name)
            except KeyError:
                res = False
            else:
                res = True
            finally:
                self._nls_listener = listener
        else:
            res = False
        return res


# Debug hooks for nonlocals tracing
if os.environ.get('ENAML_DEBUG_DYNAMIC_SCOPE'):

    class DebugScopeTracer(object):

        def try_get(self, obj, name):
            pass

        def try_fail_get(self, obj, name, exc):
            pass

        def success_get(self, obj, name, val):
            pass

        def fail_get(self, first, last, name):
            pass

        def try_set(self, obj, name, val):
            pass

        def try_fail_set(self, obj, name, val, exc):
            pass

        def success_set(self, obj, name, val):
            pass

        def fail_set(self, first, last, name, val):
            pass

    __debug_tracer = DebugScopeTracer()

    def set_debug_scope_tracer(tracer):
        assert isinstance(tracer, DebugScopeTracer)
        global __debug_tracer
        __debug_tracer = tracer

    def get_debug_scope_tracer():
        return __debug_tracer


    class DebugDynamicScope(DynamicScope):

        def __getitem__(self, name):

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
            tracer = get_debug_scope_tracer()
            parent = last = self._obj
            while parent is not None:
                try:
                    tracer.try_get(parent, name)
                    value = getattr(parent, name)
                except AttributeError as e:
                    tracer.try_fail_get(parent, name, e)
                    last = parent
                    parent = parent.parent
                else:
                    tracer.success_get(parent, name, value)
                    listener = self._listener
                    if listener is not None:
                        listener.dynamic_load(parent, name, value)
                    return value
            tracer.fail_get(self._obj, last, name)
            raise KeyError(name)

    DynamicScope = DebugDynamicScope

    class DebugNonlocals(Nonlocals):

        def __getitem__(self, name):
            tracer = get_debug_scope_tracer()
            parent = last = self._nls_obj
            while parent is not None:
                try:
                    tracer.try_get(parent, name)
                    value = getattr(parent, name)
                except AttributeError as e:
                    tracer.try_fail_get(parent, name, e)
                    last = parent
                    parent = parent.parent
                else:
                    tracer.success_get(parent, name, value)
                    listener = self._nls_listener
                    if listener is not None:
                        listener.dynamic_load(parent, name, value)
                    return value
            tracer.fail_get(self._nls_obj, last, name)
            raise KeyError(name)

        def __setitem__(self, name, value):
            tracer = get_debug_scope_tracer()
            parent = last = self._nls_obj
            while parent is not None:
                try:
                    tracer.try_set(parent, name, value)
                    setattr(parent, name, value)
                    tracer.success_set(parent, name, value)
                    return
                except AttributeError as e:
                    tracer.try_fail_set(parent, name, value, e)
                    last = parent
                    parent = parent.parent
            tracer.fail_set(self._nls_obj, last, name, value)
            raise KeyError(name)

    Nonlocals = DebugNonlocals
