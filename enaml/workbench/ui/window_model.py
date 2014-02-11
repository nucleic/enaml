#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed

from enaml.widgets.menu import Menu

from .branding import Branding
from .workspace import Workspace


class WindowModel(Atom):
    """ A model which is used to drive the WorkbenchWindow instance.

    """
    #: The branding which contributes the window title and icon.
    branding = Typed(Branding, ())

    #: The menu objects for the menu bar.
    menus = List(Menu)

    #: The currently active workspace for the window.
    workspace = Typed(Workspace, ())
