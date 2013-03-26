#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.bubble_view import ProxyBubbleView

from .q_bubble_view import QBubbleView
from .qt_widget import QtWidget


ANCHOR = {
    'left': QBubbleView.AnchorLeft,
    'right': QBubbleView.AnchorRight,
    'top': QBubbleView.AnchorTop,
    'bottom': QBubbleView.AnchorBottom,
}


class QtBubbleView(QtWidget, ProxyBubbleView):
    """ A Qt implementation of an Enaml ProxyBubbleView.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QBubbleView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QBubbleView widget.

        """
        self.widget = QBubbleView(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtBubbleView, self).init_widget()
        d = self.declaration
        self.set_anchor(d.anchor)
        self.set_arrow(d.arrow)
        self.set_radius(d.radius)
        self.set_relative_pos(d.relative_pos)
        self.widget.closed.connect(self.on_closed)

    def init_layout(self):
        """ Initialize the widget layout.

        """
        super(QtBubbleView, self).init_layout()
        self.widget.setCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Find and return the central widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The central widget defined for this widget, or None if one
            is not defined.

        """
        d = self.declaration.central_widget()
        if d is not None:
            return d.proxy.widget or None

    def on_closed(self):
        """ The signal handler for the 'closed' signal.

        This method will fire the 'closed' event on the declaration.

        """
        self.declaration._handle_close()

    #--------------------------------------------------------------------------
    # ProxyBubbleView API
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.close()

    def set_anchor(self, anchor):
        """ Set the size of the anchor

        """
        self.widget.setAnchor(ANCHOR[anchor])

    def set_radius(self, radius):
        """ Set the size of the QBubbleView corner radii

        """
        self.widget.setRadius(radius)

    def set_arrow(self, arrow):
        """ Set the size of the anchor arrow

        """
        self.widget.setArrowSize(arrow)

    def set_relative_pos(self, relative_pos):
        """ Set the relative position of anchor with respect to the QBubbleView's
        bounds

        """
        self.widget.setRelativePos(relative_pos)
