#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, Event, Int, Tuple, Typed, ForwardTyped, observe, set_default,
)

from enaml.application import deferred_call
from enaml.core.declarative import d_

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyBubbleView(ProxyWidget):
    """ The abstract definition of a proxy BubbleView object.

    """
    #: A reference to the BubbleView declaration.
    declaration = ForwardTyped(lambda: BubbleView)

    def setup_window(self):
        raise NotImplementedError

    def set_anchor(self, anchor):
        raise NotImplementedError

    def set_radius(self, radius):
        raise NotImplementedError

    def set_arrow(self, arrow):
        raise NotImplementedError

    def set_relative_pos(self, relative_pos):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class BubbleView(Widget):
    """ A BubbleView popup widget.

    This widget implements a popup style with rounded corners and an
    arrow anchoring it to an underlying widget. Useful for transient
    dialogs.

    """
    #: An enum which indicates the which side of the parent will be used
    #: as the anchor point. The default value is 'bottom'
    anchor = d_(Enum('bottom', 'left', 'right', 'top'))

    #: The size in pixels of the x and y radii of the BubbleView's rounded
    #: corners
    radius = d_(Int(10))

    #: The size of the BubbleView's anchoring arrow
    arrow = d_(Int(20))

    #: The position of the anchor relative to the BubbleView parent widget's
    #: bounds
    relative_pos = d_(Tuple(float, (0.5, 0.5)))

    #: An event fired when the BubbleView is closed.
    closed = d_(Event(), writable=False)

    #: BubbleViews are invisible by default.
    visible = set_default(False)

    #: A reference to the ProxyBubbleView object.
    proxy = Typed(ProxyBubbleView)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Get the central widget defined on the BubbleView.

        The last `Container` child of the window is the central widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    def close(self):
        """ Send the 'close' action to the client widget.

        """
        if self.proxy_is_active:
            self.proxy.close()

    def show(self):
        """ Show the BubbleView.

        This is a reimplemented parent class method which will init
        and build the BubbleView hierarchy if needed.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        super(BubbleView, self).show()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('anchor', 'radius', 'arrow', 'relative_pos'))
    def _update_proxy(self, change):
        """ Update the ProxyBubbleView when the BubbleView data changes.

        """
        # The superclass handler implementation is sufficient.
        super(BubbleView, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _handle_close(self):
        """ Handle the close event from the proxy widget.

        """
        self.visible = False
        self.closed()
        deferred_call(self.destroy)
