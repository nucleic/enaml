#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed

from .content_provider import ContentProvider
from .icon_provider import IconProvider
from .menu_provider import MenuProvider
from .title_provider import TitleProvider


class WindowModel(Atom):
    """ A model which is used to drive the StudioWindow instance.

    """
    #: The provider which contributes the window title.
    title_provider = Typed(TitleProvider, ())

    #: The provider which contributes the window icon.
    icon_provider = Typed(IconProvider, ())

    #: The providers which contribute menus to the menu bar.
    menu_providers = List(MenuProvider)

    #: The provider which contributes the window content.
    content_provider = Typed(ContentProvider, ())
