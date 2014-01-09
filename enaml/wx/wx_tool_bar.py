#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.tool_bar import ProxyToolBar

from .wx_action import WxAction, EVT_ACTION_CHANGED
from .wx_action_group import WxActionGroup
from .wx_constraints_widget import WxConstraintsWidget


#: A mapping from Enaml orientation to wx Orientation
_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class wxToolBar(wx.ToolBar):
    """ A wx.ToolBar subclass which handles wxAction instances.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxToolBar.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments needed to initialize
            an AuiToolBar.

        """
        super(wxToolBar, self).__init__(*args, **kwargs)
        self._all_items = []
        self._actions_map = {}

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _InsertAction(self, index, action):
        """ Insert a new tool into the tool bar for the given action.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to add to the tool bar.

        Returns
        -------
        result : wxToolBarToolBase
            The tool base item created when adding the control to the
            tool bar.

        """
        if action.IsSeparator():
            item = self.InsertSeparator(index)
        else:
            text = action.GetText()
            short_help = action.GetToolTip()
            long_help = action.GetStatusTip()
            action_id = action.GetId()
            bmp = wx.EmptyBitmap(0, 0)
            if action.IsCheckable():
                item = self.InsertLabelTool(
                    index, action_id, text, bmp, kind=wx.ITEM_CHECK,
                    shortHelp=short_help, longHelp=long_help,
                )
                if action.IsChecked() != item.IsToggled():
                    item.Toggle()
            else:
                item = self.InsertLabelTool(
                    index, action_id, text, bmp, kind=wx.ITEM_NORMAL,
                    shortHelp=short_help, longHelp=long_help,
                )
            item.Enable(action.IsEnabled())
        return item

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will be called when a child action changes. It
        ensures that the new state of the child action is in sync with
        the associated tool bar item.

        """
        event.Skip()
        action = event.GetEventObject()
        item = self._actions_map.get(action)

        # Handle a visibility change. The tool must be added/removed.
        visible = action.IsVisible()
        if visible != bool(item):
            if visible:
                index = self._all_items.index(action)
                index = min(index, len(self._actions_map))
                new_item = self._InsertAction(index, action)
                self._actions_map[action] = new_item
                self.Realize()
            else:
                self.DeleteTool(item.GetId())
                del self._actions_map[action]
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # Handle a separator change. The existing tool must be replaced.
        if action.IsSeparator() != item.IsSeparator():
            self.DeleteTool(item.GetId())
            del self._actions_map[action]
            index = self._all_items.index(action)
            index = min(index, len(self._actions_map))
            new_item = self._InsertAction(index, action)
            self._actions_map[action] = new_item
            self.Realize()
            return

        # Handle a checkable change. The existing too must be replaced.
        if action.IsCheckable() != item.CanBeToggled():
            self.DeleteTool(item.GetId())
            del self._actions_map[action]
            index = self._all_items.index(action)
            index = min(index, len(self._actions_map))
            new_item = self._InsertAction(index, action)
            self._actions_map[action] = new_item
            self.Realize()
            return

        # All other state can be updated in-place.
        item.SetLabel(action.GetText())
        item.SetShortHelp(action.GetToolTip())
        item.SetLongHelp(action.GetStatusTip())
        if action.IsCheckable():
            if action.IsChecked() != item.IsToggled():
                item.Toggle()
        item.Enable(action.IsEnabled())
        self.Realize()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def AddAction(self, action, realize=True):
        """ Add an action to the tool bar.

        If the action already exists in the toolbar, it will be moved
        to the end.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to add to the tool bar.

        realize : bool, optional
            Whether the toolbar should realize the change immediately.
            If False, Realize() will need to be called manually once
            all desired changes have been made. The default is True.

        """
        self.InsertAction(None, action, realize)

    def AddActions(self, actions, realize=True):
        """ Add multiple wx actions to the tool bar.

        If an action already exists in the tool bar, it will be moved
        to the end.

        Parameters
        ----------
        actions : iterable
            An iterable of wxAction instances to add to the tool bar.

        realize : bool, optional
            Whether the toolbar should realize the change immediately.
            If False, Realize() will need to be called manually once
            all desired changes have been made. The default is True.

        """
        insert = self.InsertAction
        for action in actions:
            insert(None, action, False)
        if realize:
            self.Realize()

    def InsertAction(self, before, action, realize=True):
        """ Insert a wx action into the tool bar.

        If the action already exists in the tool bar, it will be moved
        to the proper location.

        Parameters
        ----------
        before : wxAction or None
            The action in the tool bar which should come directly after
            the new action.

        action : wxAction
            The wxAction instance to insert into this tool bar.

        realize : bool, optional
            Whether the toolbar should realize the change immediately.
            If False, Realize() will need to be called manually once
            all desired changes have been made. The default is True.

        """
        all_items = self._all_items
        if action not in all_items:
            if before in all_items:
                index = all_items.index(before)
            else:
                index = len(all_items)
            all_items.insert(index, action)
            if action.IsVisible():
                max_index = len(self._actions_map)
                index = min(index, max_index)
                item = self._InsertAction(index, action)
                self._actions_map[action] = item
            action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)
            if realize:
                self.Realize()
        else:
            # XXX this is a potentially slow way to do things if the
            # number of actions being moved around is large. But, the
            # Wx apis don't appear to offer a better way, so this is
            # what we get (as usual...).
            self.RemoveAction(action)
            self.InsertAction(before, action, realize)

    def InsertActions(self, before, actions, realize=True):
        """ Insert multiple wx actions into the Menu.

        If an action already exists in this menu, it will be moved to
        the proper location.

        Parameters
        ----------
        before : wxAction, wxMenu, or None
            The item in the menu which should come directly after the
            new actions.

        actions : iterable
            An iterable of wxAction instances to add to the tool bar.

        realize : bool, optional
            Whether the toolbar should realize the change immediately.
            If False, Realize() will need to be called manually once
            all desired changes have been made. The default is True.

        """
        insert = self.InsertAction
        for action in actions:
            insert(before, action, False)
        if realize:
            self.Realize()

    def RemoveAction(self, action):
        """ Remove a wx action from the tool bar.

        If the action does not exist in the tool bar, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to remove from this tool bar.

        """
        all_items = self._all_items
        if action in all_items:
            all_items.remove(action)
            action.Unbind(EVT_ACTION_CHANGED, handler=self.OnActionChanged)
            item = self._actions_map.pop(action, None)
            if item is not None:
                self.DeleteTool(item.GetId())

    def RemoveActions(self, actions):
        """ Remove multiple actions from the tool bar.

        If an action does not exist in the tool bar, it will be ignored.

        Parameters
        ----------
        actions : iterable
            An iterable of wxActions to remove from the tool bar.

        """
        remove = self.RemoveAction
        for action in actions:
            remove(action)


class WxToolBar(WxConstraintsWidget, ProxyToolBar):
    """ A Wx implementation of an Enaml ToolBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxToolBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QCustomToolBar widget.

        """
        # The orientation of a tool bar can only be set at creation time.
        # Wx does not support changing it dynamically. It is only set if
        # the tool bar is a child of something other than a wx.Frame.
        # The style must include TB_FLAT or separators won't be drawn.
        d = self.declaration
        parent = self.parent_widget()
        style =  wx.TB_FLAT | wx.TB_TEXT | wx.NO_BORDER
        if not isinstance(parent, wx.Frame):
            style |= _ORIENTATION_MAP[d.orientation]
        else:
            style |= wx.HORIZONTAL

        self.widget = wxToolBar(parent, style=style)

        # Setting the tool bar to double buffered avoids a ton of
        # flickering on Windows during resize events.
        self.widget.SetDoubleBuffered(True)

        # For now, we set the bitmap size to 0 since we don't yet
        # support icons or images.
        self.widget.SetToolBitmapSize(wx.Size(0, 0))

    def init_layout(self):
        """ Initialize the layout for the toolbar.

        """
        super(WxToolBar, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, WxAction):
                widget.AddAction(child.widget, False)
            elif isinstance(child, WxActionGroup):
                widget.AddActions(child.actions(), False)
        widget.Realize()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Locate the wxAction object which logically follows the child.

        Parameters
        ----------
        child : WxToolkitObject
            The child object of interest.

        Returns
        -------
        result : wxAction or None
            The wxAction which logically follows the position of the
            child in the list of children. None will be returned if
            a relevant wxAction is not found.

        """
        found = False
        for dchild in self.children():
            if found:
                if isinstance(dchild, WxAction):
                    return dchild.widget
                if isinstance(dchild, WxActionGroup):
                    acts = dchild.actions()
                    if len(acts) > 0:
                        return acts[0]
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a WxToolBar.

        """
        super(WxToolBar, self).child_added(child)
        if isinstance(child, WxAction):
            before = self.find_next_action(child)
            self.widget.InsertAction(before, child.widget)
        elif isinstance(child, WxActionGroup):
            before = self.find_next_action(child)
            self.widget.InsertActions(before, child.actions())

    def child_removed(self, child):
        """  Handle the child removed event for a WxToolBar.

        """
        super(WxToolBar, self).child_removed(child)
        if isinstance(child, WxAction):
            if child.widget is not None:
                self.widget.RemoveAction(child.widget)
        elif isinstance(child, WxActionGroup):
            self.widget.RemoveActions(child.actions())

    #--------------------------------------------------------------------------
    # ProxyToolBar API
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Overridden parent class visibility setter which properly
        handles the visibility of the tool bar.

        """
        # XXX implement me!
        pass

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        # Wx does not support dynamically changing the orientation.
        pass

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass
