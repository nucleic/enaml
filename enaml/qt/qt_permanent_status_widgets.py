#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

from PyQt4.QtGui import QStatusBar

from atom.api import Typed

from .qt_toolkit_object import QtToolkitObject
from .qt_widget import QtWidget

from enaml.widgets.permanent_status_widgets import ProxyPermanentStatusWidgets


class QtPermanentStatusWidgets(QtToolkitObject, ProxyPermanentStatusWidgets):
    """ A Qt implementation of the permanent children of an Enaml StatusBar

    """
    #: A reference to the widget created by the proxy
    widget = Typed(QStatusBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ This is a virtual widget - return the parent status bar widget

        """
        self.widget = self.parent_widget()

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtPermanentStatusWidgets, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, QtWidget):
                widget.addPermanentWidget(child.widget)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtPermanentStatusWidgets.

        """
        if isinstance(child, QtWidget):
            self.widget.removeWidget(child.widget)

    def child_added(self, child):
        """ Handle the child added event for a QtPermanentStatusWidgets.
        
        """
        if isinstance(child, QtWidget):
            for index, dchild in enumerate(self.children()):
                if dchild is child:
                    self.widget.insertPermanentWidget(index, child.widget)
                    break

