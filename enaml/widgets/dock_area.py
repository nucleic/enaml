#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Dict, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem


def item(name):
    """ A function for creating a layout dict for an item.

    Parameters
    ----------
    name : basestring
        The name of the dock item to use at this point in the layout.

    """
    return {'type': 'item', 'name': name}


def _split(orientation, *children, **metadata):
    """ A private function for creating a splitter layout dict.

    """
    layout = {'type': 'split', 'orientation': orientation}
    kids = []
    for child in children:
        if isinstance(child, basestring):
            child = item(child)
        kids.append(child)
    layout['children'] = kids
    return layout


def hsplit(*children, **metadata):
    """ A function for creating a horizontal splitter layout dict.

    Parameters
    ----------
    *children
        The child items to include in the split layout. Strings will
        be promoted to items automatically.

    **metadata
        Additional configuration data for the layout.

    """
    return _split('horizontal', *children, **metadata)


def vsplit(*children, **metadata):
    """ A function for creating a vertical splitter layout dict.

    Parameters
    ----------
    *children
        The child items to include in the split layout. Strings will
        be promoted to items automatically.

    **metadata
        Additional configuration data for the layout.

    """
    return _split('vertical', *children, **metadata)


def tabbed(*children, **metadata):
    """ A function for creating a tabbed layout dict.

    Parameters
    ----------
    *children
        The child items to include in the tabbed layout. Strings will
        be promoted to items automatically.

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
    kids = []
    for child in children:
        if isinstance(child, basestring):
            child = item(child)
        kids.append(child)
    layout['children'] = kids
    return layout


def floated(child, **metadata):
    """ A function to creating a floating dock area.

    Parameters
    ----------
    child : dict
        The dict describing how to layout the floating child item.

    **metadata
        Additional configuration data for the layout.

    """
    layout = {'type': 'floated'}
    if isinstance(child, basestring):
        child = item(child)
    layout['child'] = child
    return layout


def docklayout(primary, *secondary):
    """ A function for creating a dock layout.

    Parameters
    ----------
    primary : dict
        The layout dict for the primary dock area.

    *floated
        An iterable of dicts for secondary floating areas.

    """
    assert primary['type'] in ('split', 'tabbed', 'item')
    layout = {'type': 'docklayout'}
    valid = []
    for other in secondary:
        if other['type'] != 'floated':
            msg = "Secondary layouts must be 'floated' layouts. Got layout "
            msg += "of type '%s' instead." % other['type']
            raise TypeError(msg)
        valid.append(other)
    layout['primary'] = primary
    layout['secondary'] = valid
    return layout


class ProxyDockArea(ProxyConstraintsWidget):
    """ The abstract definition of a proxy DockArea object.

    """
    #: A reference to the Stack declaration.
    declaration = ForwardTyped(lambda: DockArea)

    def save_layout(self):
        raise NotImplementedError

    def apply_layout(self, layout):
        raise NotImplementedError


class DockArea(ConstraintsWidget):
    """ A component which aranges dock item children.

    """
    #: The layout of dock items for the area. The layout can also be
    #: changed at runtime with the 'apply_layout()' method.
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

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('layout')
    def _update_layout(self, change):
        """ An observer which updates the layout when it changes.

        """
        if change['type'] == 'update':
            self.apply_layout(change['value'])

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def save_layout(self):
        """ Get the current dictionary representation of the layout.

        Returns
        -------
        result : dict
            The current layout state of the dock area.

        """
        if self.proxy_is_active:
            return self.proxy.save_layout()
        return self.layout

    def apply_layout(self, layout):
        """ Apply a layout from a saved layout state.

        Parameters
        ----------
        layout : dict
            The layout description dictionary to apply to the area.

        """
        if self.proxy_is_active:
            return self.proxy.apply_layout(layout)
