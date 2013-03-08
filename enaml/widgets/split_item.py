#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Range, Value, observe

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget


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

    @property
    def split_widget(self):
        """ A read only property that returns the split widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(SplitItem, self).snapshot()
        snap['stretch'] = self.stretch
        snap['collapsible'] = self.collapsible
        return snap

    @observe(r'^(stretch|collapsible)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(SplitItem, self).send_member_change(change)

