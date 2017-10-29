#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from past.builtins import basestring
from atom.api import Atom, atomref

from .alias import Alias
from .code_tracing import CodeTracer
from ..compat import IS_PY3


class SubscriptionObserver(object):
    """ An observer object which manages a tracer subscription.

    """
    __slots__ = ('ref', 'name')

    def __init__(self, owner, name):
        """ Initialize a SubscriptionObserver.

        Parameters
        ----------
        owner : Declarative
            The declarative owner of interest.

        name : string
            The name to which the operator is bound.

        """
        self.ref = atomref(owner)
        self.name = name

    def __bool__(self):
        """ The notifier is valid when it has an internal owner.

        The atom observer mechanism will remove the observer when it
        tests boolean False.

        """
        return bool(self.ref)

    if not IS_PY3:
        __nonzero__ = __bool__
        del __bool__

    def __call__(self, change):
        """ The handler for the change notification.

        This will be invoked by the Atom observer mechanism when the
        item which is being observed changes.

        """
        if self.ref:
            owner = self.ref()
            engine = owner._d_engine
            if engine is not None:
                engine.update(owner, self.name)


class StandardTracer(CodeTracer):
    """ A CodeTracer for tracing expressions which use Atom.

    This tracer maintains a running set of `traced_items` which are the
    (obj, name) pairs of atom items discovered during tracing.

    """
    __slots__ = ('owner', 'name', 'items')

    def __init__(self, owner, name):
        """ Initialize a StandardTracer.

        """
        self.owner = owner
        self.name = name
        self.items = set()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def trace_atom(self, obj, name):
        """ Add the atom object and name pair to the traced items.

        Parameters
        ----------
        obj : Atom
            The atom object owning the attribute.

        name : string
            The member name for which to bind a handler.

        """
        if obj.get_member(name) is not None:
            self.items.add((obj, name))
        else:
            alias = getattr(type(obj), name, None)
            if isinstance(alias, Alias):
                alias_obj, alias_attr = alias.resolve(obj)
                if alias_attr:
                    self.trace_atom(alias_obj, alias_attr)

    def finalize(self):
        """ Finalize the tracing process.

        This method will discard the old observer and attach a new
        observer to the traced dependencies.

        """
        owner = self.owner
        name = self.name
        key = '_[%s|trace]' % name
        storage = owner._d_storage

        # invalidate the old observer so that it can be collected
        old_observer = storage.get(key)
        if old_observer is not None:
            old_observer.ref = None

        # create a new observer and subscribe it to the dependencies
        if self.items:
            observer = SubscriptionObserver(owner, name)
            storage[key] = observer
            for obj, d_name in self.items:
                obj.observe(d_name, observer)

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will trace the object if it is an Atom instance.
        See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, Atom):
            self.trace_atom(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will trace the object if it is an Atom instance.
        See also: `CodeTracer.load_attr`.

        """
        if isinstance(obj, Atom):
            self.trace_atom(obj, attr)

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL_FUNCTION opcode is executed.

        This will trace the func if it is the builtin `getattr` and the
        object is an Atom instance. See also: `CodeTracer.call_function`

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            if isinstance(obj, Atom) and isinstance(attr, basestring):
                self.trace_atom(obj, attr)

    def return_value(self, value):
        """ Called before the RETURN_VALUE opcode is executed.

        This handler finalizes the subscription.

        """
        self.finalize()
