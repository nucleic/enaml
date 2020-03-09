#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed
from enaml.widgets.button_group import ProxyButtonGroup

from .QtWidgets import QButtonGroup

from .qt_toolkit_object import QtToolkitObject


class QtButtonGroup(QtToolkitObject, ProxyButtonGroup):
    """ A Qt implementation of the Enaml ProxyButtonGroup.

    """

    #: A reference to the widget created by the proxy
    widget = Typed(QButtonGroup)

    def create_widget(self):
        """ Create the button group widget.

        """
        self.widget = QButtonGroup(self.parent_widget())

    def init_widget(self):
        """ Initialize the button group widget.

        """
        super(QtButtonGroup, self).init_widget()

        d = self.declaration
        self.set_exclusive(d.exclusive)

    def set_exclusive(self, exclusive):
        """ Make the button group exclusive or not.

        """
        self.widget.setExclusive(exclusive)

    def add_button(self, button):
        """ Add a button to the group.

        """
        self.widget.addButton(button.proxy.widget)

    def remove_button(self, button):
        """ Remove a button from the group.

        """
        self.widget.removeButton(button.proxy.widget)
