#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QObject, QEvent, QSize

from atom.api import Typed

from enaml.widgets.dock_area import ProxyDockArea, docklayout, docksplit, tabbed

from .q_dock_area import QDockArea, DockItem, DockSplitter, DockTabs
from .qt_constraints_widget import QtConstraintsWidget


ORIENT = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


def convert_layout(layout, parent=None):
    """ Convert an Enaml docklayout into a Qt DockLayout.

    """
    if isinstance(layout, docksplit):
        qorient = ORIENT[layout.orientation]
        ql = DockSplitter(parent=parent, orientation=qorient, sizes=layout.sizes[:])
        for item in layout.items:
            if isinstance(item, docklayout):
                ql.items.append(convert_layout(item, ql))
            else:
                qitem = item.proxy.widget
                ql.items.append(DockItem(parent=ql, item=qitem))
    elif isinstance(layout, tabbed):
        ql = DockTabs(parent=parent)
        for item in layout.items:
            qitem = item.proxy.widget
            ql.items.append(DockItem(parent=ql, item=qitem))
    else:
        raise TypeError(type(layout).__name__)
    return ql


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
        qlayout = convert_layout(d.resolve_layout())
        self.widget.layout().setDockLayout(qlayout)
        self.dock_filter = DockFilter(self)
        self.widget.installEventFilter(self.dock_filter)

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
