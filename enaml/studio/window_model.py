#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed, Unicode

from enaml.icon import Icon


class TitleProvider(Atom):
    """ A base class for defining studio title providers.

    """
    title = Unicode()


class IconProvider(Atom):
    """ A base class for defining icon providers.

    """
    icon = Typed(Icon)


class WindowModel(Atom):
    """ A model which is used to build the studio window.

    """
    #: The list of providers which contribute title information.
    title_providers = List(TitleProvider)

    #: The provider which contributes the window icon.
    icon_provider = Typed(IconProvider, ())
