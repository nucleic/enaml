#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Range, Coerced, observe, set_default

from enaml.core.declarative import d_
from enaml.layout.geometry import Box

from .constraints_widget import ConstraintsWidget
from .flow_item import FlowItem


class FlowArea(ConstraintsWidget):
    """ A widget which lays out its children in flowing manner, wrapping
    around at the end of the available space.

    """
    #: The flow direction of the layout.
    direction = d_(Enum(
        'left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top'
    ))

    #: The alignment of a line of items within the layout.
    align = d_(Enum('leading', 'trailing', 'center', 'justify'))

    #: The amount of horizontal space to place between items.
    horizontal_spacing = d_(Range(low=0, value=10))

    #: The amount of vertical space to place between items.
    vertical_spacing = d_(Range(low=0, value=10))

    #: The margins to use around the outside of the flow area.
    margins = d_(Coerced(Box, factory=lambda: Box(10, 10, 10, 10)))

    #: A FlowArea expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    @property
    def flow_items(self):
        """ A read only property which returns the flow items.

        """
        isinst = isinstance
        target = FlowItem
        return [child for child in self.children if isinst(child, target)]

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the FlowArea.

        """
        snap = super(FlowArea, self).snapshot()
        snap['direction'] = self.direction
        snap['align'] = self.align
        snap['horizontal_spacing'] = self.horizontal_spacing
        snap['vertical_spacing'] = self.vertical_spacing
        snap['margins'] = self.margins
        return snap

    @observe(r'^(direction|align|horizontal_spacing|vertical_spacing|'
             r'margins)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(FlowArea, self).send_member_change(change)

