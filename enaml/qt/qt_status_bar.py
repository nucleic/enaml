#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

from PyQt4.QtGui import QStatusBar

from atom.api import Typed

from enaml.widgets.status_bar import ProxyStatusBar

from .qt_widget import QtWidget
from .qt_permanent_status_widgets import QtPermanentStatusWidgets
from .qt_transient_status_widgets import QtTransientStatusWidgets

class QtStatusBar(QtWidget, ProxyStatusBar):
    """ A Qt implementation of an Enaml StatusBar.

    """
    #: A reference to the widget created by the proxy
    widget = Typed(QStatusBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QStatusBar widget.

        """
        self.widget = QStatusBar(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtStatusBar, self).init_widget()
        d = self.declaration
        self.set_grip_enabled(d.grip_enabled)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtStatusBar.

        """
        if isinstance(child, (QtPermanentStatusWidgets, QtTransientStatusWidgets)):
            for subchild in child.children():
                self.widget.removeWidget(subchild.widget)

    def child_added(self, child):
        """ Handle the child added event for a QtStatusBar.

        """
        widget = self.widget
        if isinstance(child, QtPermanentStatusWidgets):
            for subchild in child.children():
                widget.addPermanentWidget(subchild.widget)
        elif isinstance(child, QtTransientStatusWidget):
            for subchild in child.children():
                widget.insertWidget(child.widget)

    #--------------------------------------------------------------------------
    # ProxyStatusBar API
    #--------------------------------------------------------------------------
    def set_grip_enabled(self, grip_enabled):
        """ Set the size grip enabled on the underlying widget.

        """
        self.widget.setSizeGripEnabled(grip_enabled)

    def show_message(self, message, timeout=None):
        """ Show a message on the status bar

        Parameters
        ----------
        message: Str
            The message to show
        timeout: Int
            How long to show the message in seconds

        """
        self.widget.showMessage(message, timeout)

    def clear_message(self):
        """ Clear the current message on the status bar

        """
        self.widget.clearMessage()