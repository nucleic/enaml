#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from atom.api import Typed

from enaml.widgets.menu import ProxyMenu

from .wx_action import WxAction, EVT_ACTION_CHANGED
from .wx_action_group import WxActionGroup
from .wx_toolkit_object import WxToolkitObject


#: An event emitted when the menu state changes.
wxMenuChangedEvent, EVT_MENU_CHANGED = wx.lib.newevent.NewEvent()


class wxMenu(wx.Menu):
    """ A wx.Menu subclass which provides a more convenient api for
    working with wxMenu and wxAction children.

    """
    def __init__(self, parent, *args, **kwargs):
        """ Initialize a wxMenu.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wx.Menu.

        """
        super(wxMenu, self).__init__(*args, **kwargs)
        self._parent = parent
        self._title = u''
        self._all_items = []
        self._menus_map = {}
        self._actions_map = {}
        self._enabled = True
        self._bar_enabled = True
        self._visible = True
        self._batch = False
        self._is_context_menu = False
        self._id = wx.NewId()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _EmitChanged(self):
        """ Emits the menu changed event if not in batch mode.

        """
        if not self._batch:
            event = wxMenuChangedEvent()
            event.SetEventObject(self)
            wx.PostEvent(self, event)

    def _SetBarEnabled(self, enabled):
        """ A private method called by an owner menu bar.

        Parameters
        ----------
        enabled : bool
            Whether or not the owner menu bar is enabled.

        """
        if self._bar_enabled != enabled:
            old = self.IsEnabled()
            self._bar_enabled = enabled
            new = self.IsEnabled()
            if old != new:
                self._EmitChanged()

    def _InsertMenuItem(self, index, menu):
        """ Insert a new item into the menu for the given menu.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to use as the submenu.

        Returns
        -------
        result : wx.MenuItem
            The menu item to use for the given menu.

        """
        text = menu.GetTitle()
        menu_id = menu.GetId()
        text = text or 'menu_%d' % menu_id # null text == exception
        res = wx.MenuItem(self, menu_id, text, '', subMenu=menu)
        res.Enable(menu.IsEnabled())
        self.InsertItem(index, res)
        return res

    def _InsertActionItem(self, index, action):
        """ Insert a new item into the menu for the given action.

        Parameters
        ----------
        action : wxAction
            The wx action for which to create a wx.MenuItem.

        Returns
        -------
        result : wx.MenuItem
            The menu item for the given action.

        """
        text = action.GetText()
        help = action.GetStatusTip()
        if action.IsSeparator():
            res = wx.MenuItem(self, wx.ID_SEPARATOR, text, help)
            self.InsertItem(index, res)
        else:
            action_id = action.GetId()
            text = text or 'action_%d' % action_id # null text == exception
            if action.IsCheckable():
                # The wx.ITEM_RADIO kind doesn't behave nicely, so we
                # just use the check kind and rely on the action group
                # to handle the exclusive radio behavior. Changing the
                # bitmap to something that looks like a radio button
                # breaks the Windows theme.
                kind = wx.ITEM_CHECK
                res = wx.MenuItem(self, action_id, text, help, kind)
                # Must instert the item before checking it, or c++
                # assertion errors are thrown
                self.InsertItem(index, res)
                res.Check(action.IsChecked())
            else:
                kind = wx.ITEM_NORMAL
                res = wx.MenuItem(self, action_id, text, help, kind)
                self.InsertItem(index, res)
            res.Enable(action.IsEnabled())
        return res

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will be called when a child action changes. It
        ensures that the new state of the child action is in sync with
        the associated menu item.

        """
        event.Skip()
        action = event.GetEventObject()
        item = self._actions_map.get(action)

        # Fist, check for a visibility change. This requires adding or
        # removing the menu item from the menu and the actions map.
        visible = action.IsVisible()
        if visible != bool(item):
            if visible:
                index = self._all_items.index(action)
                n_visible = len(self._actions_map) + len(self._menus_map)
                index = min(index, n_visible)
                new_item = self._InsertActionItem(index, action)
                self._actions_map[action] = new_item
            else:
                self.DestroyItem(item)
                del self._actions_map[action]
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # If the item is a separator, and the separator state has
        # changed, we need to build an entirely new menu item, and
        # replace the existing item with the new one.
        item_sep = item.IsSeparator()
        action_sep = action.IsSeparator()
        if item_sep or action_sep:
            if item_sep != action_sep:
                self.DestroyItem(item)
                index = self._all_items.index(action)
                n_visible = len(self._actions_map) + len(self._menus_map)
                index = min(index, n_visible)
                new_item = self._InsertActionItem(index, action)
                self._actions_map[action] = new_item
            return

        # For all other state, the menu item can be updated in-place.
        item.SetItemLabel(action.GetText())
        item.SetHelp(action.GetStatusTip())
        if action.IsCheckable():
            item.SetKind(wx.ITEM_CHECK)
            item.Check(action.IsChecked())
        else:
            if item.IsCheckable():
                item.Check(False)
            item.SetKind(wx.ITEM_NORMAL)
        item.Enable(action.IsEnabled())

    def OnMenuChanged(self, event):
        """ The event hanlder for the EVT_MENU_CHANGED event.

        This handler will be called when a child menu changes. It
        ensure that the new state of the child menu is in sync with
        the associated menu item.

        """
        event.Skip()
        menu = event.GetEventObject()
        item = self._menus_map.get(menu)

        # Fist, check for a visibility change. This requires adding or
        # removing the menu item from the menu and the menus map.
        visible = menu.IsVisible()
        if visible != bool(item):
            if visible:
                index = self._all_items.index(menu)
                n_visible = len(self._actions_map) + len(self._menus_map)
                index = min(index, n_visible)
                new_item = self._InsertMenuItem(index, menu)
                self._menus_map[menu] = new_item
            else:
                # Need to first remove the submenu or wx will destroy it.
                item.SetSubMenu(None)
                self.DestroyItem(item)
                del self._menus_map[menu]
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # For all other state, the menu item can be updated in-place.
        item.SetItemLabel(menu.GetTitle())
        item.Enable(menu.IsEnabled())

    def OnShowContextMenu(self, event):
        """ A private event handler for displaying the context menu.

        This handler is connected to the context menu event on the
        parent widget when this menu is marked as a context menu.

        """
        parent = self._parent
        if parent and isinstance(parent, wx.Window):
            parent.PopupMenu(self)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def BeginBatch(self):
        """ Enter batch update mode for the menu.

        """
        self._batch = True

    def EndBatch(self, emit=True):
        """ Exit batch update mode for the menu.

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
        """ Get the unique wx id for this menu.

        Returns
        -------
        result : int
            The wx id number for this menu.

        """
        return self._id

    def GetTitle(self):
        """ Get the title for the menu.

        Returns
        -------
        result : unicode
            The unicode title for the menu.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for the menu.

        Parameters
        ----------
        title : unicode
            The unicode string to use as the menu title.

        """
        if self._title != title:
            self._title = title
            self._EmitChanged()

    def IsEnabled(self):
        """ Get whether or not the menu is enabled.

        Returns
        -------
        result : bool
            Whether or not the menu is enabled.

        """
        if self._bar_enabled:
            return self._enabled
        return False

    def SetEnabled(self, enabled):
        """ Set whether or not the menu is enabled.

        Parameters
        ----------
        enabled : bool
            Whether or not the menu is enabled.

        """
        if self._enabled != enabled:
            self._enabled = enabled
            if self._bar_enabled:
                self._EmitChanged()

    def IsVisible(self):
        """ Get whether or not the menu is visible.

        Returns
        -------
        result : bool
            Whether or not the menu is visible.

        """
        return self._visible

    def SetVisible(self, visible):
        """ Set whether or not the menu is visible.

        Parameters
        ----------
        visible : bool
            Whether or not the menu is visible.

        """
        if self._visible != visible:
            self._visible = visible
            self._EmitChanged()

    def IsContextMenu(self):
        """ Whether this menu acts as a context menu for its parent.

        Returns
        -------
        result : bool
            True if this menu acts as a context menu, False otherwise.

        """
        return self._is_context_menu

    def SetContextMenu(self, context):
        """ Set whether this menu acts as a context menu for its parent.

        Parameters
        ----------
        context : bool
            True if this menu should act as a context menu, False
            otherwise.

        """
        old_context = self._is_context_menu
        self._is_context_menu = context
        if old_context != context:
            parent = self._parent
            if parent:
                handler = self.OnShowContextMenu
                if context:
                    parent.Bind(wx.EVT_CONTEXT_MENU, handler)
                else:
                    parent.Unbind(wx.EVT_CONTEXT_MENU, handler=handler)

    def AddMenu(self, menu):
        """ Add a wx menu to the Menu.

        If the menu already exists in this menu, it will be moved to
        the end.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to add to this menu.

        """
        self.InsertMenu(None, menu)

    def InsertMenu(self, before, menu):
        """ Insert a wx menu into the Menu.

        If the menu already exists in this menu, if will be moved to
        the proper location.

        Parameters
        ----------
        before : wxAction, wxMenu, or None
            The item in the menu which should come directly after the
            new sub-menu.

        menu : wxMenu
            The wxMenu instance to insert into this menu.

        """
        all_items = self._all_items
        if menu not in all_items:
            if before in all_items:
                index = all_items.index(before)
            else:
                index = len(all_items)
            all_items.insert(index, menu)
            if menu.IsVisible():
                max_index = len(self._actions_map) + len(self._menus_map)
                index = min(index, max_index)
                menu_item = self._InsertMenuItem(index, menu)
                self._menus_map[menu] = menu_item
            menu.Bind(EVT_MENU_CHANGED, self.OnMenuChanged)
        else:
            # XXX this is a potentially slow way to do things if the
            # number of menus being moved around is large. But, the
            # Wx apis don't appear to offer a better way, so this is
            # what we get (as usual...).
            self.RemoveMenu(menu)
            self.InsertMenu(before, menu)

    def RemoveMenu(self, menu):
        """ Remove a wx menu from the Menu.

        If the menu does not exist in the menu, this is a no-op.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to remove from this menu.

        """
        all_items = self._all_items
        if menu in all_items:
            all_items.remove(menu)
            menu.Unbind(EVT_MENU_CHANGED, handler=self.OnMenuChanged)
            menu_item = self._menus_map.pop(menu, None)
            if menu_item is not None:
                self.RemoveItem(menu_item)
                # Set the SubMenu to None or wx will destroy it.
                menu_item.SetSubMenu(None)

    def AddAction(self, action):
        """ Add a wx action to the Menu.

        If the action already exists in the menu, it will be moved to
        the end.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to add to this menu.

        """
        self.InsertAction(None, action)

    def AddActions(self, actions):
        """ Add multiple wx actions to the Menu.

        If an action already exists in the menu, it will be moved to
        the end.

        Parameters
        ----------
        actions : iterable
            An iterable of wxAction instances to add to the menu.

        """
        insert = self.InsertAction
        for action in actions:
            insert(None, action)

    def InsertAction(self, before, action):
        """ Insert a wx action into the Menu.

        If the action already exists in the menu, it will be moved to
        the proper location.

        Parameters
        ----------
        before : wxAction, wxMenu, or None
            The item in the menu which should come directly after the
            new action.

        action : wxAction
            The wxAction instance to insert into this menu.

        """
        all_items = self._all_items
        if action not in all_items:
            if before in all_items:
                index = all_items.index(before)
            else:
                index = len(all_items)
            all_items.insert(index, action)
            if action.IsVisible():
                max_index = len(self._actions_map) + len(self._menus_map)
                index = min(index, max_index)
                menu_item = self._InsertActionItem(index, action)
                self._actions_map[action] = menu_item
            action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)
        else:
            # XXX this is a potentially slow way to do things if the
            # number of actions being moved around is large. But, the
            # Wx apis don't appear to offer a better way, so this is
            # what we get (as usual...).
            self.RemoveAction(action)
            self.InsertAction(before, action)

    def InsertActions(self, before, actions):
        """ Insert multiple wx actions into the Menu.

        If an action already exists in this menu, it will be moved to
        the proper location.

        Parameters
        ----------
        before : wxAction, wxMenu, or None
            The item in the menu which should come directly after the
            new actions.

        actions : iterable
            An iterable of wxAction instances to add to the menu.

        """
        insert = self.InsertAction
        for action in actions:
            insert(before, action)

    def RemoveAction(self, action):
        """ Remove a wx action from the Menu.

        If the action does not exist in the menu, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to remove from this menu.

        """
        all_items = self._all_items
        if action in all_items:
            all_items.remove(action)
            action.Unbind(EVT_ACTION_CHANGED, handler=self.OnActionChanged)
            menu_item = self._actions_map.pop(action, None)
            if menu_item is not None:
                self.RemoveItem(menu_item)

    def RemoveActions(self, actions):
        """ Remove multiple actions from the Menu.

        If an action does not exist in the menu, it will be ignored.

        Parameters
        ----------
        actions : iterable
            An iterable of wxAction instances to remove from the menu.

        """
        remove = self.RemoveAction
        for action in actions:
            remove(action)


class WxMenu(WxToolkitObject, ProxyMenu):
    """ A Wx implementation of an Enaml ProxyMenu.

    """
        #: A reference to the widget created by the proxy.
    widget = Typed(wxMenu)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying menu widget.

        """
        self.widget = wxMenu(self.parent_widget())
        self.widget.BeginBatch()

    def init_widget(self):
        """ Initialize the widget.

        """
        super(WxMenu, self).init_widget()
        d = self.declaration
        self.set_title(d.title)
        self.set_enabled(d.enabled)
        self.set_visible(d.visible)
        self.set_context_menu(d.context_menu)
        self.widget.EndBatch(emit=False)

    def init_layout(self):
        """ Initialize the layout of the widget.

        """
        super(WxMenu, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, WxMenu):
                widget.AddMenu(child.widget)
            elif isinstance(child, WxAction):
                widget.AddAction(child.widget)
            elif isinstance(child, WxActionGroup):
                widget.AddActions(child.actions())

    def destroy(self):
        """ A reimplemented destructor.

        This destructor simply drops the reference to the menu and the
        enaml declaration. Destroying it will cause wx to segfault.

        """
        del self.widget
        del self.declaration

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the wxAction instance which follows the child.

        Parameters
        ----------
        child : WxToolkitObject
            The child of interest.

        Returns
        -------
        result : wxAction or None
            The wxAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        found = False
        for dchild in self.children():
            if found:
                if isinstance(dchild, (WxMenu, WxAction)):
                    return dchild.widget
                if isinstance(dchild, WxActionGroup):
                    acts = dchild.actions()
                    if len(acts) > 0:
                        return acts[0]
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a WxMenu.

        """
        super(WxMenu, self).child_added(child)
        if isinstance(child, WxMenu):
            before = self.find_next_action(child)
            self.widget.InsertMenu(before, child.widget)
        elif isinstance(child, WxAction):
            before = self.find_next_action(child)
            self.widget.InsertAction(before, child.widget)
        elif isinstance(child, WxActionGroup):
            before = self.find_next_action(child)
            self.widget.InsertActions(before, child.actions())

    def child_removed(self, child):
        """  Handle the child removed event for a WxMenu.

        """
        super(WxMenu, self).child_removed(child)
        if isinstance(child, WxMenu):
            self.widget.RemoveMenu(child.widget)
        elif isinstance(child, WxAction):
            self.widget.RemoveAction(child.widget)
        elif isinstance(child, WxActionGroup):
            self.widget.RemoveActions(child.actions())

    #--------------------------------------------------------------------------
    # ProxyMenu API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the underlyling control.

        """
        self.widget.SetTitle(title)

    def set_visible(self, visible):
        """ Set the visibility on the underlying widget.

        """
        self.widget.SetVisible(visible)

    def set_enabled(self, enabled):
        """ Set the enabled state of the widget.

        """
        self.widget.SetEnabled(enabled)

    def set_context_menu(self, context):
        """ Set whether or not the menu is a context menu.

        """
        self.widget.SetContextMenu(context)

    def popup(self):
        """ Popup the menu at the current mouse location.

        """
        # This is not supported on wx. Wx requires the menu to be
        # popped up over a specified window. It can't be done using
        # global coordinates.
        pass
