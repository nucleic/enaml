#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Range, Coerced, observe

from enaml.core.declarative import d_
from enaml.layout.geometry import Size

from .container import Container
from .widget import Widget


class FlowItem(Widget):
    """ A widget which can be used as an item in a FlowArea.

    A FlowItem is a widget which can be used as a child of a FlowArea
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The preferred size of this flow item. This size will be used as
    #: the size of the item in the layout, bounded to the computed min
    #: and max size. A size of (-1, -1) indicates to use the widget's
    #: size hint as the preferred size.
    preferred_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: The alignment of this item in the direction orthogonal to the
    #: layout flow.
    align = d_(Enum('leading', 'trailing', 'center'))

    #: The stretch factor for this item in the flow direction, relative
    #: to other items in the same line. The default is zero which means
    #: that the item will not expand in the direction orthogonal to the
    #: layout flow.
    stretch = d_(Range(low=0, value=0))

    #: The stretch factor for this item in the orthogonal direction
    #: relative to other items in the layout. The default is zero
    #: which means that the item will not expand in the direction
    #: orthogonal to the layout flow.
    ortho_stretch = d_(Range(low=0, value=0))

    @property
    def flow_widget(self):
        """ A read only property which returns the flow widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the FlowItem.

        """
        snap = super(FlowItem, self).snapshot()
        snap['preferred_size'] = self.preferred_size
        snap['align'] = self.align
        snap['stretch'] = self.stretch
        snap['ortho_stretch'] = self.ortho_stretch
        return snap

    @observe(r'^(preferred_size|align|stretch|ortho_stretch)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(FlowItem, self).send_member_change(change)

