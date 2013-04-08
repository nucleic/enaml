#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, List, Typed, ForwardTyped, Bool, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem


class docklayout(Atom):
    """ A base class for defining dock layout items.

    """
    def flat(self):
        """ Iterate over the flattened DockItems in the layout.

        """
        raise NotImplementedError


class docksplit(docklayout):
    """ A docklayout which arranges items in a splitter.

    """
    #: The orientation of the splitter.
    orientation = Enum('horizontal', 'vertical')

    #: The docklayout items to include in the splitter.
    items = List()

    #: The suggested initial sizes to apply to the items.
    sizes = List(int)

    def __init__(self, *items, **kwargs):
        super(docksplit, self).__init__(**kwargs)
        these = self.items
        orient = self.orientation
        for item in items:
            if not isinstance(item, (DockItem, docklayout)):
                msg = 'The items in a docksplit must be docklayout or '
                msg += 'DockItem instances. Got object of type %s intead.'
                raise TypeError(msg % type(item).__name__)
            # simplify nested dock splits of like-orientation
            if isinstance(item, docksplit) and item.orientation == orient:
                these.extend(item.items)
            else:
                these.append(item)

    def flat(self):
        """ Iterate over the flattened DockItems in the layout.

        """
        for item in self.items:
            if isinstance(item, DockItem):
                yield item
            else:
                for ditem in item.flat():
                    yield ditem


class hsplit(docksplit):
    """ A convenience subclass for creating a horizontal docksplit.

    """
    orientation = set_default('horizontal')


class vsplit(docksplit):
    """ A convenience subclass for creating a vertical docksplit.

    """
    orientation = set_default('vertical')


class tabbed(docklayout):
    """ A docklayout which arranges its items in a tabbed container.

    """
    #: The style of tabs to use for the tab layout.
    tab_style = d_(Enum('document', 'preferences'))

    #: The position of the tabs on the tab widget.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: Whether or not the tabs are movable.
    tabs_movable = Bool(True)

    #: The DockItem instances to include in the tabbed layout.
    items = List()

    def __init__(self, *items, **kwargs):
        super(tabbed, self).__init__(**kwargs)
        these = self.items
        for item in items:
            if not isinstance(item, DockItem):
                msg = 'The items in a tabbed layout must be DockItem '
                msg += 'instances. Got object of type %s intead.'
                raise TypeError(msg % type(item).__name__)
            these.append(item)

    def flat(self):
        """ Iterate over the flattened DockItems in the layout.

        """
        return iter(self.items)


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
    layout = d_(Typed(docklayout))

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyStack widget.
    proxy = Typed(ProxyDockArea)

    def dock_items(self):
        """ Get the dock items defined on the stack

        """
        return [c for c in self.children if isinstance(c, DockItem)]

    def resolve_layout(self):
        """ Resolve the final layout for the dock area.

        This method will validate and fixup the user-supplied layout.
        If the layout contains invalid children, an exception will be
        raised. If the layout does not contain all of the children,
        the extra children will be added to a tabbed area.

        """
        layout = self.layout
        dock_items = self.dock_items()
        if layout is None:
            return tabbed(*dock_items)
        remaining = dock_items[:]
        for item in layout.flat():
            try:
                remaining.remove(item)
            except ValueError:
                msg = 'DockArea layout contains a non-child DockItem'
                raise ValueError(msg)
        if remaining:
            layout = hsplit(layout, tabbed(*remaining))
        return layout
