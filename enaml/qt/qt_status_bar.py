#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.status_bar import ProxyStatusBar

from .QtWidgets import QStatusBar

from .qt_status_item import QtStatusItem
from .qt_widget import QtWidget


class QtStatusBar(QtWidget, ProxyStatusBar):
    """ A Qt implementation of an Enaml ProxyStatusBar.

    """
    #: A reference to the widget created by the proxy.
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
        self.set_size_grip_enabled(self.declaration.size_grip_enabled)

    def init_layout(self):
        """ Initialize the layout for the widget.

        """
        super(QtStatusBar, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, QtStatusItem):
                s_widget = child.status_widget()
                if s_widget is not None:
                    stretch = child.stretch()
                    if child.is_permanent():
                        widget.addPermanentWidget(s_widget, stretch)
                    else:
                        widget.addWidget(s_widget, stretch)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def refresh_item(self, item):
        """ A method invoked by a child status item.

        This method can be called when the widget for the item should
        be refreshed in the status bar.

        """
        w = self.widget
        s = item.status_widget()
        if s is not None:
            w.removeWidget(s)
            for index, child in enumerate(self.children()):
                if child is item:
                    stretch = item.stretch()
                    if item.is_permanent():
                        w.insertPermanentWidget(index, s, stretch)
                    else:
                        w.insertWidget(index, s, stretch)
                    s.show()
                    break

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtStatusBar.

        """
        super(QtStatusBar, self).child_added(child)
        if isinstance(child, QtStatusItem):
            w = self.widget
            s = child.status_widget()
            if s is not None:
                for index, item in enumerate(self.children()):
                    if child is item:
                        stretch = item.stretch()
                        if item.is_permanent():
                            w.insertPermanentWidget(index, s, stretch)
                        else:
                            w.insertWidget(index, s, stretch)
                        break

    def child_removed(self, child):
        """ Handle the child removed event for a QtStatusBar.

        """
        if isinstance(child, QtStatusItem):
            s = child.status_widget()
            if s is not None:
                self.widget.removeWidget(s)

    #--------------------------------------------------------------------------
    # ProxyStatusBar API
    #--------------------------------------------------------------------------
    def set_size_grip_enabled(self, enabled):
        """ Set the size grip enabled on the underlying widget.

        """
        self.widget.setSizeGripEnabled(enabled)

    def show_message(self, message, timeout=0):
        """ Show a temporary message in the status bar.

        """
        self.widget.showMessage(message, timeout)

    def clear_message(self):
        """ Clear any temporary message shown in the status bar.

        """
        self.widget.clearMessage()
