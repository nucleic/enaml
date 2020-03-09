#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str

from enaml.core.declarative import Declarative, d_

from .item_group import ItemGroup


class MenuItem(Declarative):
    """ A declarative class for defining a menu in the workbench.

    """
    #: The "/" separated path to this item in the menu bar.
    path = d_(Str())

    #: The parent menu group to which this menu item belongs.
    group = d_(Str())

    #: The menu item will appear before this item in its group.
    before = d_(Str())

    #: The menu item will appear after this item in its group.
    after = d_(Str())

    #: The display label for the menu.
    label = d_(Str())

    #: Whether or not the menu is visible.
    visible = d_(Bool(True))

    #: Whether or not the menu is enabled.
    enabled = d_(Bool(True))

    @property
    def item_groups(self):
        """ Get the item groups defined on this menu item.

        """
        return [c for c in self.children if isinstance(c, ItemGroup)]
