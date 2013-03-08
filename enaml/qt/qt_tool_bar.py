#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from .qt.QtCore import Qt, Signal
from .qt.QtGui import QToolBar, QMainWindow
from .qt_action import QtAction
from .qt_action_group import QtActionGroup
from .qt_constraints_widget import QtConstraintsWidget


#: A mapping from Enaml dock area to Qt tool bar areas
_DOCK_AREA_MAP = {
    'top': Qt.TopToolBarArea,
    'right': Qt.RightToolBarArea,
    'bottom': Qt.BottomToolBarArea,
    'left': Qt.LeftToolBarArea,
    'all': Qt.AllToolBarAreas,
}


#: A mapping from Qt tool bar areas to Enaml dock areas
_DOCK_AREA_INV_MAP = {
    Qt.TopToolBarArea: 'top',
    Qt.RightToolBarArea: 'right',
    Qt.BottomToolBarArea: 'bottom',
    Qt.LeftToolBarArea: 'left',
    Qt.AllToolBarAreas: 'all',
}


#: A mapping from Enaml orientation to Qt Orientation
_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
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


class QtToolBar(QtConstraintsWidget):
    """ A Qt implementation of an Enaml ToolBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying tool bar widget.

        """
        return QCustomToolBar(parent)

    def create(self, tree):
        """ Create and initialize the underlying tool bar control.

        """
        super(QtToolBar, self).create(tree)
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])
        self.set_orientation(tree['orientation'])
        widget = self.widget()
        widget.floated.connect(self.on_floated)
        widget.docked.connect(self.on_docked)

    def init_layout(self):
        """ Initialize the layout for the toolbar.

        """
        super(QtToolBar, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtAction):
                widget.addAction(child.widget())
            elif isinstance(child, QtActionGroup):
                widget.addActions(child.actions())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """  Handle the child removed event for a QtToolBar.

        """
        if isinstance(child, QtAction):
            self.widget().removeAction(child.widget())
        elif isinstance(child, QtActionGroup):
            self.widget().removeActions(child.actions())

    def child_added(self, child):
        """ Handle the child added event for a QtToolBar.

        """
        before = self.find_next_action(child)
        if isinstance(child, QtAction):
            self.widget().insertAction(before, child.widget())
        elif isinstance(child, QtActionGroup):
            self.widget().insertActions(before, child.actions())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which comes immediately after the
        actions of the given child.

        Parameters
        ----------
        child : QtActionGroup, or QtAction
            The child of interest.

        Returns
        -------
        result : QAction or None
            The QAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        # The target action must be tested for membership against the
        # current actions on the tool bar itself, since this method may
        # be called after a child is added, but before the actions for
        # the child have actually been added to the tool bar.
        index = self.index_of(child)
        if index != -1:
            actions = set(self.widget().actions())
            for child in self.children()[index + 1:]:
                target = None
                if isinstance(child, QtAction):
                    target = child.widget()
                elif isinstance(child, QtActionGroup):
                    acts = child.actions()
                    target = acts[0] if acts else None
                if target in actions:
                    return target

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_floated(self):
        """ The signal handler for the 'floated' signal.

        """
        if 'floating' not in self.loopback_guard:
            self.send_action('floated', {})

    def on_docked(self, area):
        """ The signal handler for the 'docked' signal.

        """
        if 'floating' not in self.loopback_guard:
            content = {'dock_area': _DOCK_AREA_INV_MAP[area]}
            self.send_action('docked', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_movable(self, content):
        """ Handle the 'set_movable' action from the Enaml widget.

        """
        self.set_movable(content['movable'])

    def on_action_set_floatable(self, content):
        """ Handle the 'set_floatable' action from the Enaml widget.

        """
        self.set_floatable(content['floatable'])

    def on_action_set_floating(self, content):
        """ Handle the 'set_floating' action from the Enaml widget.

        """
        self.set_floating(content['floating'])

    def on_action_set_dock_area(self, content):
        """ Handle the 'set_dock_area' action from the Enaml widget.

        """
        self.set_dock_area(content['dock_area'])

    def on_action_set_allowed_dock_areas(self, content):
        """ Handle the 'set_allowed_dock_areas' action from the Enaml
        widget.

        """
        self.set_allowed_dock_areas(content['allowed_dock_areas'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        self.widget().setMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget().setFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        with self.loopback_guard('floating'):
            self.widget().setFloating(floating)

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        self.widget().setToolBarArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        qt_areas = Qt.NoToolBarArea
        for area in dock_areas:
            qt_areas |= _DOCK_AREA_MAP[area]
        self.widget().setAllowedAreas(qt_areas)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        # If the tool bar is a child of a QMainWindow, then that window
        # will take control of setting its orientation and changes to
        # the orientation by the user must be ignored.
        widget = self.widget()
        parent = widget.parent()
        if not isinstance(parent, QMainWindow):
            widget.setOrientation(_ORIENTATION_MAP[orientation])

