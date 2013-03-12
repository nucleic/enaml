#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Int, Typed, Value, Str, Unicode, Callable, Signal, observe
)

from enaml.core.declarative import Declarative, d_
from enaml.datamodels.enums import ItemFlag, AlignmentFlag, CheckState
from enaml.icon import Icon


class ListItem(Declarative):
    """ A non-widget used as an item in a `ListView`

    A `ListItem` represents an item in a `ListView`. It contains all of
    the information needed for data and styling. It is more heavyweight
    that creating an AbstractItemModel directly, but can be useful for
    smaller declarative models

    """
    #: The text to display in the item.
    text = d_(Unicode())

    #: The tool tip to use for the item.
    tool_tip = d_(Unicode())

    #: The status tip to use for the item.
    status_tip = d_(Unicode())

    #: The background color of the item. Supports CSS3 color strings.
    background = d_(Str())

    #: The foreground color of the item. Supports CSS3 color strings.
    foreground = d_(Str())

    #: The font used for the widget. Supports CSS3 shorthand font strings.
    font = d_(Str())

    #: The icon to use for the item.
    icon = d_(Typed(Icon))

    #: An or'd combination of ItemFlag values.
    flags = d_(Int(ItemFlag.ITEM_IS_ENABLED | ItemFlag.ITEM_IS_SELECTABLE))

    #: One of the CheckState enum values.
    check_state = d_(Int(CheckState.UNCHECKED))

    #: The alignment of the text in the item area.
    text_alignment = d_(Int(AlignmentFlag.ALIGN_CENTER))

    #: The size hint of the item. This is None or a 2-tuple of ints.
    size_hint = d_(Value())

    #: A callable which will be invoked the the change from the item when
    #: any of its data changes. There can only be one notifier installed
    #: at a time. This can be more space efficient than observing the data
    #: changed signal if there is only one observer.
    notifier = Callable()

    #: A signal emitted when any of the data changes on the item.
    data_changed = Signal()

    @observe(('text', 'tool_tip', 'status_tip', 'background', 'foreground',
        'font', 'icon', 'flags', 'check_state', 'alignment', 'preferred_size'))
    def _on_item_changed(self, change):
        """ An observer which sends state change to the client.

        """
        notifier = self.notifer
        if notifier:
            notifier(change)
        self.data_changed.emit(change)
