#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_action import WxAction, EVT_ACTION_CHANGED
from .wx_object import WxObject


class wxActionGroup(wx.EvtHandler):
    """ A simple object which keeps track of a group of actions.

    """
    def __init__(self, parent=None):
        """ Initialize a wxActionGroup.

        Parameters
        ----------
        parent : object or None
            The parent for this wxActionGroup. The parent is not used
            directly by the action, but is provided as a convenience
            for other parts of the framework.

        """
        super(wxActionGroup, self).__init__()
        self._parent = parent
        self._exclusive = True
        self._enabled = True
        self._visible = True
        self._actions = []
        self._checked_action = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will update the current checked action and toggle
        any other old action if the group is exclusive.

        """
        event.Skip()
        action = event.GetEventObject()
        if action.IsChecked():
            old_action = self._checked_action
            self._checked_action = action
            if self.IsExclusive():
                if action is not old_action:
                    if old_action is not None:
                        old_action.SetChecked(False)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetParent(self):
        """ Get the parent of the action group.

        Returns
        -------
        result : object or None
            The parent of this action group or None.

        """
        return self._parent

    def SetParent(self, parent):
        """ Set the parent of the action group.

        Parameters
        ----------
        parent : object or None
            The object to use as the parent of this action group.

        """
        self._parent = parent

    def AddAction(self, action):
        """ Add an action to the action group.

        If the action already exists in the group, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction to add to the group.

        """
        actions = self._actions
        if action not in actions:
            actions.append(action)
            action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)
            parent = action.GetParent()
            if isinstance(parent, wxActionGroup) and parent is not self:
                parent.RemoveAction(action)
                action.SetParent(self)

        if action.IsChecked():
            old_action = self._checked_action
            self._checked_action = action
            if self.IsExclusive():
                if action is not old_action:
                    if old_action is not None:
                        old_action.SetChecked(False)

        action._SetGroupEnabled(self._enabled)
        action._SetGroupVisible(self._visible)

    def RemoveAction(self, action):
        """ Remove the action from the action group.

        If the action does not exist in the group, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction to remove from the group.

        """
        actions = self._actions
        if action in actions:
            actions.remove(action)
            action.Unbind(EVT_ACTION_CHANGED, handler=self.OnActionChanged)
            if action is self._checked_action:
                self._checked_action = None

    def GetActions(self):
        """ Get the list of actions for this group.

        Returns
        -------
        result : list
            The list of wxAction instances for this action group. This
            list should not be modified in-place.

        """
        return self._actions

    def GetCheckedAction(self):
        """ Get the currently checked action in the group.

        Returns
        -------
        result : wxAction or None
            The currently checked action in the group, or None if
            no action is checked.

        """
        return self._checked_action

    def IsExclusive(self):
        """ Get whether or not the action group is exclusive.

        Returns
        -------
        result : bool
            Whether or not the action group is exclusive.

        """
        return self._exclusive

    def SetExclusive(self, exclusive):
        """ Set whether or not the action group is exclusive.

        Parameters
        ----------
        exclusive : bool
            Whether or not the action is exclusive.

        """
        if self._exclusive != exclusive:
            self._exclusive = exclusive
            if exclusive:
                curr = self._checked_action
                for action in self._actions:
                    if action is not curr:
                        action.SetChecked(False)

    def IsEnabled(self):
        """ Get whether or not the action group is enabled.

        Returns
        -------
        result : bool
            Whether or not the action group is enabled.

        """
        return self._enabled

    def SetEnabled(self, enabled):
        """ Set whether or not the action group is enabled.

        Parameters
        ----------
        enabled : bool
            Whether or not the action group is enabled.

        """
        if self._enabled != enabled:
            self._enabled = enabled
            for action in self._actions:
                action._SetGroupEnabled(enabled)

    def IsVisible(self):
        """ Get whether or not the action group is visible.

        Returns
        -------
        result : bool
            Whether or not the action group is visible.

        """
        return self._visible

    def SetVisible(self, visible):
        """ Set whether or not the action group is visible.

        Parameters
        ----------
        enabled : bool
            Whether or not the action is visible.

        """
        if self._visible != visible:
            self._visible = visible
            for action in self._actions:
                action._SetGroupVisible(visible)


class WxActionGroup(WxObject):
    """ A Wx implementation of an Enaml ActionGroup.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying action group widget.

        """
        return wxActionGroup(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(WxActionGroup, self).create(tree)
        self.set_exclusive(tree['exclusive'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(WxActionGroup, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, WxAction):
                widget.AddAction(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a WxActionGroup.

        """
        if isinstance(child, WxAction):
            action = child.widget()
            self.widget().RemoveAction(action)
            parent = self.parent()
            if parent is not None:
                parent.widget().RemoveAction(action)

    def child_added(self, child):
        """ Handle the child added event for a WxActionGroup.

        """
        # The easiest way to handle the insert is to tell the parent to
        # insert all the current actions. It will work out the proper
        # ordering automatically.
        if isinstance(child, WxAction):
            self.widget().AddAction(child.widget())
            parent = self.parent()
            if parent is not None:
                before = parent.find_next_action(self)
                parent.widget().InsertActions(before, self.actions())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def actions(self):
        """ Get the WxAction children for this action group.

        Returns
        -------
        result : list
            The list of wxAction instances which are children of this
            action group. Unlike the list returned by the `GetActions`
            method of the wxActionGroup, the children in this list will
            have the correct order.

        """
        isinst = isinstance
        return [c.widget() for c in self.children() if isinst(c, WxAction)]

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_exclusive(self, content):
        """ Handle the 'set_exclusive' action from the Enaml widget.

        """
        self.set_exclusive(content['exclusive'])

    def on_action_set_enabled(self, content):
        """ Handle the 'set_enabled' action from the Enaml widget.

        """
        self.set_enabled(content['enabled'])

    def on_action_set_visible(self, content):
        """ Handle the 'set_visible' action from the Enaml widget.

        """
        self.set_visible(content['visible'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_exclusive(self, exclusive):
        """ Set the exclusive state of the underlying control.

        """
        self.widget().SetExclusive(exclusive)

    def set_enabled(self, enabled):
        """ Set the enabled state of the underlying control.

        """
        self.widget().SetEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visible state of the underlying control.

        """
        self.widget().SetVisible(visible)

