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
from .title_provider import TitleProvider


class WindowModel(Atom):
    """ A model which is used to build the studio window.

    """
    #: The providers which contributes the window title.
    title_provider = Typed(TitleProvider, ())

    #: The provider which contributes the window icon.
    icon_provider = Typed(IconProvider, ())

    #: The menu objects to include in the menu bar.
    menus = List()

    #: The primary content widget for the window.
    content_provider = Typed(ContentProvider, ())
