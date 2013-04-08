#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.dock_item import ProxyDockItem

from .q_dock_item import QDockItem
from .qt_widget import QtWidget


class QtDockItem(QtWidget, ProxyDockItem):
    """ A Qt implementation of an Enaml ProxyDockItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDockItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockItem widget.

        """
        self.widget = QDockItem(self.parent_widget())

    def init_widget(self):
        """ Initialize the state of the underlying widget.

        """
        super(QtDockItem, self).init_widget()
        d = self.declaration
        self.set_title(d.title)
        self.set_stretch(d.stretch)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtDockItem, self).init_layout()
        self.widget.setDockWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_widget(self):
        """ Find and return the dock widget child for this widget.

        """
        d = self.declaration.dock_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockItem.

        """
        super(QtDockItem, self).child_added(child)

    def child_removed(self, child):
        """ Handle the child added event for a QtDockItem.

        """
        super(QtDockItem, self).child_removed(child)

    #--------------------------------------------------------------------------
    # ProxyDockItem API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        self.widget.setTitle(title)

    def set_stretch(self, stretch):
        """ Set the stretch factor for the underlyling widget.

        """
        sp = self.widget.sizePolicy()
        sp.setHorizontalStretch(stretch)
        sp.setVerticalStretch(stretch)
        self.widget.setSizePolicy(sp)
