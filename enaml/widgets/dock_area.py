#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Dict, Typed, ForwardTyped, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem


def _split(orientation, *items, **metadata):
    """ A private function for creating a splitter layout dict.

    """
    layout = {'type': 'split', 'orientation': orientation}
    children = []
    for item in items:
        if isinstance(item, basestring):
            item = {'type': 'item', 'name': item}
        children.append(item)
    layout['children'] = children
    return layout


def hsplit(*items, **metadata):
    """ A function for creating a horizontal splitter layout dict.

    Parameters
    ----------
    *items
        The items to include in the split layout. Strings will be
        promoted to items automatically.

    **metadata
        Additional configuration data for the layout.

    """
    return _split('horizontal', *items, **metadata)


def vsplit(*items, **metadata):
    """ A function for creating a vertical splitter layout dict.

    Parameters
    ----------
    *items
        The items to include in the split layout. Strings will be
        promoted to items automatically.

    **metadata
        Additional configuration data for the layout.

    """
    return _split('vertical', *items, **metadata)


def tabbed(*items, **metadata):
    """ A function for creating a tabbed layout dict.

    Parameters
    ----------
    *items
        The items to include in the tabbed layout. Strings will be
        promoted to items automatically.

    **metadata
        Additional configuration data for the layout.

    """
    style = metadata.get('tab_style', 'document')
    movable = metadata.get('tabs_movable', True)
    position = metadata.get('tab_position', 'top')
    assert style in ('document', 'preferences')
    assert movable in (True, False)
    assert position in ('top', 'right', 'bottom', 'left')
    layout = {'type': 'tabbed'}
    layout['tab_style'] = style
    layout['tabs_movable'] = movable
    layout['tab_position'] = position
    children = []
    for item in items:
        if isinstance(item, basestring):
            item = {'type': 'item', 'name': item}
        children.append(item)
    layout['children'] = children
    return layout


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
    layout = d_(Dict())

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyStack widget.
    proxy = Typed(ProxyDockArea)

    def dock_items(self):
        """ Get the dock items defined on the stack

        """
        return [c for c in self.children if isinstance(c, DockItem)]
