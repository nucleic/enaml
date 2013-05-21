#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Coerced, Enum, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_
from enaml.layout.dock_layout import (
    docklayout, dockarea, dockitem, docksplit, docktabs
)

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem


def coerce_layout(thing):
    """ Coerce a variety of objects into a docklayout.

    Parameters
    ----------
    thing : dict, basetring, dockitem, dockarea, split, or tabs
        Something that can be coerced into a dock layout.

    """
    if isinstance(thing, basestring):
        thing = dockitem(thing)
    if isinstance(thing, (dockitem, docksplit, docktabs)):
        return docklayout(dockarea(thing))
    if isinstance(thing, dockarea):
        return docklayout(thing)
    msg = "cannot coerce '%s' to a 'docklayout'"
    raise TypeError(msg % type(thing).__name__)


class ProxyDockArea(ProxyConstraintsWidget):
    """ The abstract definition of a proxy DockArea object.

    """
    #: A reference to the Stack declaration.
    declaration = ForwardTyped(lambda: DockArea)

    def set_tab_position(self, position):
        raise NotImplementedError

    def save_layout(self):
        raise NotImplementedError

    def apply_layout(self, layout):
        raise NotImplementedError


class DockArea(ConstraintsWidget):
    """ A component which aranges dock item children.

    """
    #: The layout of dock items for the area. The layout can also be
    #: changed at runtime with the 'apply_layout()' method.
    layout = d_(Coerced(docklayout, ('',), coercer=coerce_layout))

    #: The default tab position for newly created dock tabs.
    tab_position = d_(Enum('top', 'bottom', 'left', 'right'))

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

    @observe('tab_position')
    def _update_proxy(self, change):
        """ Update the proxy when the area state changes.

        """
        # The superclass implementation is sufficient.
        super(DockArea, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def save_layout(self):
        """ Get the current dictionary representation of the layout.

        Returns
        -------
        result : docklayout
            The current docklayout state of the dock area.

        """
        if self.proxy_is_active:
            return self.proxy.save_layout()
        return self.layout

    def apply_layout(self, layout):
        """ Apply a layout from a saved layout state.

        Parameters
        ----------
        layout : docklayout
            The docklayout to apply to the dock area.

        """
        assert isinstance(layout, docklayout), 'layout must be a docklayout'
        if self.proxy_is_active:
            return self.proxy.apply_layout(layout)
