#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.menu_bar import ProxyMenuBar

from .wx_menu import WxMenu, EVT_MENU_CHANGED
from .wx_toolkit_object import WxToolkitObject


class wxMenuBar(wx.MenuBar):
    """ A wx.MenuBar subclass which exposes a more convenient api for
    working with wxMenu children.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMenuBar.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wx.MenuBar.

        """
        super(wxMenuBar, self).__init__(*args, **kwargs)
        self._menus = []
        self._visible_menus = []
        self._enabled = True

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def OnMenuChanged(self, event):
        """ The event handler for the EVT_MENU_CHANGED event.

        This event handler will synchronize the menu changes with
        the menu bar.

        """
        event.Skip()
        if self.IsAttached():
            menu = event.GetEventObject()

            # First, check for a visibility change. This requires adding
            # or removing the menu from the menu bar.
            visible = menu.IsVisible()
            was_visible = menu in self._visible_menus
            if visible != was_visible:
                if visible:
                    index = self._menus.index(menu)
                    index = min(index, len(self._visible_menus))
                    self._visible_menus.insert(index, menu)
                    self.Insert(index, menu, menu.GetTitle())
                    self.EnableTop(index, menu.IsEnabled())
                else:
                    index = self._visible_menus.index(menu)
                    self._visible_menus.pop(index)
                    self.Remove(index)
                return

            # If the menu isn't visible, there's nothing to do.
            if not visible:
                return

            # For all other state, the menu can be updated in-place.
            index = self._visible_menus.index(menu)
            self.SetMenuLabel(index, menu.GetTitle())
            self.EnableTop(index, menu.IsEnabled())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def IsEnabled(self):
        """ Get whether or not the menu bar is enabled.

        Returns
        -------
        result : bool
            Whether or not the menu bar is enabled.

        """
        return self._enabled

    def SetEnabled(self, enabled):
        """ Set whether or not the menu bar is enabled.

        Parameters
        ----------
        enabled : bool
            Whether or not the menu bar is enabled.

        """
        # Wx does not provide a means for disabling the entire menu
        # bar, so we must do it manually by disabling each menu.
        if self._enabled != enabled:
            self._enabled = enabled
            for menu in self._menus:
                menu._SetBarEnabled(enabled)

    def AddMenu(self, menu):
        """ Add a wxMenu to the menu bar.

        If the menu already exists in the menu bar, this is a no-op.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to add to the menu bar.

        """
        self.InsertMenu(None, menu)

    def InsertMenu(self, before, menu):
        """ Insert a wxMenu into the menu bar.

        If the menu already exists in the menu bar, this is a no-op.

        Parameters
        ----------
        before : wxMenu
            The menu before which to insert the given menu.

        menu : wxMenu
            The menu to insert into the menu bar.

        """
        menus = self._menus
        if menu not in menus:
            if before in menus:
                index = menus.index(before)
            else:
                index = len(menus)
            menus.insert(index, menu)
            if menu.IsVisible():
                max_index = len(self._visible_menus)
                index = min(index, max_index)
                self._visible_menus.insert(index, menu)
                self.Insert(index, menu, menu.GetTitle())
            menu.Bind(EVT_MENU_CHANGED, self.OnMenuChanged)
            menu._SetBarEnabled(self._enabled)

    def RemoveMenu(self, menu):
        """ Remove a wxMenu from the menu bar.

        If the menu does not exist in the menu bar, this is a no-op.

        Parameters
        ----------
        menu : wxMenu
            The menu to remove from the menu bar.

        """
        menus = self._menus
        if menu in menus:
            menus.remove(menu)
            menu.Unbind(EVT_MENU_CHANGED, handler=self.OnMenuChanged)
            visible_menus = self._visible_menus
            if menu in visible_menus:
                index = visible_menus.index(menu)
                visible_menus.remove(menu)
                self.Remove(index)

    def Update(self):
        """ A method which can be called to update the menu bar.

        Calling this method will manually refresh the state of the
        items in the menu bar. This is useful to call just after
        attaching the menu bar to a frame, since the menu bar state
        cannot be updated prior to being attached.

        """
        if self.IsAttached():
            for index, menu in enumerate(self._visible_menus):
                self.SetMenuLabel(index, menu.GetTitle())
                if not menu.IsEnabled():
                    self.EnableTop(index, False)


class WxMenuBar(WxToolkitObject, ProxyMenuBar):
    """ A Wx implementation of an Enaml ProxyMenuBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxMenuBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying menu bar widget.

        """
        # Wx behaves better when creating the menu bar without a parent.
        self.widget = wxMenuBar()

    def init_layout(self):
        """ Initialize the layout for the menu bar.

        """
        super(WxMenuBar, self).init_layout()
        widget = self.widget
        for child in self.children():
            if isinstance(child, WxMenu):
                widget.AddMenu(child.widget)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor simply drops the reference to the menu bar and
        the enaml declaration and clears the menus in the menu bar.
        Destroying it will cause wx to segfault.

        """
        if self.widget:
            self.widget.SetMenus([])
        del self.widget
        del self.declaration

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def find_next_menu(self, child):
        """ Get the wxMenu instance which follows the child.

        Parameters
        ----------
        child : WxMenu
            The child menu of interest.

        Returns
        -------
        result : wxMenu or None
            The wxMenu which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        found = False
        for dchild in self.children():
            if found:
                if isinstance(dchild, WxMenu):
                    return dchild.widget
            else:
                found = dchild is child

    def child_added(self, child):
        """ Handle the child added event for a WxMenuBar.

        """
        super(WxMenuBar, self).child_added(child)
        if isinstance(child, WxMenu):
            before = self.find_next_menu(child)
            self.widget.InsertMenu(before, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a WxMenuBar.

        """
        super(WxMenuBar, self).child_removed(child)
        if isinstance(child, WxMenu):
            self.widget.RemoveMenu(child.widget)
