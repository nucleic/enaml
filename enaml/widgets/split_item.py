#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Range, Value, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget, ProxyWidget


class ProxySplitItem(ProxyWidget):
    """ The abstract definition of a proxy SplitItem object.

    """
    #: A reference to the SplitItem declaration.
    declaration = ForwardTyped(lambda: SplitItem)

    def set_stretch(self, stretch):
        raise NotImplementedError

    def set_collapsible(self, collapsible):
        raise NotImplementedError


class SplitItem(Widget):
    """ A widget which can be used as an item in a Splitter.

    A SplitItem is a widget which can be used as a child of a Splitter
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The stretch factor for this item. The stretch factor determines
    #: how much an item is resized relative to its neighbors when the
    #: splitter space is allocated.
    stretch = d_(Range(low=0, value=1))

    #: Whether or not the item can be collapsed to zero width by the
    #: user. This holds regardless of the minimum size of the item.
    collapsible = d_(Bool(True))

    #: This is a deprecated attribute. It should no longer be used.
    preferred_size = d_(Value())

    #: A reference to the ProxySplitItem object.
    proxy = Typed(ProxySplitItem)

    def split_widget(self):
        """ Get the split widget defined on the item.

        The split widget is the last child Container.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('stretch', 'collapsible'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(SplitItem, self)._update_proxy(change)
