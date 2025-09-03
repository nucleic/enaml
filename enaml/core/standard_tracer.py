#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, atomref

from .alias import Alias
from .code_tracing import CodeTracer
from .subscription_observer import SubscriptionObserver


class StandardTracer(CodeTracer):
    """ A CodeTracer for tracing expressions which use Atom.

    This tracer maintains a running set of `traced_items` which are the
    (obj, name) pairs of atom items discovered during tracing.

    """
    __slots__ = ('owner', 'name', 'key', 'items')

    def __init__(self, owner, name):
        """ Initialize a StandardTracer.

        """
        self.owner = owner
        self.name = name
        self.key = '_[%s|trace]' % name
        self.items = set()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def trace_atom(self, obj: Atom, name: str):
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
        key = self.key
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
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will trace the object if it is an Atom instance.
        See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, Atom):
            self.trace_atom(obj, attr)

    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will trace the object if it is an Atom instance.
        See also: `CodeTracer.load_attr`.

        """
        if isinstance(obj, Atom):
            self.trace_atom(obj, attr)

    def call_function(self, func, argtuple: tuple, nargs: int):
        """ Called before the CALL opcode is executed.

        This will trace the func if it is the builtin `getattr` and the
        object is an Atom instance. See also: `CodeTracer.call_function`

        """
        if (func is getattr and (nargs == 2 or nargs == 3)):
            obj, attr = argtuple[0], argtuple[1]
            if isinstance(obj, Atom) and isinstance(attr, str):
                self.trace_atom(obj, attr)

    def return_value(self, value):
        """ Called before the RETURN_VALUE opcode is executed.

        This handler finalizes the subscription.

        """
        self.finalize()
