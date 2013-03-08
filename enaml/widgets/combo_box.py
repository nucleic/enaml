#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, List, Int, CachedProperty, Unicode, set_default, observe
)

from enaml.core.declarative import d_

from .control import Control


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

    #: A readonly property that will return the currently selected
    #: item. If the index falls out of range, the selected item will
    #: be the empty string.
    selected_item = CachedProperty(Unicode())

    #: A combo box hugs its width weakly by default.
    hug_width = set_default('weak')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the control.

        """
        snap = super(ComboBox, self).snapshot()
        snap['items'] = self.items
        snap['index'] = self.index
        snap['editable'] = self.editable
        return snap

    @observe(r'^(index|items|editable)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ComboBox, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_index_changed(self, content):
        """ The message handler for the 'index_changed' action from the
        client widget. The content will contain the selected 'index'.

        """
        index = content['index']
        self.set_guarded(index=index)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(r'^(index|items)$', regex=True)
    def _reset_selected_item(self, change):
        CachedProperty.reset(self, 'selected_item')

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    def _get_selected_item(self):
        """ The getter for the `selected_item` property.

        """
        items = self.items
        idx = self.index
        if idx < 0 or idx >= len(items):
            return u''
        return items[idx]

