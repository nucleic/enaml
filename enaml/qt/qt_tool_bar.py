#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Int, Typed

from enaml.widgets.tool_bar import ProxyToolBar

from .QtCore import Qt, Signal
from .QtWidgets import QToolBar, QMainWindow

from .qt_action import QtAction
from .qt_action_group import QtActionGroup
from .qt_constraints_widget import QtConstraintsWidget
from .qt_widget import QtWidget


#: A mapping from Enaml dock area to Qt tool bar areas
DOCK_AREAS = {
    'top': Qt.TopToolBarArea,
    'right': Qt.RightToolBarArea,
    'bottom': Qt.BottomToolBarArea,
    'left': Qt.LeftToolBarArea,
    'all': Qt.AllToolBarAreas,
}


#: A mapping from Qt tool bar areas to Enaml dock areas
DOCK_AREAS_INV = {
    Qt.TopToolBarArea: 'top',
    Qt.RightToolBarArea: 'right',
    Qt.BottomToolBarArea: 'bottom',
    Qt.LeftToolBarArea: 'left',
    Qt.AllToolBarAreas: 'all',
}


#: A mapping from Enaml orientation to Qt Orientation
ORIENTATIONS = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


#: A mapping from Enaml button style to Qt ToolButtonStyle
BUTTON_STYLES = {
    'icon_only': Qt.ToolButtonIconOnly,
    'text_only': Qt.ToolButtonTextOnly,
    'text_beside_icon': Qt.ToolButtonTextBesideIcon,
    'text_under_icon': Qt.ToolButtonTextUnderIcon,
}


class QCustomToolBar(QToolBar):
    """ A custom QToolBar which adds some Enaml specific features.

    """
    #: A signal emitted when the dock widget is floated.
    floated = Signal()

    #: A signal emitted when the dock widget is docked. The payload
    #: will be the new dock area.
    docked = Signal(object)

    def __init__(self, *args, **kwargs):
        """ Initialize a QCustomToolBar.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QToolBar.

        """
        super(QCustomToolBar, self).__init__(*args, **kwargs)
        self._tool_bar_area = Qt.TopToolBarArea
        self.topLevelChanged.connect(self._onTopLevelChanged)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTopLevelChanged(self, top_level):
        """ The signal handler for the the 'topLevelChanged' signal.

        """
        if top_level:
            self.floated.emit()
        else:
            parent = self.parent()
            if parent is not None and isinstance(parent, QMainWindow):
                self._tool_bar_area = parent.toolBarArea(self)
            self.docked.emit(self._tool_bar_area)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def removeActions(self, actions):
        """ Remove the given actions from the tool bar.

        Parameters
        ----------
        actions : iterable
            An iterable of QActions to remove from the tool bar.

        """
        remove = self.removeAction
        for action in actions:
            remove(action)

    def toolBarArea(self):
        """ Get the current tool bar area for the tool bar.

        Returns
        -------
        result : QToolBarArea
            The tool bar area where this tool bar resides.

        """
        return self._tool_bar_area

    def setToolBarArea(self, area):
        """ Set the current tool bar area for the tool bar.

        Parameters
        ----------
        area : QToolBarArea
            The tool bar area where this tool bar should reside.

        """
        self._tool_bar_area = area
        parent = self.parent()
        if isinstance(parent, QMainWindow):
            parent.setToolBarArea(area, self)

    def setFloating(self, floating):
        """ Set the floating state of the tool bar.

        Parameters
        ----------
        floating : bool
            Whether or not the tool bar should floating.

        """
        # QToolBar doesn't provide a setFloating() method. This code
        # is taken mostly from QToolBarPrivate::updateWindowFlags.
        parent = self.parent()
        if isinstance(parent, QMainWindow):
            visible = self.isVisibleTo(parent)
            flags = Qt.Tool if floating else Qt.Widget
            flags |= Qt.FramelessWindowHint
            if sys.platform == 'darwin':
                flags |= Qt.WindowStaysOnTopHint
            self.setWindowFlags(flags)
            if visible:
                self.resize(self.sizeHint())
                self.setVisible(True)


# cyclic notification guard flags
FLOATED_GUARD = 0x1


class QtToolBar(QtConstraintsWidget, ProxyToolBar):
    """ A Qt implementation of an Enaml ToolBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomToolBar)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QCustomToolBar widget.

        """
        self.widget = QCustomToolBar(self.parent_widget())

    def init_widget(self):
        """ Initialize the tool bar widget.

        """
        super(QtToolBar, self).init_widget()
        d = self.declaration
        self.set_button_style(d.button_style)
        self.set_movable(d.movable)
        self.set_floatable(d.floatable)
        self.set_floating(d.floating)
        self.set_dock_area(d.dock_area)
        self.set_allowed_dock_areas(d.allowed_dock_areas)
        self.set_orientation(d.orientation)
        widget = self.widget
        widget.floated.connect(self.on_floated)
        widget.docked.connect(self.on_docked)

    def init_layout(self):
        """ Initialize the layout for the toolbar.

        """
        super(QtToolBar, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, QtAction):
                widget.addAction(child.widget)
            elif isinstance(child, QtActionGroup):
                widget.addActions(child.actions())
            elif isinstance(child, QtWidget):
                widget.addAction(child.get_action(True))

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Locate the QAction object which logically follows the child.

        Parameters
        ----------
        child : QtToolkitObject
            The child object of interest.

        Returns
        -------
        result : QAction or None
            The QAction which logically follows the position of the
            child in the list of children. None will be returned if
            a relevant QAction is not found.

        """
        found = False
        for dchild in self.children():
            if found:
                if isinstance(dchild, QtAction):
                    return dchild.widget
                elif isinstance(dchild, QtActionGroup):
                    actions = dchild.actions()
                    if len(actions) > 0:
                        return actions[0]
                elif isinstance(dchild, QtWidget):
                    action = dchild.get_action(False)
                    if action is not None:
                        return action
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a QtToolBar.

        This handler will scan the children to find the proper point
        at which to insert the action.

        """
        super(QtToolBar, self).child_added(child)
        if isinstance(child, QtAction):
            before = self.find_next_action(child)
            self.widget.insertAction(before, child.widget)
        elif isinstance(child, QtActionGroup):
            before = self.find_next_action(child)
            self.widget.insertActions(before, child.actions())
        elif isinstance(child, QtWidget):
            before = self.find_next_action(child)
            self.widget.insertAction(before, child.get_action(True))

    def child_removed(self, child):
        """  Handle the child removed event for a QtToolBar.

        """
        super(QtToolBar, self).child_removed(child)
        if isinstance(child, QtAction):
            self.widget.removeAction(child.widget)
        elif isinstance(child, QtActionGroup):
            self.widget.removeActions(child.actions())
        elif isinstance(child, QtWidget):
            self.widget.removeAction(child.get_action(False))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
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
                self.declaration.dock_area = DOCK_AREAS_INV[area]
            finally:
                self._guard &= ~FLOATED_GUARD

    #--------------------------------------------------------------------------
    # ProxyToolBar API
    #--------------------------------------------------------------------------
    def set_button_style(self, style):
        """ Set the button style for the toolbar.

        """
        self.widget.setToolButtonStyle(BUTTON_STYLES[style])

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        self.widget.setMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget.setFloatable(floatable)

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
        """ Set the dock area on the underyling widget.

        """
        self.widget.setToolBarArea(DOCK_AREAS[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        qt_areas = Qt.NoToolBarArea
        for area in dock_areas:
            qt_areas |= DOCK_AREAS[area]
        self.widget.setAllowedAreas(qt_areas)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        # If the tool bar is a child of a QMainWindow, then that window
        # will take control of setting its orientation and changes to
        # the orientation by the user must be ignored.
        widget = self.widget
        parent = widget.parent()
        if not isinstance(parent, QMainWindow):
            widget.setOrientation(ORIENTATIONS[orientation])
