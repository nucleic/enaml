#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Coerced, Event, Enum, Str, Unicode, observe

from enaml.core.declarative import Declarative, d_
from enaml.core.messenger import Messenger
from enaml.layout.geometry import Size


class ListItem(Messenger, Declarative):
    """ A non-widget used as an item in a `ListControl`

    A `ListItem` represents an item in a `ListControl`. It contains all
    of the information needed for data and styling.

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

    #: The source url for the icon to use for the item.
    icon_source = d_(Str())

    #: Whether or not the item can be checked by the user. This has no
    #: bearing on whether or not a checkbox is visible for the item.
    #: For controlling the visibility of the checkbox, see `checked`.
    checkable = d_(Bool(False))

    #: Whether or not the item is checked. A value of None indicates
    #: that no check box should be visible for the item.
    checked = d_(Enum(None, False, True))

    #: Whether or not the item can be selected.
    selectable = d_(Bool(True))

    #: Whether or not the item is selected. This value only has meaning
    #: if 'selectable' is set to True.
    selected = d_(Bool(False))

    #: Whether or not the item is editable.
    editable = d_(Bool(False))

    #: Whether or not the item is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the item is visible.
    visible = d_(Bool(True))

    #: The horizontal alignment of the text in the item area.
    text_align = d_(Enum('left', 'right', 'center', 'justify'))

    #: The vertical alignment of the text in the item area.
    vertical_text_align = d_(Enum('center', 'top', 'bottom'))

    #: The preferred size of the item.
    preferred_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: An event fired when the user clicks on the item. The payload
    #: will be the current checked state of the item.
    clicked = Event()

    #: An event fired when the user double clicks on the item. The
    #: payload will be the current checked state of the item.
    double_clicked = Event()

    #: An event fired when the user toggles a checkable item. The
    #: payload will be the current checked state of the item.
    toggled = Event()

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list item.

        """
        snap = super(ListItem, self).snapshot()
        snap['text'] = self.text
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        snap['background'] = self.background
        snap['foreground'] = self.foreground
        snap['font'] = self.font
        snap['icon_source'] = self.icon_source
        snap['checkable'] = self.checkable
        snap['checked'] = self.checked
        snap['selectable'] = self.selectable
        snap['selected'] = self.selected
        snap['editable'] = self.editable
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['text_align'] = self.text_align
        snap['vertical_text_align'] = self.vertical_text_align
        snap['preferred_size'] = self.preferred_size
        return snap

    @observe(r'^(text|tool_tip|status_tip|background|foreground|font|checked|'
             r'icon_source|checkable|selectable|selected|editable|enabled|'
             r'visible|preferred_size|text_align|vertical_text_align)$',
             regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ListItem, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_clicked(self, content):
        """ Handle the 'clicked' action from the client widget.

        """
        self.clicked(self.checked)

    def on_action_double_clicked(self, content):
        """ Handle the 'double_clicked' action from the client widget.

        """
        self.double_clicked(self.checked)

    def on_action_changed(self, content):
        """ Handle the 'changed' action from the client widget.

        """
        old_checked = self.checked
        new_checked = content['checked']
        was_toggled = old_checked != new_checked
        if was_toggled:
            self.set_guarded(checked=new_checked)
        self.set_guarded(text=content['text'])
        if was_toggled:
            self.toggled(new_checked)

