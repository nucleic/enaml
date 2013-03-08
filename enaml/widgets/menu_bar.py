#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .menu import Menu
from .widget import Widget


class MenuBar(Widget):
    """ A widget used as a menu bar in a MainWindow.

    """
    @property
    def menus(self):
        """ A property which returns the menus defined on the menu bar.

        """
        isinst = isinstance
        menus = (child for child in self.children if isinst(child, Menu))
        return tuple(menus)

