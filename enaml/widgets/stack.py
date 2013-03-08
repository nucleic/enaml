#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Dict, Int, observe, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget
from .stack_item import StackItem


class Stack(ConstraintsWidget):
    """ A component which displays its children as a stack of widgets,
    only one of which is visible at a time.

    """
    #: The index of the visible widget in the stack. The widget itself
    #: does not provide a means to changing this index. That control
    #: must be supplied externally. If the given index falls outside of
    #: the range of stack items, no widget will be visible.
    index = d_(Int(0))

    #: The transition to use when change between stack items.
    #: XXX Document the supported transitions.
    transition = d_(Dict())

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    @property
    def stack_items(self):
        """ A read only property which returns the list of stack items.

        """
        isinst = isinstance
        target = StackItem
        return [child for child in self.children if isinst(child, target)]

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the control.

        """
        snap = super(Stack, self).snapshot()
        snap['index'] = self.index
        snap['transition'] = self.transition
        return snap

    @observe(r'^(index|transition)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Stack, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_index_changed(self, content):
        """ Handle the `index_changed` action from the client widget.

        """
        with self.loopback_guard('index'):
            self.index = content['index']

