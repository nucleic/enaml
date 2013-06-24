#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QMargins, QSize
from PyQt4.QtGui import (
    QFrame, QLayout, QTabWidget, QGridLayout, QStackedLayout, QWidget
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
        self._pane = pane = QWidget(self)

        self._tab_position = None
        self._opaque_resize = None
        self._pinned = {}

        grid = QGridLayout()
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 0)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(5)
        grid.setContentsMargins(QMargins(0, 0, 0, 0))
        grid.setSizeConstraint(QLayout.SetMinAndMaxSize)
        pane.setLayout(grid)

        layout = QDockAreaLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        layout.insertWidget(0, pane)
        self.setLayout(layout)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def layoutPane(self):
        """ Get the layout pane widget for the dock area.

        This method is used the dock bar manager to access the main
        layout pane. It should not normally be called by user code.

        Returns
        -------
        result : QWidget
            The primary layout pane for the dock area.

        """
        return self._pane

    def layoutWidget(self):
        """ Get the widget implementing the layout for the area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Returns
        -------
        result : QWidget or None
            The widget implementing the area, or None if no widget is
            installed.

        """
        item = self._pane.layout().itemAtPosition(1, 1)
        if item is not None:
            return item.widget()

    def setLayoutWidget(self, widget):
        """ Set the layout widget for the dock area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Parameters
        ----------
        widget : QWidget
            The widget which implements the dock area layout.

        """
        grid = self._pane.layout()
        item = grid.itemAtPosition(1, 1)
        if item is not None:
            old = item.widget()
            if old is widget:
                return
            old.hide()
            old.setParent(None)
        if widget is not None:
            grid.addWidget(widget, 1, 1)
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

    def pinContainer(self, container, position):
        """ Pin the container to the given dock bar position.

        Parameters
        ----------
        container : QDockContainer
            The dock container to pin to a dock bar.

        position : QDockBar.Position
            The enum value specifying the dock bar to which the
            container should be pinned.

        """
        self._dock_bar_manager.addContainer(container, position)

    def unpinContainer(self, container):
        """ Unpin a container previously pinned to a dock bar.

        Parameters
        ----------
        container : QDockContainer
            The dock container to unpin from the dock bar.

        """
        self._dock_bar_manager.removeContainer(container)

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
