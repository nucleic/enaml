#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QPointF

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
        self.set_arrow_size(d.arrow_size)
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
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_closed(self):
        """ The signal handler for the 'closed' signal.

        This method will destroy the declarative object.

        """
        self.declaration.destroy()

    #--------------------------------------------------------------------------
    # ProxyBubbleView API
    #--------------------------------------------------------------------------
    def set_anchor(self, anchor):
        """ Set the anchor location on the underlying widget.

        """
        self.widget.setAnchor(ANCHOR[anchor])

    def set_arrow_size(self, size):
        """ Set the size of the arrow on the underlying widget.

        """
        self.widget.setArrowSize(size)

    def set_relative_pos(self, relative_pos):
        """ Set the relatitve anchor position of the underlying widget.

        """
        self.widget.setRelativePos(QPointF(*relative_pos))
