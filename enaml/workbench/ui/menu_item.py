#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Unicode

from enaml.core.declarative import Declarative, d_

from .group import Group


class MenuItem(Declarative):
    """ A declarative class for defining a menu in the workbench.

    """
    #: The globally unique identifier for the menu.
    id = d_(Unicode())

    #: The identifier of the parent menu in which the menu resides. A
    #: group can be specified by appending a colon followed by the name
    #: of the desired group. e.g. file:close_group
    location = d_(Unicode())

    #: The item id before which this item will appear.
    before = d_(Unicode())

    #: The item id after which this item will appear.
    after = d_(Unicode())

    #: The display label for the menu.
    label = d_(Unicode())

    #: Whether or not the menu is visible.
    visible = d_(Bool(True))

    #: Whether or not the menu is enabled.
    enabled = d_(Bool(True))

    @property
    def groups(self):
        """ Get the groups defined on this menu item.

        """
        return [c for c in self.children if isinstance(c, Group)]
