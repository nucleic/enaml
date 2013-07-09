#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, Range, Coerced, Typed, ForwardTyped, observe, set_default
)

from enaml.core.declarative import d_
from enaml.layout.geometry import Box

from .frame import Frame, ProxyFrame, Border
from .flow_item import FlowItem


class ProxyFlowArea(ProxyFrame):
    """ The abstract definition of a proxy FlowArea object.

    """
    #: A reference to the FlowArea declaration.
    declaration = ForwardTyped(lambda: FlowArea)

    def set_direction(self, direction):
        raise NotImplementedError

    def set_align(self, align):
        raise NotImplementedError

    def set_horizontal_spacing(self, spacing):
        raise NotImplementedError

    def set_vertical_spacing(self, spacing):
        raise NotImplementedError

    def set_margins(self, margins):
        raise NotImplementedError


class FlowArea(Frame):
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
    margins = d_(Coerced(Box, (10, 10, 10, 10)))

    #: A FlowArea expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyFlowArea object.
    proxy = Typed(ProxyFlowArea)

    def flow_items(self):
        """ Get the flow item children defined on this area.

        """
        return [c for c in self.children if isinstance(c, FlowItem)]

    #--------------------------------------------------------------------------
    # Default Handlers
    #--------------------------------------------------------------------------
    def _default_border(self):
        """ Get the default border for the flow area.

        The default value matches the default for Qt's QScrollArea.

        """
        return Border(style='styled_panel', line_style='sunken')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('direction', 'align', 'horizontal_spacing', 'vertical_spacing',
        'margins'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(FlowArea, self)._update_proxy(change)
