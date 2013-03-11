#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyStackItem(ProxyWidget):
    """ The abstract definition of a proxy StackItem object.

    """
    #: A reference to the StackItem declaration.
    declaration = ForwardTyped(lambda: StackItem)


class StackItem(Widget):
    """ A widget which can be used as an item in a Stack.

    A StackItem is a widget which can be used as a child of a Stack
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: A reference to the ProxyStackItem object.
    proxy = Typed(ProxyStackItem)

    def stack_widget(self):
        """ Get the stack widget defined for the item.

        The stack widget is the last child Container.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child
