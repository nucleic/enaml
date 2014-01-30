#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.menu import Menu
from enaml.workbench.extension_object import ExtensionObject


class MenuProvider(ExtensionObject):
    """ An interface for creating menu providers.

    Plugins which contribute to the 'enaml.studio.ui.menus' extension
    point should subclass this to provide a menu for the menu bar.

    """
    #: The menu to add to the menu bar. The window's menu bar will
    #: automatically update if this value changes at runtime. The
    #: studio takes ownership of the menu and will destroy it at
    #: the appropriate time.
    menu = Typed(Menu)
