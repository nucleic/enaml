#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.push_button import ProxyPushButton

from .QtWidgets import QPushButton

from .qt_abstract_button import QtAbstractButton
from .qt_menu import QtMenu


class QtPushButton(QtAbstractButton, ProxyPushButton):
    """ A Qt implementation of an Enaml ProxyPushButton.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QPushButton)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QPushButton widget.

        """
        self.widget = QPushButton(self.parent_widget())

    def init_widget(self):
        """ Initialize the state of the widget.

        """
        super(QtPushButton, self).init_widget()
        self.set_default(self.declaration.default)

    def init_layout(self):
        """ Handle layout initialization for the push button.

        """
        super(QtPushButton, self).init_layout()
        self.widget.setMenu(self.menu())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def menu(self):
        """ Find and return the menu child for this widget.

        Returns
        -------
        result : QMenu or None
            The menu defined for this widget, or None if not defined.

        """
        m = self.declaration.menu()
        if m is not None:
            return m.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtPushButton.

        """
        super(QtPushButton, self).child_added(child)
        if isinstance(child, QtMenu):
            self.widget.setMenu(self.menu())

    def child_removed(self, child):
        """ Handle the child removed event for a QtPushButton.

        """
        super(QtPushButton, self).child_removed(child)
        if isinstance(child, QtMenu):
            self.widget.setMenu(self.menu())

    #--------------------------------------------------------------------------
    # ProxyPushButton API
    #--------------------------------------------------------------------------
    def set_default(self, default):
        """ Set the default button behavior for the widget.

        """
        self.widget.setDefault(default)
        if default:
            self.widget.setFocus()
