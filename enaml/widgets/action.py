#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Unicode, Bool, Event, observe

from enaml.core.declarative import d_
from enaml.icon import Icon

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyAction(ProxyToolkitObject):
    """ The abstract definition of a proxy Action object.

    """
    #: A reference to the Action declaration.
    declaration = ForwardTyped(lambda: Action)

    def set_text(self, text):
        raise NotImplementedError

    def set_tool_tip(self, tool_tip):
        raise NotImplementedError

    def set_status_tip(self, status_tip):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def set_checkable(self, checkable):
        raise NotImplementedError

    def set_checked(self, checked):
        raise NotImplementedError

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_visible(self, visible):
        raise NotImplementedError

    def set_separator(self, separator):
        raise NotImplementedError


class Action(ToolkitObject):
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

    #: The icon to use for the Action.
    icon = d_(Typed(Icon))

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
    #: They payload will be the current checked state. This event is
    #: triggered by the proxy object when the action is triggerd.
    triggered = d_(Event(bool), writable=False)

    #: An event fired when a checkable action changes its checked state.
    #: The payload will be the current checked state. This event is
    #: triggerd by the proxy object when the action is toggled.
    toggled = d_(Event(bool), writable=False)

    #: A reference to the ProxyAction object.
    proxy = Typed(ProxyAction)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('text', 'tool_tip', 'status_tip', 'icon', 'checkable', 'checked',
        'enabled', 'visible', 'separator'))
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the Action changes.

        """
        # The superclass implementation is sufficient
        super(Action, self)._update_proxy(change)
