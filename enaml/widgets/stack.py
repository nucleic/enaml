#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Atom, Enum, Int, Range, Typed, ForwardTyped, observe, set_default
)

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .stack_item import StackItem


class Transition(Atom):
    """ An object representing an animated transition.

    Once a transition is created, it should be considered read-only.

    """
    #: The type of transition effect to use.
    type = Enum('slide', 'wipe', 'iris', 'fade', 'crossfade')

    #: The direction of the transition effect. Some transition types
    #: will ignore the direction if it doesn't apply to the effect.
    direction = Enum(
        'left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top'
    )

    #: The duration of the transition, in milliseconds.
    duration = Range(low=0, value=250)


class ProxyStack(ProxyConstraintsWidget):
    """ The abstract definition of a proxy Stack object.

    """
    #: A reference to the Stack declaration.
    declaration = ForwardTyped(lambda: Stack)

    def set_index(self, index):
        raise NotImplementedError

    def set_transition(self, transition):
        raise NotImplementedError


class Stack(ConstraintsWidget):
    """ A component which displays its children as a stack of widgets,
    only one of which is visible at a time.

    """
    #: The index of the visible widget in the stack. The widget itself
    #: does not provide a means to changing this index. That control
    #: must be supplied externally. If the given index falls outside of
    #: the range of stack items, no widget will be visible.
    index = d_(Int(0))

    #: The item transition to use when changing between stack items.
    transition = d_(Typed(Transition))

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyStack widget.
    proxy = Typed(ProxyStack)

    def stack_items(self):
        """ Get the stack items defined on the stack

        """
        return [c for c in self.children if isinstance(c, StackItem)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('index', 'transition'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(Stack, self)._update_proxy(change)
