#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.menu import ProxyMenu

from .QtCore import Qt
from .QtGui import QCursor
from .QtWidgets import QMenu

from .qt_action import QtAction
from .qt_action_group import QtActionGroup
from .qt_toolkit_object import QtToolkitObject
from .qt_widget import QtWidget


class QCustomMenu(QMenu):
    """ A custom subclass of QMenu which adds some convenience apis.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QCustomMenu.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QMenu.

        """
        super(QCustomMenu, self).__init__(*args, **kwargs)
        self._is_context_menu = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onShowContextMenu(self, pos):
        """ A private signal handler for displaying the context menu.

        This handler is connected to the context menu requested signal
        on the parent widget when this menu is marked as a context
        menu.

        """
        parent = self.parentWidget()
        if parent is not None:
            global_pos = parent.mapToGlobal(pos)
            self.exec_(global_pos)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def isContextMenu(self):
        """ Whether this menu acts as a context menu for its parent.

        Returns
        -------
        result : bool
            True if this menu acts as a context menu, False otherwise.

        """
        return self._is_context_menu

    def setContextMenu(self, context):
        """ Set whether this menu acts as a context menu for its parent.

        Parameters
        ----------
        context : bool
            True if this menu should act as a context menu, False
            otherwise.

        """
        old_context = self._is_context_menu
        self._is_context_menu = context
        if old_context != context:
            parent = self.parentWidget()
            if parent is not None:
                handler = self._onShowContextMenu
                if context:
                    parent.setContextMenuPolicy(Qt.CustomContextMenu)
                    parent.customContextMenuRequested.connect(handler)
                else:
                    parent.setContextMenuPolicy(Qt.DefaultContextMenu)
                    parent.customContextMenuRequested.disconnect(handler)

    def removeActions(self, actions):
        """ Remove the given actions from the menu.

        Parameters
        ----------
        actions : iterable
            An iterable of QActions to remove from the menu.

        """
        remove = self.removeAction
        for action in actions:
            remove(action)


class QtMenu(QtToolkitObject, ProxyMenu):
    """ A Qt implementation of an Enaml ProxyMenu.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomMenu)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying menu widget.

        """
        self.widget = QCustomMenu(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtMenu, self).init_widget()
        d = self.declaration
        self.set_title(d.title)
        self.set_enabled(d.enabled)
        self.set_visible(d.visible)
        self.set_context_menu(d.context_menu)

    def init_layout(self):
        """ Initialize the layout of the widget.

        """
        super(QtMenu, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, QtMenu):
                widget.addMenu(child.widget)
            elif isinstance(child, QtAction):
                widget.addAction(child.widget)
            elif isinstance(child, QtActionGroup):
                widget.addActions(child.actions())
            elif isinstance(child, QtWidget):
                widget.addAction(child.get_action(True))

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which follows the child.

        Parameters
        ----------
        child : QtToolkitObject
            The child of interest.

        Returns
        -------
        result : QAction or None
            The QAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        found = False
        for dchild in self.children():
            if found:
                if isinstance(dchild, QtMenu):
                    return dchild.widget.menuAction()
                elif isinstance(dchild, QtAction):
                    return dchild.widget
                elif isinstance(dchild, QtActionGroup):
                    acts = dchild.actions()
                    if len(acts) > 0:
                        return acts[0]
                elif isinstance(dchild, QtWidget):
                    action = dchild.get_action(False)
                    if action is not None:
                        return action
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a QtMenu.

        """
        super(QtMenu, self).child_added(child)
        if isinstance(child, QtMenu):
            before = self.find_next_action(child)
            self.widget.insertMenu(before, child.widget)
        elif isinstance(child, QtAction):
            before = self.find_next_action(child)
            self.widget.insertAction(before, child.widget)
        elif isinstance(child, QtActionGroup):
            before = self.find_next_action(child)
            self.widget.insertActions(before, child.actions())
        elif isinstance(child, QtWidget):
            before = self.find_next_action(child)
            self.widget.insertAction(before, child.get_action(True))

    def child_removed(self, child):
        """  Handle the child removed event for a QtMenu.

        """
        super(QtMenu, self).child_removed(child)
        if isinstance(child, QtMenu):
            self.widget.removeAction(child.widget.menuAction())
        elif isinstance(child, QtAction):
            self.widget.removeAction(child.widget)
        elif isinstance(child, QtActionGroup):
            self.widget.removeActions(child.actions())
        elif isinstance(child, QtWidget):
            self.widget.removeAction(child.get_action(False))

    #--------------------------------------------------------------------------
    # ProxyMenu API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the underlying widget.

        """
        self.widget.setTitle(title)

    def set_visible(self, visible):
        """ Set the visibility on the underlying widget.

        """
        self.widget.menuAction().setVisible(visible)

    def set_enabled(self, enabled):
        """ Set the enabled state of the widget.

        """
        self.widget.setEnabled(enabled)

    def set_context_menu(self, context):
        """ Set whether or not the menu is a context menu.

        """
        self.widget.setContextMenu(context)

    def popup(self):
        """ Popup the menu over the current mouse location.

        """
        self.widget.exec_(QCursor.pos())

    def close(self):
        """ Close the underlying menu.

        """
        self.widget.close()
