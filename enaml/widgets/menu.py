#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Unicode, observe

from enaml.core.declarative import d_

from .action import Action
from .action_group import ActionGroup
from .widget import Widget


class Menu(Widget):
    """ A widget used as a menu in a MenuBar.

    """
    #: The title to use for the menu.
    title = d_(Unicode())

    #: Whether this menu should behave as a context menu for its parent.
    context_menu = d_(Bool(False))

    @property
    def items(self):
        """ A read only property for the items declared on the menu.

        A menu item is one of Action, ActionGroup, or Menu.

        """
        isinst = isinstance
        allowed = (Action, ActionGroup, Menu)
        items = (child for child in self.children if isinst(child, allowed))
        return tuple(items)

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the Menu.

        """
        snap = super(Menu, self).snapshot()
        snap['title'] = self.title
        snap['context_menu'] = self.context_menu
        return snap

    @observe(r'^(title|context_menu)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends menu state change.

        """
        # The superclass implementation is sufficient.
        super(Menu, self).send_member_change(change)

