#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from weakref import WeakValueDictionary

import wx
import wx.lib.newevent

from .wx_object import WxObject


#: An event emitted when a wxAction has been triggered by the user. The
#: payload of the event will have an 'IsChecked' attribute.
wxActionTriggeredEvent, EVT_ACTION_TRIGGERED = wx.lib.newevent.NewEvent()

#: An event emitted by a wxAction when it has been toggled by the user.
#: The payload of the event will have an 'IsChecked' attribute.
wxActionToggledEvent, EVT_ACTION_TOGGLED = wx.lib.newevent.NewEvent()

#: An event emitted by a wxAction when its state has been changed.
wxActionChangedEvent, EVT_ACTION_CHANGED = wx.lib.newevent.NewEvent()


class wxAction(wx.EvtHandler):
    """ A wx.EvtHandler which behaves similar to a QAction.

    """
    #: Class storage which maps action id -> action instance.
    _action_map = WeakValueDictionary()

    @classmethod
    def FindById(cls, action_id):
        """ Find a wxAction instance using the given action id.

        Parameters
        ----------
        action_id : int
            The id for the action.

        Returns
        -------
        result : wxAction or None
            The wxAction instance for the given id, or None if not
            action exists for that id.

        """
        return cls._action_map.get(action_id)

    def __init__(self, parent=None):
        """ Initialize a wxAction.

        Parameters
        ----------
        parent : object or None
            The parent for this wxAction. The parent is not directly
            used by the action, but is provided as a convenience for
            other parts of the framework.

        """
        super(wxAction, self).__init__()
        self._parent = parent
        self._text = u''
        self._tool_tip = u''
        self._status_tip = u''
        self._checkable = False
        self._checked = False
        self._enabled = True
        self._visible = True
        self._group_enabled = True
        self._group_visible = True
        self._separator = False
        self._batch = False
        self._id = wx.NewId()
        self._action_map[self._id] = self

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _EmitChanged(self):
        """ Emits the EVT_ACTION_CHANGED event if not in batch mode.

        """
        if not self._batch:
            event = wxActionChangedEvent()
            event.SetEventObject(self)
            wx.PostEvent(self, event)

    def _SetGroupEnabled(self, enabled):
        """ A private method called by an owner action group.

        Parameters
        ----------
        enabled : bool
            Whether or not the owner group is enabled.

        """
        if self._group_enabled != enabled:
            old = self.IsEnabled()
            self._group_enabled = enabled
            new = self.IsEnabled()
            if old != new:
                self._EmitChanged()

    def _SetGroupVisible(self, visible):
        """ A private method called by an owner action group.

        Parameters
        ----------
        visible : bool
            Whether or not the owner group is visble.

        """
        if self._group_visible != visible:
            old = self.IsVisible()
            self._group_visible = visible
            new = self.IsVisible()
            if old != new:
                self._EmitChanged()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetParent(self):
        """ Get the parent of the action.

        Returns
        -------
        result : object or None
            The parent of this action or None.

        """
        return self._parent

    def SetParent(self, parent):
        """ Set the parent of the action.

        Parameters
        ----------
        parent : object or None
            The object to use as the parent of this action.

        """
        self._parent = parent

    def Trigger(self):
        """ A method called by the action owner when the user triggers
        the action.

        This handler will emit the custom EVT_ACTION_TRIGGERED event.
        User code should not typically call this method directly.

        """
        # This event is dispatched immediately in order to preserve
        # the order of event firing for trigger/toggle.
        event = wxActionTriggeredEvent(IsChecked=self._checked)
        event.SetEventObject(self)
        wx.PostEvent(self, event)

    def BeginBatch(self):
        """ Enter batch update mode for the action.

        """
        self._batch = True

    def EndBatch(self, emit=True):
        """ Exit batch update mode for the action.

        Parameters
        ----------
        emit : bool, optional
            If True, emit a changed event after leaving batch mode. The
            default is True.

        """
        self._batch = False
        if emit:
            self._EmitChanged()

    def GetId(self):
        """ Get the unique wx id for this action.

        Returns
        -------
        result : int
            The wx id number for this action.

        """
        return self._id

    def GetText(self):
        """ Get the text for the action.

        Returns
        -------
        result : unicode
            The unicode text for the action.

        """
        return self._text

    def SetText(self, text):
        """ Set the text for the action.

        Parameters
        ----------
        text : unicode
            The unicode text for the action.

        """
        if self._text != text:
            self._text = text
            self._EmitChanged()

    def GetToolTip(self):
        """ Get the tool tip for the action.

        Returns
        -------
        result : unicode
            The unicode tool tip for the action.

        """
        return self._tool_tip

    def SetToolTip(self, tool_tip):
        """ Set the tool tip for the action.

        Parameters
        ----------
        tool_tip : unicode
            The unicode tool tip for the action.

        """
        if self._tool_tip != tool_tip:
            self._tool_tip = tool_tip
            self._EmitChanged()

    def GetStatusTip(self):
        """ Get the status tip for the action.

        Returns
        -------
        result : unicode
            The unicode status tip for the action.

        """
        return self._status_tip

    def SetStatusTip(self, status_tip):
        """ Set the status tip for the action.

        Parameters
        ----------
        status_tip : unicode
            The unicode status tip for the action.

        """
        if self._status_tip != status_tip:
            self._status_tip = status_tip
            self._EmitChanged()

    def IsCheckable(self):
        """ Get whether or not the action is checkable.

        Returns
        -------
        result : bool
            Whether or not the action is checkable.

        """
        return self._checkable

    def SetCheckable(self, checkable):
        """ Set whether or not the action is checkable.

        Parameters
        ----------
        checkable : bool
            Whether or not the action is checkable.

        """
        if self._checkable != checkable:
            self._checkable = checkable
            self._EmitChanged()

    def IsChecked(self):
        """ Get whether or not the action is checked.

        Returns
        -------
        result : bool
            Whether or not the action is checked.

        """
        return self._checked

    def SetChecked(self, checked):
        """ Set whether or not the action is checked.

        Parameters
        ----------
        checked : bool
            Whether or not the action is checked.

        """
        if self._checked != checked:
            self._checked = checked
            self._EmitChanged()
            event = wxActionToggledEvent(IsChecked=checked)
            event.SetEventObject(self)
            wx.PostEvent(self, event)

    def IsEnabled(self):
        """ Get whether or not the action is enabled.

        Returns
        -------
        result : bool
            Whether or not the action is enabled.

        """
        if self._group_enabled:
            return self._enabled
        return False

    def SetEnabled(self, enabled):
        """ Set whether or not the action is enabled.

        Parameters
        ----------
        enabled : bool
            Whether or not the action is enabled.

        """
        if self._enabled != enabled:
            self._enabled = enabled
            if self._group_enabled:
                self._EmitChanged()

    def IsVisible(self):
        """ Get whether or not the action is visible.

        Returns
        -------
        result : bool
            Whether or not the action is visible.

        """
        if self._group_visible:
            return self._visible
        return False

    def SetVisible(self, visible):
        """ Set whether or not the action is visible.

        Parameters
        ----------
        visible : bool
            Whether or not the action is visible.

        """
        if self._visible != visible:
            self._visible = visible
            if self._group_visible:
                self._EmitChanged()

    def IsSeparator(self):
        """ Get whether or not the action is a separator.

        Returns
        -------
        result : bool
            Whether or not the action is a separator.

        """
        return self._separator

    def SetSeparator(self, separator):
        """ Set whether or not the action is a separator.

        Parameters
        ----------
        separator : bool
            Whether or not the action is a separator.

        """
        if self._separator != separator:
            self._separator = separator
            self._EmitChanged()


class WxAction(WxObject):
    """ A Wx implementation of an Enaml Action.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxAction object.

        """
        return wxAction(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(WxAction, self).create(tree)
        widget = self.widget()
        widget.BeginBatch()
        self.set_text(tree['text'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_status_tip(tree['status_tip'])
        self.set_checkable(tree['checkable'])
        self.set_checked(tree['checked'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])
        self.set_separator(tree['separator'])
        widget.EndBatch(emit=False)
        widget.Bind(EVT_ACTION_TRIGGERED, self.on_triggered)
        widget.Bind(EVT_ACTION_TOGGLED, self.on_toggled)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_triggered(self, event):
        """ The event handler for the EVT_ACTION_TRIGGERED event.

        """
        content = {'checked': event.IsChecked}
        self.send_action('triggered', content)

    def on_toggled(self, event):
        """ The event handler for the EVT_ACTION_TOGGLED event.

        """
        content = {'checked': event.IsChecked}
        self.send_action('toggled', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_tool_tip(self, content):
        """ Handle the 'set_tool_tip' action from the Enaml widget.

        """
        self.set_tool_tip(content['tool_tip'])

    def on_action_set_status_tip(self, content):
        """ Handle the 'set_status_tip' action from the Enaml widget.

        """
        self.set_status_tip(content['status_tip'])

    def on_action_set_checkable(self, content):
        """ Handle the 'set_checkable' action from the Enaml widget.

        """
        self.set_checkable(content['checkable'])

    def on_action_set_checked(self, content):
        """ Handle the 'set_checked' action from the Enaml widget.

        """
        self.set_checked(content['checked'])

    def on_action_set_enabled(self, content):
        """ Handle the 'set_enabled' action from the Enaml widget.

        """
        self.set_enabled(content['enabled'])

    def on_action_set_visible(self, content):
        """ Handle the 'set_visible' action from the Enaml widget.

        """
        self.set_visible(content['visible'])

    def on_action_set_separator(self, content):
        """ Handle the 'set_separator' action from the Enaml widget.

        """
        self.set_separator(content['separator'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text on the underlying control.

        """
        self.widget().SetText(text)

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip on the underlying control.

        """
        self.widget().SetToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip on the underyling control.

        """
        self.widget().SetStatusTip(status_tip)

    def set_checkable(self, checkable):
        """ Set the checkable state on the underlying control.

        """
        self.widget().SetCheckable(checkable)

    def set_checked(self, checked):
        """ Set the checked state on the underlying control.

        """
        self.widget().SetChecked(checked)

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying control.

        """
        self.widget().SetEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visible state on the underlying control.

        """
        self.widget().SetVisible(visible)

    def set_separator(self, separator):
        """ Set the separator state on the underlying control.

        """
        self.widget().SetSeparator(separator)

