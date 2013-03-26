#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Backwards compatibility tracer for dealing with Traits models.

New code should use Atom models instead of traits.

"""
from traits.api import HasTraits, Disallow, TraitListObject, TraitDictObject

from .standard_tracer import StandardTracer


class TraitsTracer(StandardTracer):
    """ A CodeTracer for tracing expressions which use Traits.

    This tracer maintains a running set of `traced_traits` which are the
    (obj, name) pairs of traits items discovered during tracing.

    """
    __slots__ = 'traced_traits'

    def __init__(self):
        """ Initialize a TraitsTracer.

        """
        super(TraitsTracer, self).__init__()
        self.traced_traits = set()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _trace_trait(self, obj, name):
        """ Add the trait object and name pair to the traced items.

        Parameters
        ----------
        obj : HasTraits
            The traits object owning the attribute.

        name : str
            The trait name to for which to bind a handler.

        """
        # Traits will happily force create a trait for things which aren't
        # actually traits. This tries to avoid most of that when possible.
        trait = obj.trait(name)
        if trait is not None and trait.trait_type is not Disallow:
            self.traced_traits.add((obj, name))

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will trace the object if it is a HasTraits instance.
        See also: `AbstractScopeListener.dynamic_load`.

        """
        super(TraitsTracer, self).dynamic_load(obj, attr, value)
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will trace the object if it is a HasTraits instance.
        See also: `CodeTracer.dynamic_load`.

        """
        super(TraitsTracer, self).load_attr(obj, attr)
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL_FUNCTION opcode is executed.

        This will trace the func is the builtin `getattr` and the object
        is a HasTraits instance. See also: `CodeTracer.call_function`

        """
        super(TraitsTracer, self).call_function(func, argtuple, argspec)
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            if isinstance(obj, HasTraits) and isinstance(attr, basestring):
                self._trace_trait(obj, attr)

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This will trace the object if it is a `TraitListObject` or a
        `TraitDictObject`. See also: `CodeTracer.get_iter`.

        """
        super(TraitsTracer, self).binary_subscr(obj, idx)
        if isinstance(obj, (TraitListObject, TraitDictObject)):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        This will trace the object if it is a `TraitListObject`
        See also: `CodeTracer.get_iter`.

        """
        super(TraitsTracer, self).get_iter(obj)
        if isinstance(obj, TraitListObject):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)
