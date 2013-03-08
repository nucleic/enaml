#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Bool, Str, TypedEvent, observe

from enaml.core.declarative import Declarative, d_
from enaml.core.messenger import Messenger


class Action(Messenger, Declarative):
    """ A non visible widget used in a ToolBar or Menu.

    An Action represents an actionable item in a ToolBar or a Menu.
    Though an Action itself is a non-visible component, it will be
    rendered in an appropriate fashion for the location where it is
    used.

    """
    #: The text label associate with the action.
    text = d_(Unicode())

    #: The tool tip text to use for this action. Typically displayed
    #: as a small label when the user hovers over the action.
    tool_tip = d_(Unicode())

    #: The text that is displayed in the status bar when the user
    #: hovers over the action.
    status_tip = d_(Unicode())

    #: The source url for the icon to use for the Action.
    icon_source = d_(Str())

    #: Whether or not the action can be checked.
    checkable = d_(Bool(False))

    #: Whether or not the action is checked. This value only has meaning
    #: if 'checkable' is set to True.
    checked = d_(Bool(False))

    #: Whether or not the item representing the action is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the item representing the action is visible.
    visible = d_(Bool(True))

    #: Whether or not the action should be treated as a separator. If
    #: this value is True, none of the other values have meaning.
    separator = d_(Bool(False))

    #: An event fired when the action is triggered by user interaction.
    #: They payload will be the current checked state.
    triggered = TypedEvent(bool)

    #: An event fired when a checkable action changes its checked state.
    #: The payload will be the current checked state.
    toggled = TypedEvent(bool)

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the Action.

        """
        snap = super(Action, self).snapshot()
        snap['text'] = self.text
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        snap['icon_source'] = self.icon_source
        snap['checkable'] = self.checkable
        snap['checked'] = self.checked
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['separator'] = self.separator
        return snap

    #--------------------------------------------------------------------------
    # Action Updates
    #--------------------------------------------------------------------------
    @observe(r'^(text|tool_tip|status_tip|icon_source|checkable|checked|'
             r'enabled|visible|separator)$', regex=True)
    def send_member_change(self, change):
        """ An observer for the changes for the action sate.

        """
        # The superclass implementation is sufficient
        super(Action, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_triggered(self, content):
        """ Handle the 'triggered' action from the client widget.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.triggered(checked)

    def on_action_toggled(self, content):
        """ Handle the 'toggled' action from the client widget.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)

