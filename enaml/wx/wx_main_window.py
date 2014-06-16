#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.main_window import ProxyMainWindow

from .wx_action import wxAction
from .wx_container import WxContainer
from .wx_dock_pane import WxDockPane
from .wx_menu_bar import WxMenuBar
from .wx_tool_bar import WxToolBar
from .wx_upstream import aui
from .wx_window import WxWindow


class wxToolBarContainer(wx.Panel):
    """ A simple wx.Panel that arranges the tool bars for a main window.

    """
    # The Wx AuiToolBar is terrible and the aui code which lays out
    # the tool bars is equally as bad. Unless we want to rewrite the
    # entire aui libary to do docking properly, we have to accept that
    # docking toolbars on wx are a no-go. That said, if the user defined
    # multiple tool bars for their main window, it would be bad to only
    # show one of them, which is what we would get if we had the wx.Frame
    # manage the tool bars directly (since it only supports a single tool
    # bar). Instead, we put all of the tool bars in a vertical sizer and
    # stick the entire thing at the top of the main window layout and
    # forbid it from being moved around. If better docking support is
    # desired, the user would be better off with Qt.
    def __init__(self, *args, **kwargs):
        """ Initialize a wxToolBarContainer.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.Panel.

        """
        super(wxToolBarContainer, self).__init__(*args, **kwargs)
        self._tool_bars = []
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.SetDoubleBuffered(True)

    def AddToolBar(self, tool_bar):
        """ Add a tool bar to the container.

        If the tool bar already exists in this container, this will be
        a no-op. The tool bar will be reparented to this container.

        Parameters
        ----------
        tool_bar : wxToolBar
            The wxToolBar instance to add to this container.

        """
        tool_bars = self._tool_bars
        if tool_bar not in tool_bars:
            tool_bars.append(tool_bar)
            tool_bar.Reparent(self)
            self.GetSizer().Add(tool_bar, 0, wx.EXPAND)

    def RemoveToolBar(self, tool_bar):
        """ Remove a tool bar from the container.

        If the tool bar already exists in this container, this will be
        a no-op.

        Parameters
        ----------
        tool_bar : wxToolBar
            The wxToolBar instance to remove from the container.

        """
        tool_bars = self._tool_bars
        if tool_bar in tool_bars:
            tool_bars.remove(tool_bar)
            self.GetSizer().Detach(tool_bar)


class wxMainWindow(wx.Frame):
    """ A wx.Frame subclass which adds MainWindow functionality.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMainWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments necessary to initialize
            a wx.Frame.

        """
        super(wxMainWindow, self).__init__(*args, **kwargs)
        flags = (
            aui.AUI_MGR_DEFAULT | aui.AUI_MGR_LIVE_RESIZE |
            aui.AUI_MGR_USE_NATIVE_MINIFRAMES
        )
        self._manager = aui.AuiManager(self, agwFlags=flags)
        self._central_widget = None
        self._tool_bars = None
        self._batch = False
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
        self.Bind(aui.EVT_AUI_PANE_FLOATED, self.OnPaneFloated)
        self.Bind(aui.EVT_AUI_PANE_DOCKED, self.OnPaneDocked)

        # Add a hidden dummy widget to the pane manager. This is a
        # workaround for a Wx bug where the laying out of the central
        # pane will have jitter on window resize (the computed layout
        # origin of the central pane oscillates between (0, 0) and
        # (1, 1)) if there are no other panes in the layout. If we
        # add a hidden pane with zero size, it prevents the jitter.
        self._hidden_widget = wx.Window(self)
        pane = aui.AuiPaneInfo()
        pane.BestSize(wx.Size(0, 0))
        pane.MinSize(wx.Size(0, 0))
        pane.Show(False)
        self._manager.AddPane(self._hidden_widget, pane)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnPaneClose(self, event):
        """ Handle the EVT_AUI_PANE_CLOSE event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnClose(event)

    def OnPaneFloated(self, event):
        """ Handle the EVT_AUI_PANE_FLOATED event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnFloated(event)

    def OnPaneDocked(self, event):
        """ Handle the EVT_AUI_PANE_DOCKED event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnDocked(event)

    def OnMenu(self, event):
        """ The event handler for the EVT_MENU event.

        This event handler will be called when an action is triggered
        in a Menu or a ToolBar.

        """
        action = wxAction.FindById(event.GetId())
        if action is not None:
            if action.IsCheckable():
                action.SetChecked(event.Checked())
            action.Trigger()

    def OnClose(self, event):
        """ The event handler for the EVT_CLOSE event.

        This event handler prevents the frame from being destroyed on
        close. Instead it just sets the visibility to False.

        """
        self.Hide()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def BeginBatch(self):
        """ Enter batch update mode for main window updates.

        Main window updates that are performed after calling this method
        will not be committed until EndBatch is called. This can be used
        to reduce flicker when making updates to the MainWindow.

        """
        self._batch = True

    def EndBatch(self):
        """ Exit batch update mode and process any pending updates.

        After calling this method, any pending main window updates will
        be processed.

        """
        self._batch = False
        self._manager.Update()

    def GetCentralWidget(self):
        """ Get the central widget for the main window.

        Returns
        -------
        result : wxWindow or None
            The central widget for the window, or None if no central
            widget is defined.

        """
        return self._central_widget

    def SetCentralWidget(self, widget):
        """ Set the central widget for the main window.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow instance to use as the central widget in the
            main window.

        """
        manager = self._manager
        old_widget = self._central_widget
        if old_widget:
            old_widget.Hide()
            pane = manager.GetPane(old_widget)
            if pane.IsOk():
                pane.Show(False)
                manager.DetachPane(old_widget)
        self._central_widget = widget
        pane = aui.AuiPaneInfo().CenterPane()
        manager.AddPane(widget, pane)
        if not self._batch:
            manager.Update()

    def SetMenuBar(self, menu_bar):
        """ Set the menu bar for the main window.

        Parameters
        ----------
        menu_bar : wxMenuBar
            The wxMenuBar instance to add to the main window.

        """
        old_bar = self.GetMenuBar()
        if old_bar is not menu_bar:
            super(wxMainWindow, self).SetMenuBar(menu_bar)
            # The menu bar must be refreshed after attachment
            if menu_bar:
                menu_bar.Update()

    def AddToolBar(self, tool_bar):
        """ Add a tool bar to the main window.

        If the tool bar already exists in the main window, calling this
        method is effectively a no-op.

        Parameters
        ----------
        tool_bar : wxToolBar
            The wxToolBar instance to add to the main window.

        """
        bars = self._tool_bars
        manager = self._manager
        if bars is None:
            bars = self._tool_bars = wxToolBarContainer(self)
            pane = aui.AuiPaneInfo().ToolbarPane().Top().Gripper(False)
            manager.AddPane(bars, pane)
        pane = manager.GetPane(bars)
        bars.AddToolBar(tool_bar)
        pane.MinSize(bars.GetBestSize())
        if not self._batch:
            manager.Update()

    def RemoveToolBar(self, tool_bar):
        """ Remove a tool bar from the main window.

        If the tool bar already exists in the main window, calling this
        method is effectively a no-op.

        Parameters
        ----------
        tool_bar : wxToolBar
            The wxToolBar instance to remove from the main window.

        """
        bars = self._tool_bars
        if bars is not None:
            bars.RemoveToolBar(tool_bar)
            tool_bar.Hide()
            manager = self._manager
            pane = manager.GetPane(bars)
            pane.MinSize(bars.GetBestSize())
            if not self._batch:
                manager.Update()
                manager.Update() # 2 calls required, because Wx...

    def AddDockPane(self, dock_pane):
        """ Add a dock pane to the main window.

        If the pane already exists in the main window, calling this
        method is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to add to the main window.

        """
        manager = self._manager
        pane = manager.GetPane(dock_pane)
        if not pane.IsOk():
            manager.AddPane(dock_pane, dock_pane.MakePaneInfo())
            if not self._batch:
                manager.Update()

    def RemoveDockPane(self, dock_pane):
        """ Remove a dock pane from the main window.

        If the pane does not exist in the window, calling this method
        is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to remove from the window.

        """
        manager = self._manager
        pane = manager.GetPane(dock_pane)
        if pane.IsOk():
            pane.Show(False)
            manager.DetachPane(dock_pane)
            if not self._batch:
                manager.Update()


class WxMainWindow(WxWindow, ProxyMainWindow):
    """ A Wx implementation of an Enaml ProxyMainWindow.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxMainWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget wxMainWindow widget.

        """
        style = self.creation_style()
        self.widget = wxMainWindow(self.parent_widget(), style=style)

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate
        # for MainWindow.
        widget = self.widget
        widget.BeginBatch()
        widget.SetMenuBar(self.menu_bar())
        widget.SetCentralWidget(self.central_widget())
        for d in self.dock_panes():
            widget.AddDockPane(d)
        for d in self.tool_bars():
            widget.AddToolBar(d)
        widget.EndBatch()

    def destroy(self):
        """ A reimplemented destructor.

        This will free any reference to the menu bar before destroying
        the underlying window. Wx segfaults otherwise.

        """
        self.widget.SetMenuBar(None)
        super(WxMainWindow, self).destroy()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def menu_bar(self):
        """ Get the QMenuBar widget defined for the main window.

        """
        d = self.declaration.menu_bar()
        if d is not None:
            return d.proxy.widget or None

    def dock_panes(self):
        """ Get the QDockWidget widgets defined for the main window.

        """
        for d in self.declaration.dock_panes():
            w = d.proxy.widget
            if w:
                yield w

    def tool_bars(self):
        """ Get the QToolBar widgets defined for the main window.

        """
        for d in self.declaration.tool_bars():
            w = d.proxy.widget
            if w:
                yield w

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxMainWindow.

        """
        if isinstance(child, WxMenuBar):
            self.widget.SetMenuBar(self.menu_bar())
        elif isinstance(child, WxContainer):
            self.widget.SetCentralWidget(self.central_widget())
        elif isinstance(child, WxDockPane):
            self.widget.AddDockPane(child.widget)
        elif isinstance(child, WxToolBar):
            self.widget.AddToolBar(child.widget)
        else:
            super(WxMainWindow, self).child_added(child)

    def child_removed(self, child):
        """ Handle the child removed event for a WxMainWindow.

        """
        if isinstance(child, WxDockPane):
            self.widget.RemoveDockPane(child.widget)
        elif isinstance(child, WxToolBar):
            self.widget.RemoveToolBar(child.widget)
        elif isinstance(child, WxContainer):
            self.widget.SetCentralWidget(self.central_widget())
        elif isinstance(child, WxMenuBar):
            self.widget.SetMenuBar(self.menu_bar())
        else:
            super(WxMainWindow, self).child_removed(child)
