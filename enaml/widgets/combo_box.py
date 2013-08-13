#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from functools import partial

from atom.api import (
    Bool, List, Int, Unicode, Typed, ForwardTyped, set_default, observe,
    cached_property
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyComboBox(ProxyControl):
    """ The abstract defintion of a proxy ComboBox object.

    """
    #: A reference to the ComboBox declaration.
    declaration = ForwardTyped(lambda: ComboBox)

    def set_items(self, items):
        raise NotImplementedError

    def set_index(self, index):
        raise NotImplementedError

    def set_editable(self, editable):
        raise NotImplementedError


class ComboBox(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.

    """
    #: The unicode strings to display in the combo box.
    items = d_(List(Unicode()))

    #: The integer index of the currently selected item. If the given
    #: index falls outside of the range of items, the item will be
    #: deselected.
    index = d_(Int(-1))

    #: Whether the text in the combo box can be edited by the user.
    editable = d_(Bool(False))

    #: A combo box hugs its width weakly by default.
    hug_width = set_default('weak')

    #: A reference to the ProxyComboBox object.
    proxy = Typed(ProxyComboBox)

    @partial(d_, writable=False)
    @cached_property
    def selected_item(self):
        """ A read only cached property which returns the selected item.

        If the index falls out of range, the selected item will be an
        empty string.

        """
        items = self.items
        idx = self.index
        if idx < 0 or idx >= len(items):
            return u''
        return items[idx]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('index', 'items', 'editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ComboBox, self)._update_proxy(change)

    @observe('index', 'items')
    def _reset_selected_item(self, change):
        """ Reset the selected item when the index or items changes.

        """
        if change['type'] == 'update':
            self.get_member('selected_item').reset(self)
