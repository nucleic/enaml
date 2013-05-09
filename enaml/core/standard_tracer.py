#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom

from .code_tracing import CodeTracer
from .dynamic_scope import AbstractScopeListener


class StandardTracer(CodeTracer):
    """ A CodeTracer for tracing expressions which use Atom.

    This tracer maintains a running set of `traced_items` which are the
    (obj, name) pairs of atom items discovered during tracing.

    """
    __slots__ = 'traced_items'

    def __init__(self):
        """ Initialize a StandardTracer.

        """
        self.traced_items = set()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _trace_atom(self, obj, name):
        """ Add the atom object and name pair to the traced items.

        Parameters
        ----------
        obj : Atom
            The atom object owning the attribute.

        name : string
            The member name to for which to bind a handler.

        """
        if obj.get_member(name) is not None:
            self.traced_items.add((obj, name))

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will trace the object if it is an Atom instance.
        See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, Atom):
            self._trace_atom(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will trace the object if it is an Atom instance.
        See also: `CodeTracer.load_attr`.

        """
        if isinstance(obj, Atom):
            self._trace_atom(obj, attr)

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
                self._trace_atom(obj, attr)


AbstractScopeListener.register(StandardTracer)
