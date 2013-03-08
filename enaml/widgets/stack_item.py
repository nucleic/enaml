#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .container import Container
from .widget import Widget


class StackItem(Widget):
    """ A widget which can be used as an item in a Stack.

    A StackItem is a widget which can be used as a child of a Stack
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    @property
    def stack_widget(self):
        """ A read only property which returns the item's stack widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

