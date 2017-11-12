#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.action_group import ProxyActionGroup

from .QtWidgets import QActionGroup

from .qt_action import QtAction
from .qt_toolkit_object import QtToolkitObject


class QCustomActionGroup(QActionGroup):
    """ A QActionGroup subclass which fixes some toggling issues.

    When a QActionGroup is set from non-exclusive to exclusive, it
    doesn't uncheck the non-current actions. It also does not keep
    track of the most recently checked widget when in non-exclusive
    mode, so that state is lost. This subclass corrects these issues.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QCustomActionGroup.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QActionGroup.

        """
        super(QCustomActionGroup, self).__init__(*args, **kwargs)
        self.triggered.connect(self.onTriggered)
        self._last_checked = None

    def onTriggered(self, action):
        """ The signal handler for the 'triggered' signal.

        """
        if action.isCheckable() and action.isChecked():
            if self.isExclusive():
                last = self._last_checked
                if last is not None and last is not action:
                    last.setChecked(False)
            self._last_checked = action

    def setExclusive(self, exclusive):
        """ Set the exclusive state of the action group.

        Parameters
        ----------
        exclusive : bool
            Whether or not the action group is exclusive.

        """
        super(QCustomActionGroup, self).setExclusive(exclusive)
        if exclusive:
            last = self._last_checked
            if last is not None:
                last.setChecked(True)
                for action in self.actions():
                    if action is not last:
                        action.setChecked(False)


class QtActionGroup(QtToolkitObject, ProxyActionGroup):
    """ A Qt implementation of an Enaml ProxyActionGroup.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomActionGroup)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying action group widget.

        """
        self.widget = QCustomActionGroup(self.parent_widget())

    def init_widget(self):
        """ Initialize the control.

        """
        super(QtActionGroup, self).init_widget()
        d = self.declaration
        self.set_exclusive(d.exclusive)
        self.set_enabled(d.enabled)
        self.set_visible(d.visible)

    def init_layout(self):
        """ Initialize the layout for the control.

        """
        super(QtActionGroup, self).init_layout()
        widget = self.widget
        for action in self.actions():
            widget.addAction(action)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Locate the QAction object which logically follows the child.

        If the given child is last in the list of children, then the
        parent object will be invoked to find the QAction which follows
        this action group.

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
            if found and isinstance(dchild, QtAction):
                return dchild.widget
            else:
                found = child is dchild
        parent = self.parent()
        if parent is not None:
            return parent.find_next_action(self)

    def child_added(self, child):
        """ Handle the child added event for a QtActionGroup.

        This handler will also add the widget to the parent widget,
        since a QActionGroup only serves as a management container.

        """
        super(QtActionGroup, self).child_added(child)
        if isinstance(child, QtAction):
            self.widget.addAction(child.widget)
            parent = self.parent()
            if parent is not None:
                before = self.find_next_action(child)
                parent.widget.insertAction(before, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtActionGroup.

        This handler will also remove the widget to the parent widget,
        since a QActionGroup only serves as a management container.

        """
        super(QtActionGroup, self).child_removed(child)
        if isinstance(child, QtAction) and child.widget is not None:
            self.widget.removeAction(child.widget)
            parent = self.parent()
            if parent is not None:
                parent.widget.removeAction(child.widget)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def actions(self):
        """ Get the QAction children for this action group.

        Returns
        -------
        result : list
            The list of QAction instances which are children of this
            action group. Unlike the list returned by the `actions`
            method of the QActionGroup, the children in this list will
            have the correct order.

        """
        isinst = isinstance
        return [c.widget for c in self.children() if isinst(c, QtAction)]

    #--------------------------------------------------------------------------
    # ProxyActionGroup API
    #--------------------------------------------------------------------------
    def set_exclusive(self, exclusive):
        """ Set the exclusive state of the underlying control.

        """
        self.widget.setExclusive(exclusive)

    def set_enabled(self, enabled):
        """ Set the enabled state of the underlying control.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visible state of the underlying control.

        """
        self.widget.setVisible(visible)
