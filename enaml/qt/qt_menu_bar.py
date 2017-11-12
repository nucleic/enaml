#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed

from enaml.widgets.menu_bar import ProxyMenuBar

from .QtWidgets import QMainWindow, QMenuBar

from .qt_menu import QtMenu
from .qt_toolkit_object import QtToolkitObject


class QtMenuBar(QtToolkitObject, ProxyMenuBar):
    """ A Qt implementation of an Enaml ProxyMenuBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QMenuBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying menu bar widget.

        """
        # Qt behaves better when creating the menu bar without a parent.
        self.widget = QMenuBar()

    def init_layout(self):
        """ Initialize the layout for the menu bar.

        """
        super(QtMenuBar, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, QtMenu):
                widget.addMenu(child.widget)

    def destroy(self):
        """ A reimplemented destructor.

        Qt takes ownership of the menubar, so the destructor does not
        attempt to unparent the menubar. The child_removed handler on
        the main window will reset the menu bar.

        """
        del self.declaration

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which follows the child.

        Parameters
        ----------
        child : QtMenu
            The child menu of interest.

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
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a QtMenuBar.

        """
        super(QtMenuBar, self).child_added(child)
        if isinstance(child, QtMenu):
            before = self.find_next_action(child)
            self.widget.insertMenu(before, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtMenuBar.

        """
        super(QtMenuBar, self).child_removed(child)
        if isinstance(child, QtMenu):
            self.widget.removeAction(child.widget.menuAction())
