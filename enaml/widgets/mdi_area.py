#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, set_default

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .mdi_window import MdiWindow


class ProxyMdiArea(ProxyConstraintsWidget):
    """ The abstract definition of a proxy MdiArea object.

    """
    #: A reference to the MdiArea declaration.
    declaration = ForwardTyped(lambda: MdiArea)


class MdiArea(ConstraintsWidget):
    """ A widget which acts as a virtual window manager for other
    top level widget.

    An MdiArea can be used to provide an area within an application
    that can display other widgets in their own independent windows.
    Children of an MdiArea should be defined as instances of MdiWindow.

    """
    #: An MdiArea expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: An MdiArea resists clipping only weakly by default.
    resist_width = set_default('weak')
    resist_height = set_default('weak')

    #: A reference to the ProxyMdiArea object.
    proxy = Typed(ProxyMdiArea)

    def mdi_windows(self):
        """ Get the mdi windows defined for the area.

        """
        return [c for c in self.children if isinstance(c, MdiWindow)]
