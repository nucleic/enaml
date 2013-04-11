#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QObject, QEvent, QSize

from atom.api import Typed

from enaml.widgets.dock_area import ProxyDockArea

from .q_dock_area import QDockArea
from .qt_constraints_widget import QtConstraintsWidget


class DockFilter(QObject):

    def __init__(self, owner):
        super(DockFilter, self).__init__()
        self.owner = owner
        self.sh = QSize()

    def eventFilter(self, obj, event):
        owner = self.owner
        if owner is not None and event.type() == QEvent.LayoutRequest:
            hint = obj.sizeHint()
            if hint != self.sh:
                self.sh = hint
                owner.size_hint_updated()
        return False


class QtDockArea(QtConstraintsWidget, ProxyDockArea):
    """ A Qt implementation of an Enaml DockArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDockArea)

    dock_filter = Typed(DockFilter)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockArea widget.

        """
        self.widget = QDockArea(self.parent_widget())

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtDockArea, self).init_layout()
        d = self.declaration
        self.widget.setDockLayout(d.layout)
        self.dock_filter = DockFilter(self)
        self.widget.installEventFilter(self.dock_filter)

    def destroy(self):
        self.widget.removeEventFilter(self.dock_filter)
        del self.dock_filter
        super(QtDockArea, self).destroy()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockArea.

        """
        super(QtDockArea, self).child_added(child)

    def child_removed(self, child):
        """ Handle the child removed event for a QtDockArea.

        """
        super(QtDockArea, self).child_removed(child)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QtDockArea.

        """
        self.size_hint_updated()
