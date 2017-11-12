#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.styling import StyleCache
from enaml.widgets.dock_area import ProxyDockArea
from enaml.widgets.dock_events import DockItemEvent

from .QtCore import QObject, QEvent, QSize, QTimer
from .QtWidgets import QTabWidget

from .docking.dock_manager import DockManager
from .docking.event_types import (
    DockItemDocked, DockItemUndocked, DockItemExtended, DockItemRetracted,
    DockItemShown, DockItemHidden, DockItemClosed, DockTabSelected
)
from .docking.q_dock_area import QDockArea
from .docking.style_sheets import get_style_sheet

from .qt_constraints_widget import QtConstraintsWidget
from .qt_dock_item import QtDockItem
from .styleutil import translate_dock_area_style


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


EVENT_TYPES = {
    DockItemDocked: DockItemEvent.Docked,
    DockItemUndocked: DockItemEvent.Undocked,
    DockItemExtended: DockItemEvent.Extended,
    DockItemRetracted: DockItemEvent.Retracted,
    DockItemShown: DockItemEvent.Shown,
    DockItemHidden: DockItemEvent.Hidden,
    DockItemClosed: DockItemEvent.Closed,
    DockTabSelected: DockItemEvent.TabSelected,
}


class DockLayoutFilter(QObject):
    """ An event filter used by the QtDockArea.

    This event filter listens for LayoutRequest events on the dock
    area widget, and will send a geometry_updated notification to
    the constraints system when the dock area size hint changes. The
    notifications are collapsed on a single shot timer so that the
    dock area geometry can fully settle before being snapped by the
    constraints layout engine.

    """
    def __init__(self, owner):
        super(DockLayoutFilter, self).__init__()
        self._owner = owner
        self._size_hint = QSize()
        self._pending = False
        self._timer = timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.onNotify)

    def onNotify(self):
        self._owner.geometry_updated()
        self._pending = False

    def eventFilter(self, obj, event):
        if not self._pending and event.type() == QEvent.LayoutRequest:
            hint = obj.sizeHint()
            if hint != self._size_hint:
                self._size_hint = hint
                self._timer.start(0)
                self._pending = True
        return False


class DockEventFilter(QObject):
    """ An event filter used by the QtDockArea.

    This event filter listens for dock events on the dock area widget,
    converts them to front-end events, and posts them to the front-end
    declaration object.

    """
    def __init__(self, owner):
        super(DockEventFilter, self).__init__()
        self._owner = owner

    def eventFilter(self, obj, event):
        e_type = EVENT_TYPES.get(event.type())
        if e_type is not None:
            d = self._owner.declaration
            if d is not None:
                d.dock_event(DockItemEvent(type=e_type, name=event.name()))
        return False


class QtDockArea(QtConstraintsWidget, ProxyDockArea):
    """ A Qt implementation of an Enaml DockArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDockArea)

    #: The docking manager which will drive the dock area.
    manager = Typed(DockManager)

    #: The event filter which listens for layout requests.
    dock_layout_filter = Typed(DockLayoutFilter)

    #: The event filter which listens for dock events.
    dock_event_filter = Typed(DockEventFilter)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockArea widget.

        """
        self.widget = QDockArea(self.parent_widget())
        self.manager = DockManager(self.widget)
        self.dock_event_filter = DockEventFilter(self)
        self.dock_layout_filter = DockLayoutFilter(self)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDockArea, self).init_widget()
        d = self.declaration
        self.set_tab_position(d.tab_position)
        self.set_live_drag(d.live_drag)
        if d.style:  # TODO remove this in Enaml 1.0
            self.set_style(d.style)
        self.set_dock_events_enabled(d.dock_events_enabled)

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtDockArea, self).init_layout()
        manager = self.manager
        for item in self.dock_items():
            manager.add_item(item)
        d = self.declaration
        self.apply_layout(d.layout)
        self.widget.installEventFilter(self.dock_layout_filter)

    def destroy(self):
        """ A reimplemented destructor.

        This removes the event filter from the dock area and releases
        the items from the dock manager.

        """
        self.widget.removeEventFilter(self.dock_layout_filter)
        self.widget.removeEventFilter(self.dock_event_filter)
        del self.dock_layout_filter
        del self.dock_event_filter
        self.manager.destroy()
        super(QtDockArea, self).destroy()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def refresh_style_sheet(self):
        """ A reimplemented styling method.

        The dock area uses custom stylesheet processing.

        """
        # workaround win-7 sizing bug
        parts = [u'QDockTabWidget::pane {}']
        name = self.widget.objectName()
        for style in StyleCache.styles(self.declaration):
            t = translate_dock_area_style(name, style)
            if t:
                parts.append(t)
        if len(parts) > 1:
            stylesheet = u'\n\n'.join(parts)
        else:
            stylesheet = u''
        self.widget.setStyleSheet(stylesheet)

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

    def set_live_drag(self, live_drag):
        """ Set the live drag state for the underlying widget.

        """
        self.widget.setOpaqueItemResize(live_drag)

    def set_style(self, style):
        """ Set the style for the underlying widget.

        """
        # If get_style_sheet returns something, it means the user will
        # have already called register_style_sheet, which will raise
        # a deprecation warning. TODO remove this method in Enaml 1.0.
        sheet = get_style_sheet(style)
        if sheet:
            self.widget.setStyleSheet(sheet)

    def set_dock_events_enabled(self, enabled):
        """ Set whether or not dock events are enabled for the area.

        """
        widget = self.widget
        widget.setDockEventsEnabled(enabled)
        if enabled:
            widget.installEventFilter(self.dock_event_filter)
        else:
            widget.removeEventFilter(self.dock_event_filter)

    def save_layout(self):
        """ Save the current layout on the underlying widget.

        """
        return self.manager.save_layout()

    def apply_layout(self, layout):
        """ Apply a new layout to the underlying widget.

        """
        self.manager.apply_layout(layout)

    def update_layout(self, ops):
        """ Update the layout from a list of layout operations.

        """
        self.manager.update_layout(ops)
