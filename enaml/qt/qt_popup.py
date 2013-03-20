#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from PyQt4.QtCore import Qt, QSize, pyqtSignal
from PyQt4.QtGui import QFrame, QLayout

from enaml.widgets.popup import ProxyPopup

from .q_popup_widget import QPopupWidget
from .qt_widget import QtWidget


class QtPopup(QtWidget, ProxyPopup):
    """ A Qt implementation of an Enaml ProxyPopup.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QPopupWidget)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QPopup widget.

        """
        self.widget = QPopupWidget(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtPopup, self).init_widget()
        d = self.declaration
        if -1 not in d.initial_size:
            self.set_initial_size(d.initial_size)
        if d.anchor:
            self.set_anchor(d.anchor)
        if d.arrow:
            self.set_arrow(d.arrow)
        if d.radius:
            self.set_radius(d.radius)
        if d.relative_pos:
            self.set_relative_pos(d.relative_pos)
        self.widget.closed.connect(self.on_closed)

    def init_layout(self):
        """ Initialize the widget layout.

        """
        super(QtPopup, self).init_layout()
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
    # ProxyPopup API
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.close()

    def set_anchor(self, anchor):
        """ Set the size of the anchor

        """
        self.widget.setAnchor(anchor)

    def set_radius(self, radius):
        """ Set the size of the popup corner radii

        """
        self.widget.setRadius(radius)

    def set_arrow(self, arrow):
        """ Set the size of the anchor arrow

        """
        self.widget.setArrowSize(arrow)

    def set_relative_pos(self, relative_pos):
        """ Set the relative position of anchor with respect to the popup's
        bounds

        """
        self.widget.setRelativePos(relative_pos)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        if -1 in size:
            return
        self.widget.resize(QSize(*size))
