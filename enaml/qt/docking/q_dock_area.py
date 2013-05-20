#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QMargins, QSize
from PyQt4.QtGui import QFrame, QLayout, QTabWidget, QWidgetItem

# Make sure the resources get registered.
from . import dock_resources


class QDockAreaLayout(QLayout):
    """ A custom QLayout which is part of the dock area implementation.

    """
    #: The index of the layout widget in the layout.
    LayoutWidget = 0

    #: The index of the maximized widget in the layout.
    MaximizedWidget = 1

    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the layout.

        """
        super(QDockAreaLayout, self).__init__(parent)
        self._items = [None, None]

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _getWidgetForRole(self, role):
        """ Get the widget for a given layout role.

        """
        item = self._items[role]
        if item is not None:
            return item.widget()

    def _setWidgetForRole(self, role, widget):
        """ Set the widget for a given layout role.

        """
        old = self._getWidgetForRole(role)
        if old is widget:
            return
        if old is not None:
            old.setParent(None)
        if widget is not None:
            self.addChildWidget(widget)
            item = QWidgetItem(widget)
            self._items[role] = item
        self._updateVisibilities()
        self.invalidate()

    def _updateVisibilities(self):
        """ Update the visibilities of the layout items.

        """
        layout, maxed = self._items
        if maxed is not None:
            maxed.widget().show()
            if layout is not None:
                layout.widget().hide()
        elif layout is not None:
            layout.widget().show()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def layoutWidget(self):
        """ Get the widget implementing the layout for the area.

        Returns
        -------
        result : QWidget or None
            The widget implementing the area, or None if no widget is
            installed.

        """
        return self._getWidgetForRole(self.LayoutWidget)

    def setLayoutWidget(self, widget):
        """ Set the layout widget for the dock area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Parameters
        ----------
        widget : QWidget
            The widget which implements the dock area layout.

        """
        self._setWidgetForRole(self.LayoutWidget, widget)

    def maximizedWidget(self):
        """ Get the widget to that is set as the maximized widget.

        Returns
        -------
        result : QWidget or None
            The widget which is maximized over the layout area.

        """
        return self._getWidgetForRole(self.MaximizedWidget)

    def setMaximizedWidget(self, widget):
        """ Set the widget to maximize over the area.

        Returns
        -------
        result : QWidget or None
            The widget to maximize over the layout area.

        """
        self._setWidgetForRole(self.MaximizedWidget, widget)

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        rect = self.contentsRect()
        for item in self._items:
            if item is not None:
                item.setGeometry(rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        widget = self._getWidgetForRole(self.MaximizedWidget)
        if widget is not None:
            return widget.sizeHint()
        widget = self._getWidgetForRole(self.LayoutWidget)
        if widget is not None:
            return widget.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size of the layout.

        """
        widget = self._getWidgetForRole(self.MaximizedWidget)
        if widget is not None:
            return widget.minimumSizeHint()
        widget = self._getWidgetForRole(self.LayoutWidget)
        if widget is not None:
            return widget.minimumSizeHint()
        return QSize(256, 192)

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        widget = self._getWidgetForRole(self.MaximizedWidget)
        if widget is not None:
            # FIXME i'm not totally sold on this logic:
            # A dock area with a maximized widget is free to expand.
            # This avoids ugly corner cases where the maximized widget
            # cannot expand, and will try to shrink the dock area.
            return super(QDockAreaLayout, self).maximumSize()
        widget = self._getWidgetForRole(self.LayoutWidget)
        if widget is not None:
            return widget.maximumSize()
        return super(QDockAreaLayout, self).maximumSize()

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setLayoutWidget` and
        `setMaximizedWidget` instead.

        """
        msg = 'Use `setLayoutWidget` and `setMaximizedWidget` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        items = self._items
        return len(items) - items.count(None)

    def itemAt(self, index):
        """ A virtual method implementation which returns None.

        """
        j = 0
        for item in self._items:
            if item is None:
                continue
            if j == index:
                return item
            j += 1

    def takeAt(self, index):
        """ A virtual method implementation which does nothing.

        """
        j = 0
        for i, item in enumerate(self._items):
            if item is None:
                continue
            if j == index:
                self._items[i] = None
                item.widget().hide()
                self._updateVisibilities()
                self.invalidate()
                return
            j += 1


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
        layout = QDockAreaLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self._tab_position = QTabWidget.North

        # FIXME temporary VS2010-like stylesheet
        self.setStyleSheet("""
            QDockArea {
                padding: 5px;
                background: rgb(49, 67, 98);
            }

            QDockSplitterHandle {
                background: rgba(0, 0, 0, 0);
            }

            QDockWindow {
                background: rgb(53, 73, 106);
                border: 1px solid rgb(40, 60, 90);
            }

            QDockContainer {
                background: rgb(53, 73, 106);
            }

            QDockContainer[floating="true"] {
                border: 1px solid rgb(40, 60, 90);
            }

            QDockItem {
                background: rgb(237, 237, 237);
            }

            QDockTitleBar {
                background: rgb(77, 96, 130);
            }

            QDockTitleBar > QTextLabel {
                color: rgb(250, 251, 254);
                font: 9pt "Segoe UI";
            }

            /* Correct a bug in the pane size when using system styling */
            QDockTabWidget::pane {
            }

            QDockTabBar::close-button {
                margin-bottom: 2px;
                image: url(:dock_images/closebtn_s.png);
            }

            QDockTabBar::close-button:selected {
                image: url(:dock_images/closebtn_b.png);
            }

            QDockTabBar::close-button:hover,
            QDockTabBar::close-button:selected:hover {
                image: url(:dock_images/closebtn_h.png);
            }

            QDockTabBar::close-button:pressed,
            QDockTabBar::close-button:selected:pressed {
                image: url(:dock_images/closebtn_p.png);
            }

            QDockTabBar::tab {
                background: rgba(255, 255, 255, 15);
                color: rgb(250, 251, 254);
            }

            QDockTabBar::tab:top, QDockTabBar::tab:bottom {
                margin-right: 1px;
                padding-left: 5px;
                padding-right: 5px;
                padding-bottom: 2px;
                height: 17px;
            }

            QDockTabBar::tab:left, QDockTabBar::tab:right {
                margin-bottom: 1px;
                padding-top: 5px;
                padding-bottom: 5px;
                width: 20px;
            }

            QDockTabBar::tab:hover {
                background: rgb(76, 105, 153);
            }

            QDockTabBar::tab:selected {
                background: rgb(237, 237, 237);
                color: black;
            }

            """ )

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
        return self.layout().layoutWidget()

    def setLayoutWidget(self, widget):
        """ Set the layout widget for the dock area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Parameters
        ----------
        widget : QWidget
            The widget which implements the dock area layout.

        """
        self.layout().setLayoutWidget(widget)

    def maximizedWidget(self):
        """ Get the widget to that is set as the maximized widget.

        Returns
        -------
        result : QWidget or None
            The widget which is maximized over the dock area.

        """
        return self.layout().maximizedWidget()

    def setMaximizedWidget(self, widget):
        """ Set the widget to maximize over the dock area.

        Returns
        -------
        result : QWidget or None
            The widget to maximize over the dock area.

        """
        self.layout().setMaximizedWidget(widget)

    def tabPosition(self):
        """ Get the default position for newly created tab widgets.

        """
        return self._tab_position

    def setTabPosition(self, position):
        """ Set the default position for newly created tab widget.

        Parameters
        ----------
        position : QTabWidget.TabPosition
            The position for the tabs of newly created tab widgets.

        """
        self._tab_position = position
