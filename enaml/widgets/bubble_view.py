#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, Int, Tuple, Typed, ForwardTyped, observe, set_default,
)

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyBubbleView(ProxyWidget):
    """ The abstract definition of a proxy BubbleView object.

    """
    #: A reference to the BubbleView declaration.
    declaration = ForwardTyped(lambda: BubbleView)

    def set_anchor(self, anchor):
        raise NotImplementedError

    def set_arrow_size(self, size):
        raise NotImplementedError

    def set_relative_pos(self, relative_pos):
        raise NotImplementedError


class BubbleView(Widget):
    """ A BubbleView popup widget.

    This widget implements a transient popup view which is useful for
    conveying contextual configuration data and notification.

    A BubbleView is a single-use widget and is automatically destroyed
    when it is closed. The view automatically closes itself when it
    loses focus or the user clicks outside of the view area.

    """
    #: The side of the parent to use as the anchor point.
    anchor = d_(Enum('bottom', 'left', 'right', 'top'))

    #: The size of the BubbleView's anchoring arrow in pixels.
    arrow_size = d_(Int(20))

    #: The position of the anchor relative to the BubbleView's parent.
    relative_pos = d_(Tuple(float, (0.5, 0.5)))

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

    def show(self):
        """ Show the BubbleView.

        This is a reimplemented method which will intitialize the proxy
        tree before showing the view.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        super(BubbleView, self).show()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('anchor', 'arrow_size', 'relative_pos'))
    def _update_proxy(self, change):
        """ Update the ProxyBubbleView when the BubbleView data changes.

        """
        # The superclass handler implementation is sufficient.
        super(BubbleView, self)._update_proxy(change)
