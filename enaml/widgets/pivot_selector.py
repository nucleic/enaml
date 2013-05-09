#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from functools import partial

from atom.api import (
    Int, List, Event, Unicode, ForwardTyped, Typed, set_default, observe,
    cached_property
)

from enaml.core.declarative import d_

from enaml.widgets.control import Control, ProxyControl


class ProxyPivotSelector(ProxyControl):
    """ The abstract definition of a proxy PivotSelector widget

    """
    #: A reference to the PivotSelector declaration
    declaration = ForwardTyped(lambda: PivotSelector)

    def set_items(self, items):
        raise NotImplementedError

    def set_index(self, index):
        raise NotImplementedError

    def set_offset(self, offset):
        raise NotImplementedError


class PivotSelector(Control):
    """ An ordered list of pivots which describe the current pivot hierarchy.

    Use the pivot selector to drill down/up in a pivot data model

    """
    #: The unicode strings to display as the pivot levels
    items = d_(List(Unicode()))

    #: The integer index of the currently selected item
    index = d_(Int(0))

    #: The integer index of the currently selected item
    offset = d_(Int(0))

    #: The integer index of a clicked event
    clicked = d_(Event(int), writable=False)

    #: A reference to the ProxyPivotSelector object
    proxy = Typed(ProxyPivotSelector)

    @partial(d_, writable=False)
    @cached_property
    def selected_item(self):
        """ A read only cached property which returns the selected item.

        If the index falls out of range, the selected item will be an
        empty string.

        """
        items = self.items
        idx = self.index+self.offset
        if idx < 0 or idx >= len(items):
            return u''
        return items[idx]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('index', 'items', 'offset'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(PivotSelector, self)._update_proxy(change)

    @observe(('index', 'items'))
    def _reset_selected_item(self, change):
        """ Reset the selected item when the index or items changes.

        """
        self.get_member('selected_item').reset(self)
