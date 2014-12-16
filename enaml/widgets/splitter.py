#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .split_item import SplitItem


class ProxySplitter(ProxyConstraintsWidget):
    """ The abstract definition of a proxy Splitter object.

    """
    #: A reference to the Splitter declaration.
    declaration = ForwardTyped(lambda: Splitter)

    def set_orientation(self, orientation):
        raise NotImplementedError

    def set_live_drag(self, live_drag):
        raise NotImplementedError


class Splitter(ConstraintsWidget):
    """ A widget which displays its children in separate resizable
    compartments that are connected with a resizing bar.

    A Splitter can have an arbitrary number of Container children.

    """
    #: The orientation of the Splitter. 'horizontal' means the children
    #: are laid out left to right, 'vertical' means top to bottom.
    orientation = d_(Enum('horizontal', 'vertical'))

    #: Whether the child widgets resize as a splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = d_(Bool(True))

    #: A splitter expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxySplitter object.
    proxy = Typed(ProxySplitter)

    def split_items(self):
        """ Get the split item children defined on the splitter.

        """
        return [c for c in self.children if isinstance(c, SplitItem)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('orientation', 'live_drag')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(Splitter, self)._update_proxy(change)
