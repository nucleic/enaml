#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QPushButton
from .qt_abstract_button import QtAbstractButton
from .qt_menu import QtMenu


class QtPushButton(QtAbstractButton):
    """ A Qt implementation of an Enaml PushButton.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying QPushButton widget.

        """
        return QPushButton(parent)

    def init_layout(self):
        """ Handle layout initialization for the push button.

        """
        super(QtPushButton, self).init_layout()
        self.widget().setMenu(self.menu())

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
        widget = None
        for child in self.children():
            if isinstance(child, QtMenu):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtPushButton.

        """
        if isinstance(child, QtMenu):
            self.widget().setMenu(self.menu())

    def child_added(self, child):
        """ Handle the child added event for a QtPushButton.

        """
        if isinstance(child, QtMenu):
            self.widget().setMenu(self.menu())

