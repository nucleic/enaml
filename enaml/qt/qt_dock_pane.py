#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.dock_pane import ProxyDockPane

from .QtCore import Qt, Signal
from .QtWidgets import QDockWidget, QWidget

from .qt_container import QtContainer
from .qt_widget import QtWidget


#: A mapping from Enaml dock areas to Qt dock areas.
_DOCK_AREA_MAP = {
    'top': Qt.TopDockWidgetArea,
    'right': Qt.RightDockWidgetArea,
    'bottom': Qt.BottomDockWidgetArea,
    'left': Qt.LeftDockWidgetArea,
    'all': Qt.AllDockWidgetAreas,
}


#: A mapping from Qt dock areas to Enaml dock areas.
_DOCK_AREA_INV_MAP = {
    Qt.TopDockWidgetArea: 'top',
    Qt.RightDockWidgetArea: 'right',
    Qt.BottomDockWidgetArea: 'bottom',
    Qt.LeftDockWidgetArea: 'left',
    Qt.AllDockWidgetAreas: 'all',
}


class QCustomDockWidget(QDockWidget):
    """ A custom QDockWidget which adds some Enaml specific features.

    """
    #: A signal emitted when the dock widget is closed by the user.
    closed = Signal()

    #: A signal emitted when the dock widget is floated.
    floated = Signal()

    #: A signal emitted when the dock widget is docked. The payload
    #: will be the new dock area.
    docked = Signal(object)

    def __init__(self, parent=None):
        """ Initialize a QCustomDockWidget.

        """
        super(QCustomDockWidget, self).__init__(parent)
        self._title_bar_visible = True
        self._dock_area = Qt.LeftDockWidgetArea
        self.topLevelChanged.connect(self._onTopLevelChanged)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTopLevelChanged(self, top_level):
        """ The signal handler for the the 'topLevelChanged' signal.

        """
        # Hiding the title bar on a floating dock widget causes the
        # frame to be hidden. We need to make sure its shown when
        # floating, and hidden again upon docking if needed.
        if top_level:
            self._showTitleBar()
            self.floated.emit()
        else:
            if not self._title_bar_visible:
                self._hideTitleBar()
            parent = self.parent()
            if parent is not None:
                self._dock_area = parent.dockWidgetArea(self)
            self.docked.emit(self._dock_area)

    def _showTitleBar(self):
        """ Shows the title bar for the widget.

        """
        if self.titleBarWidget() is not None:
            self.setTitleBarWidget(None)

    def _hideTitleBar(self):
        """ Hides the title bar for the widget.

        """
        if self.titleBarWidget() is None:
            self.setTitleBarWidget(QWidget())

    def closeEvent(self, event):
        """ A close event handler which emits the 'closed' signal.

        """
        super(QCustomDockWidget, self).closeEvent(event)
        self.closed.emit()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockArea(self):
        """ Get the current dock area for the dock widget.

        Returns
        -------
        result : QDockWidgetArea
            The dock widget area where this dock widget resides.

        """
        return self._dock_area

    def setDockArea(self, area):
        """ Set the current dock area for the dock widget.

        Parameters
        ----------
        area : QDockWidgetArea
            The dock widget area where this dock widget should reside.

        """
        self._dock_area = area
        parent = self.parent()
        if parent is not None:
            parent.setDockWidgetArea(area, self)

    def titleBarVisible(self):
        """ Get whether or not the title bar is visible.

        Returns
        -------
        result : bool
            Whether or not the title bar is visible.

        """
        return self._title_bar_visible

    def setTitleBarVisible(self, visible):
        """ Set whether or not the title bar is visible.

        Parameters
        ----------
        visible : bool
            Whether or not the title bar is visible.

        """
        self._title_bar_visible = visible
        if visible:
            self._showTitleBar()
        else:
            if not self.isFloating():
                self._hideTitleBar()


# cyclic notification guard flags
FLOATED_GUARD = 0x1


class QtDockPane(QtWidget, ProxyDockPane):
    """ A Qt implementation of an Enaml ProxyDockPane.

    """
    #: A reference tot he widget created by the proxy.
    widget = Typed(QCustomDockWidget)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QCustomDockWidget widget.

        """
        self.widget = QCustomDockWidget(self.parent_widget())

    def init_widget(self):
        """ Initialize the dock pane control.

        """
        super(QtDockPane, self).init_widget()
        d = self.declaration
        self.set_title(d.title)
        self.set_title_bar_visible(d.title_bar_visible)
        self.set_title_bar_orientation(d.title_bar_orientation)
        self.set_closable(d.closable)
        self.set_movable(d.movable)
        self.set_floatable(d.floatable)
        self.set_floating(d.floating)
        self.set_dock_area(d.dock_area)
        self.set_allowed_dock_areas(d.allowed_dock_areas)
        widget = self.widget
        widget.closed.connect(self.on_closed)
        widget.floated.connect(self.on_floated)
        widget.docked.connect(self.on_docked)

    def init_layout(self):
        """ Handle the layout initialization for the dock pane.

        """
        super(QtDockPane, self).init_layout()
        self.widget.setWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_widget(self):
        """ Find and return the dock widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The dock widget defined for this widget, or None if one is
            not defined.

        """
        d = self.declaration.dock_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockPane.

        """
        super(QtDockPane, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setWidget(self.dock_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a QtDockPane.

        """
        super(QtDockPane, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_closed(self):
        """ The signal handler for the 'closed' signal.

        """
        # The closed signal is only emitted when the widget is closed
        # by the user, so there is no need for a loopback guard.
        self.declaration.visible = False
        self.declaration.closed()

    def on_floated(self):
        """ The signal handler for the 'floated' signal.

        """
        if not self._guard & FLOATED_GUARD:
            self._guard |= FLOATED_GUARD
            try:
                self.declaration.floating = True
            finally:
                self._guard &= ~FLOATED_GUARD

    def on_docked(self, area):
        """ The signal handler for the 'docked' signal.

        """
        if not self._guard & FLOATED_GUARD:
            self._guard |= FLOATED_GUARD
            try:
                self.declaration.floating = False
                self.declaration.dock_area = _DOCK_AREA_INV_MAP[area]
            finally:
                self._guard &= ~FLOATED_GUARD

    #--------------------------------------------------------------------------
    # ProxyDockPane API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        self.widget.setWindowTitle(title)

    def set_title_bar_visible(self, visible):
        """ Set the title bar visibility of the underlying widget.

        """
        self.widget.setTitleBarVisible(visible)

    def set_title_bar_orientation(self, orientation):
        """ Set the title bar orientation of the underyling widget.

        """
        widget = self.widget
        features = widget.features()
        if orientation == 'vertical':
            features |= QDockWidget.DockWidgetVerticalTitleBar
        else:
            features &= ~QDockWidget.DockWidgetVerticalTitleBar
        widget.setFeatures(features)

    def set_closable(self, closable):
        """ Set the closable state on the underlying widget.

        """
        widget = self.widget
        features = widget.features()
        if closable:
            features |= QDockWidget.DockWidgetClosable
        else:
            features &= ~QDockWidget.DockWidgetClosable
        widget.setFeatures(features)

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        widget = self.widget
        features = widget.features()
        if movable:
            features |= QDockWidget.DockWidgetMovable
        else:
            features &= ~QDockWidget.DockWidgetMovable
        widget.setFeatures(features)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        widget = self.widget
        features = widget.features()
        if floatable:
            features |= QDockWidget.DockWidgetFloatable
        else:
            features &= ~QDockWidget.DockWidgetFloatable
        widget.setFeatures(features)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        if not self._guard & FLOATED_GUARD:
            self._guard |= FLOATED_GUARD
            try:
                self.widget.setFloating(floating)
            finally:
                self._guard &= ~FLOATED_GUARD

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underlying widget.

        """
        self.widget.setDockArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        qt_areas = Qt.NoDockWidgetArea
        for area in dock_areas:
            qt_areas |= _DOCK_AREA_MAP[area]
        self.widget.setAllowedAreas(qt_areas)
