#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem
from .dock_layout import DockLayout


class ProxyDockArea(ProxyConstraintsWidget):
    """ The abstract definition of a proxy DockArea object.

    """
    #: A reference to the Stack declaration.
    declaration = ForwardTyped(lambda: DockArea)

    def set_layout(self, layout):
        raise NotImplementedError


class DockArea(ConstraintsWidget):
    """ A component which aranges dock item children.

    """
    #: The initial layout of dock items for the area.
    layout = d_(Typed(DockLayout))

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyStack widget.
    proxy = Typed(ProxyDockArea)

    def dock_items(self):
        """ Get the dock items defined on the stack

        """
        return [c for c in self.children if isinstance(c, DockItem)]
