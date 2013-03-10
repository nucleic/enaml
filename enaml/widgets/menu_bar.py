#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .menu import Menu
from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyMenuBar(ProxyToolkitObject):
    """ The abstract definition of a proxy MenuBar object.

    """
    #: A reference to the MenuBar declaration.
    declaration = ForwardTyped(lambda: MenuBar)


class MenuBar(ToolkitObject):
    """ A widget used as a menu bar in a MainWindow.

    """
    #: A reference to the ProxyMenuBar object.
    proxy = Typed(ProxyMenuBar)

    def menus(self):
        """ Get the menus defined as children on the menu bar.

        """
        return [child for child in self.children if isinstance(child, Menu)]
