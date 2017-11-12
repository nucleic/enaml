#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import QMargins, QSize, QEvent
from enaml.qt.QtWidgets import (
    QFrame, QLayout, QTabWidget, QGridLayout, QStackedLayout, QVBoxLayout,
    QWidget, QStyle, QStyleOption
)

from .q_dock_bar import QDockBarManager


class QDockAreaLayout(QStackedLayout):
    """ A custom stacked layout for the QDockArea.

    This stacked layout reports its size hints according to the widget
    which is currently visible, as opposed to aggregated hints which is
    the default.

    """
    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        widget = self.currentWidget()
        if widget is not None:
            return widget.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        widget = self.currentWidget()
        if widget is not None:
            return widget.minimumSizeHint()
        return QSize(256, 192)


class QDockArea(QFrame):
    """ A custom QFrame which provides an area for docking QDockItems.

    A dock area is used by creating QDockItem instances using the dock
    area as the parent. A DockLayout instance can then be created and
    applied to the dock area with the 'setDockLayout' method. The names
    in the DockLayoutItem objects are used to find the matching dock
    item widget child.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockArea.

        Parameters
        ----------
        parent : QWidget
            The parent of the dock area.

        """
        super(QDockArea, self).__init__(parent)
        self._dock_bar_manager = QDockBarManager(self)
        self._primary_pane = primary_pane = QWidget(self)
        self._central_pane = central_pane = QWidget(primary_pane)
        self._dock_events_enabled = False
        self._opaque_resize = None
        self._tab_position = None

        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        central_layout.setSizeConstraint(QLayout.SetMinimumSize)
        central_pane.setLayout(central_layout)

        grid_layout = QGridLayout()
        grid_layout.setRowStretch(0, 0)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 0)
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 0)
        grid_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        grid_layout.setSizeConstraint(QLayout.SetMinimumSize)
        grid_layout.addWidget(central_pane, 1, 1)
        primary_pane.setLayout(grid_layout)

        area_layout = QDockAreaLayout()
        area_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        area_layout.setSizeConstraint(QLayout.SetMinimumSize)
        area_layout.insertWidget(0, primary_pane)
        self.setLayout(area_layout)
        self.updateSpacing()

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock area.

        """
        if event.type() == QEvent.StyleChange:
            self.updateSpacing()
        return super(QDockArea, self).event(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def updateSpacing(self):
        """ Update the primary layout spacing for the dock area.

        This method will extract spacing value defined in the style
        sheet for the dock area and apply it to the spacing between
        the dock bars and the central widget.

        """
        opt = QStyleOption()
        opt.initFrom(self)
        style = self.style()
        # hack to get the style sheet 'spacing' property.
        spacing = style.pixelMetric(QStyle.PM_ToolBarItemSpacing, opt, self)
        grid_layout = self._primary_pane.layout()
        grid_layout.setVerticalSpacing(spacing)
        grid_layout.setHorizontalSpacing(spacing)

    def centralPane(self):
        """ Get the central pane for the dock area.

        This method is used the dock bar manager to access the central
        layout pane. It should not normally be called by user code.

        Returns
        -------
        result : QWidget
            The central pane for the dock area.

        """
        return self._central_pane

    def primaryPane(self):
        """ Get the primary pane for the dock area.

        This method is used the dock bar manager to access the primary
        layout pane. It should not normally be called by user code.

        Returns
        -------
        result : QWidget
            The primary pane for the dock area.

        """
        return self._primary_pane

    def centralWidget(self):
        """ Get the central dock widget for the area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Returns
        -------
        result : QWidget or None
            The central dock widget for the area, or None if no widget
            is installed.

        """
        item = self._central_pane.layout().itemAt(0)
        if item is not None:
            return item.widget()

    def setCentralWidget(self, widget):
        """ Set the central widget for the dock area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Parameters
        ----------
        widget : QWidget
            The central widget for the dock area.

        """
        layout = self._central_pane.layout()
        item = layout.itemAt(0)
        if item is not None:
            old = item.widget()
            if old is widget:
                return
            old.hide()
            old.setParent(None)
        if widget is not None:
            layout.addWidget(widget)
            # lower the widget to keep it stacked behind any pinned
            # containers which are in the slide-out position.
            widget.lower()
            widget.show()

    def maximizedWidget(self):
        """ Get the widget to that is set as the maximized widget.

        Returns
        -------
        result : QWidget or None
            The widget which is maximized over the dock area.

        """
        return self.layout().widget(1)

    def setMaximizedWidget(self, widget):
        """ Set the widget to maximize over the dock area.

        Returns
        -------
        result : QWidget or None
            The widget to maximize over the dock area.

        """
        old = self.maximizedWidget()
        if old is not None:
            if old is widget:
                return
            old.hide()
            old.setParent(None)
        if widget is not None:
            layout = self.layout()
            layout.insertWidget(1, widget)
            layout.setCurrentIndex(1)
            widget.show()

    def addToDockBar(self, container, position, index=-1):
        """ Add a container to the dock bar at the given position.

        Parameters
        ----------
        container : QDockContainer
            The dock container to add to the dock bar. The container
            should be unplugged from any other layout before calling
            this method.

        position : QDockBar.Position
            The enum value specifying the dock bar to which the
            container should be added.

        index : int, optional
            The index at which to insert the item. The default is -1
            and will append the item to the dock bar.

        """
        self._dock_bar_manager.addContainer(container, position, index)

    def removeFromDockBar(self, container):
        """ Remove a container previously added to a dock bar.

        Parameters
        ----------
        container : QDockContainer
            The dock container to remove from the dock bar.

        """
        self._dock_bar_manager.removeContainer(container)

    def dockBarGeometry(self, position):
        """ Get the geometry of the dock bar at the given position.

        Parameters
        ----------
        position : QDockBar.Position
            The enum value specifying the dock bar of interest.

        Returns
        -------
        result : QRect
            The geometry of the given dock bar expressed in area
            coordinates. If no dock bar exists at the given position,
            an invalid QRect will be returned.

        """
        return self._dock_bar_manager.dockBarGeometry(position)

    def dockBarContainers(self):
        """ Get the containers held in the dock bars.

        Returns
        -------
        result : list
            A list of tuples of the form (container, position).

        """
        return self._dock_bar_manager.dockBarContainers()

    def dockBarPosition(self, container):
        """ Get the dock bar position of the given container.

        Parameters
        ----------
        container : QDockContainer
            The dock container of interest.

        Returns
        -------
        result : QDockBar.Position or None
            The position of the container, or None if the container
            does not exist in the manager.

        """
        return self._dock_bar_manager.dockBarPosition(container)

    def extendFromDockBar(self, container):
        """ Extend the given container from its dock bar.

        If the container does not exist in a dock bar, this is a no-op.

        Parameters
        ----------
        container : QDockContainer
            The dock container of interest.

        """
        self._dock_bar_manager.extendContainer(container)

    def retractToDockBar(self, container):
        """ Retract the given container into it's dock bar.

        If the container does not exist in a dock bar, this is a no-op.

        Parameters
        ----------
        container : QDockContainer
            The dock container of interest.

        """
        self._dock_bar_manager.retractContainer(container)

    def clearDockBars(self):
        """ Clear the dock bars from the dock area.

        This method is called by the dock manager when the dock area
        is reset. It should not be called directly by user code.

        """
        self._dock_bar_manager.clearDockBars()

    def isEmpty(self):
        """ Get whether or not the dock area is empty.

        Returns
        -------
        result : bool
            True if the dock area is empty, False otherwise.

        """
        if self.centralWidget() is not None:
            return False
        if self.maximizedWidget() is not None:
            return False
        return self._dock_bar_manager.isEmpty()

    def tabPosition(self):
        """ Get the default position for newly created tab widgets.

        The tab position is inherited from an ancestor dock area unless
        it is explicitly set by the user.

        Returns
        -------
        result : QTabWidget.TabPosition
            The position for dock area tabs. If the value has not been
            set by the user and there is no ancestor dock area, the
            default is QTabWidget.North.

        """
        pos = self._tab_position
        if pos is not None:
            return pos
        p = self.parent()
        while p is not None:
            if isinstance(p, QDockArea):
                return p.tabPosition()
            p = p.parent()
        return QTabWidget.North

    def setTabPosition(self, position):
        """ Set the default position for newly created tab widget.

        Parameters
        ----------
        position : QTabWidget.TabPosition
            The position for the tabs of newly created tab widgets.

        """
        self._tab_position = position

    def dockEventsEnabled(self):
        """ Get whether dock events are enabled for the area.

        Returns
        -------
        result : bool
            True if dock events are enabled, False otherwise.

        """
        return self._dock_events_enabled

    def setDockEventsEnabled(self, enabled):
        """ Set whether dock events are enabled for the area.

        If events are enabled, then the various widgets involved with
        the dock area will post events to the *root* dock area when the
        various states have changed. If events are disabled, no such
        events will be posted.

        Parameters
        ----------
        enabled : bool
            True if dock events should be enabled, False otherwise.

        """
        self._dock_events_enabled = enabled

    def opaqueItemResize(self):
        """ Get whether opaque item resize is enabled.

        The tab position is inherited from an ancestor dock area unless
        it is explicitly set by the user.

        Returns
        -------
        result : bool
            True if item resizing is opaque, False otherwise. If the
            value has not been set by the user and there is no ancestor
            dock area, the default is True.

        """
        opaque = self._opaque_resize
        if opaque is not None:
            return opaque
        p = self.parent()
        while p is not None:
            if isinstance(p, QDockArea):
                return p.opaqueItemResize()
            p = p.parent()
        return True

    def setOpaqueItemResize(self, opaque):
        """ Set whether opaque item resize is enabled.

        Parameters
        ----------
        opaque : bool
            True if item resizing should be opaque, False otherwise.

        """
        is_different = opaque != self.opaqueItemResize()
        self._opaque_resize = opaque
        if is_different:
            # Avoid a circular import
            from .q_dock_splitter import QDockSplitter
            for sp in self.findChildren(QDockSplitter):
                sp.inheritOpaqueResize()
