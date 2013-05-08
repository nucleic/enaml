#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QObject, QEvent, QSize, QTimer
from PyQt4.QtGui import QTabWidget

from atom.api import Typed

from enaml.widgets.dock_area import ProxyDockArea

from .docking.dock_manager import DockManager
from .docking.q_dock_area import QDockArea
from .qt_constraints_widget import QtConstraintsWidget
from .qt_dock_item import QtDockItem


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


class DockFilter(QObject):
    """ A simple event filter used by the QtDockArea.

    This event filter listens for LayoutRequest events on the dock
    area widget, and will send a size_hint_updated notification to
    the constraints system when the dock area size hint changes.

    The notifications are collapsed on a single shot timer so that
    the dock area geometry can fully settle before being snapped
    by the constraint layout engine.

    """
    def __init__(self, owner):
        super(DockFilter, self).__init__()
        self._owner = owner
        self._size_hint = QSize()
        self._pending = False
        self._timer = timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.onNotify)

    def onNotify(self):
        self._owner.size_hint_updated()
        self._pending = False

    def eventFilter(self, obj, event):
        if not self._pending and event.type() == QEvent.LayoutRequest:
            hint = obj.sizeHint()
            if hint != self._size_hint:
                self._size_hint = hint
                self._timer.start(0)
                self._pending = True
        return False


class QtDockArea(QtConstraintsWidget, ProxyDockArea):
    """ A Qt implementation of an Enaml DockArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDockArea)

    #: The docking manager which will drive the dock area.
    manager = Typed(DockManager)

    #: The event filter which listens for layout requests.
    dock_filter = Typed(DockFilter)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockArea widget.

        """
        self.widget = QDockArea(self.parent_widget())
        self.manager = DockManager(self.widget)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDockArea, self).init_widget()
        self.set_tab_position(self.declaration.tab_position)

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtDockArea, self).init_layout()
        manager = self.manager
        for item in self.dock_items():
            manager.add_item(item)
        manager.apply_layout(self.declaration.layout)
        self.dock_filter = dock_filter = DockFilter(self)
        self.widget.installEventFilter(dock_filter)

    def destroy(self):
        """ A reimplemented destructor.

        This removes the event filter from the dock area and releases
        the items from the dock manager.

        """
        self.widget.removeEventFilter(self.dock_filter)
        del self.dock_filter
        self.manager.clear_items()
        super(QtDockArea, self).destroy()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_items(self):
        """ Get an iterable of QDockItem children for this area.

        """
        for d in self.declaration.dock_items():
            w = d.proxy.widget
            if w is not None:
                yield w

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockArea.

        """
        super(QtDockArea, self).child_added(child)
        if isinstance(child, QtDockItem):
            w = child.widget
            if w is not None:
                self.manager.add_item(w)

    def child_removed(self, child):
        """ Handle the child removed event for a QtDockArea.

        """
        super(QtDockArea, self).child_removed(child)
        if isinstance(child, QtDockItem):
            w = child.widget
            if w is not None:
                self.manager.remove_item(w)

    #--------------------------------------------------------------------------
    # ProxyDockArea API
    #--------------------------------------------------------------------------
    def set_tab_position(self, position):
        """ Set the default tab position on the underyling widget.

        """
        self.widget.setTabPosition(TAB_POSITIONS[position])

    def save_layout(self):
        """ Save the current layout on the underlying widget.

        """
        return self.manager.save_layout()

    def apply_layout(self, layout):
        """ Apply a new layout to the underlying widget.

        """
        self.manager.apply_layout(layout)
