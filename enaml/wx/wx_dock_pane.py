#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_container import WxContainer
from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_upstream import aui
from .wx_widget import WxWidget


#: A mapping from Enaml dock areas to wx aui dock area enums
_DOCK_AREA_MAP = {
    'top': aui.AUI_DOCK_TOP,
    'right': aui.AUI_DOCK_RIGHT,
    'bottom': aui.AUI_DOCK_BOTTOM,
    'left': aui.AUI_DOCK_LEFT,
}

#: A mapping from wx aui dock area enums to Enaml dock areas.
_DOCK_AREA_INV_MAP = {
    aui.AUI_DOCK_TOP: 'top',
    aui.AUI_DOCK_RIGHT: 'right',
    aui.AUI_DOCK_BOTTOM: 'bottom',
    aui.AUI_DOCK_LEFT: 'left',
}

#: A mapping from Enaml allowed dock areas to wx direction enums.
_ALLOWED_AREAS_MAP = {
    'top': wx.TOP,
    'right': wx.RIGHT,
    'bottom': wx.BOTTOM,
    'left': wx.LEFT,
    'all': wx.ALL,
}

#: A mappint from Enaml orientations to wx orientations.
_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


#: An event emitted when the dock pane is floated.
wxDockPaneFloatedEvent, EVT_DOCK_PANE_FLOATED = wx.lib.newevent.NewEvent()

#: An event emitted when the dock is docked.
wxDockPaneDockedEvent, EVT_DOCK_PANE_DOCKED = wx.lib.newevent.NewEvent()

#: An event emitted when the dock pane is closed.
wxDockPaneClosedEvent, EVT_DOCK_PANE_CLOSED = wx.lib.newevent.NewEvent()


class wxDockPane(wx.Panel):
    """ A wxPanel subclass which adds DockPane features.

    """
    def __init__(self, parent, *args, **kwargs):
        """ Initialize a wxDockPane.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxPanel.

        """
        super(wxDockPane, self).__init__(parent, *args, **kwargs)
        self._is_open = True
        self._title = u''
        self._title_bar_visible = True
        self._title_bar_orientation = wx.HORIZONTAL
        self._closable = True
        self._movable = True
        self._floatable = True
        self._floating = False
        self._dock_area = aui.AUI_DOCK_LEFT
        self._allowed_dock_areas = wx.ALL
        self._dock_widget = None
        self.SetSizer(wxSingleWidgetSizer())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _FindPaneManager(self):
        """ Find the pane manager for this dock pane.

        Returns
        -------
        result : AuiManager or None
            The AuiManager for this dock pane, or None if not found.

        """
        event = aui.AuiManagerEvent(aui.wxEVT_AUI_FIND_MANAGER)
        self.ProcessEvent(event)
        return event.GetManager()

    def _PaneInfoOperation(self, closure):
        """ A private method which will run the given closure if there
        is a valid pane info object for this dock pane.

        """
        manager = self._FindPaneManager()
        if manager is not None:
            pane = manager.GetPane(self)
            if pane.IsOk():
                closure(pane)
                manager.Update()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnClose(self, event):
        """ Handles the parent EVT_AUI_PANE_CLOSE event.

        This event handler is called directly by the parent wxMainWindow
        from its pane close event handler. This handler simply emits the
        EVT_DOCK_PANE_CLOSED event.

        """
        self._is_open = False
        wx.PostEvent(self, wxDockPaneClosedEvent())

    def OnFloated(self, event):
        """ Handles the parent EVT_AUI_PANE_FLOATED event.

        This event handler is called directly by the parent wxMainWindow
        from its pane floated event handler. This handler simply emits
        the EVT_DOCK_PANE_FLOATED event.

        """
        self._floating = True
        wx.PostEvent(self, wxDockPaneFloatedEvent())

    def OnDocked(self, event):
        """ Handles the parent EVT_AUI_PANE_DOCKED event.

        This event handler is called directly by the parent wxMainWindow
        from its pane docked event handler. This handler simply emits
        the EVT_DOCK_PANE_DOCKED event.

        """
        self._floating = False
        self._dock_area = event.GetPane().dock_direction
        wx.PostEvent(self, wxDockPaneDockedEvent())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def MakePaneInfo(self):
        """ Create a new AuiPaneInfo object for this dock pane.

        This is called by the wxMainWindow when it adds this dock pane
        to its internal layout for the first time.

        Returns
        -------
        result : AuiPaneInfo
            An initialized AuiPaneInfo object for this pane.

        """
        info = aui.AuiPaneInfo()

        # Don't allow docking panes as a notebook since that causes
        # issues with finding the proper parent manager on updates
        # and it makes resizing of dock panes abysmally slow.
        info.NotebookDockable(False)

        info.BestSize(self.GetBestSize())
        info.MinSize(self.GetEffectiveMinSize())
        info.Show(self.IsOpen())
        info.Caption(self.GetTitle())
        info.CloseButton(self.GetClosable())
        info.Movable(self.GetMovable())
        info.Floatable(self.GetFloatable())
        info.Direction(self.GetDockArea())

        left = self.GetTitleBarOrientation() == wx.VERTICAL
        info.CaptionVisible(self.GetTitleBarVisible(), left)

        areas = self.GetAllowedDockAreas()
        info.TopDockable(bool(areas & wx.TOP))
        info.RightDockable(bool(areas & wx.RIGHT))
        info.LeftDockable(bool(areas & wx.LEFT))
        info.BottomDockable(bool(areas & wx.BOTTOM))

        if self.GetFloating():
            info.Float()
        else:
            info.Dock()

        return info

    def GetDockWidget(self):
        """ Get the dock widget being managed by this pane.

        Returns
        -------
        result : wxWindow or None
            The wx widget being managed by this dock pane, or None
            if no widget is being managed.

        """
        return self._dock_widget

    def SetDockWidget(self, widget):
        """ Set the dock widget to be managed by the pane.

        Any old dock widget will be removed, but not destroyed.

        Parameters
        ----------
        widget : wxWindow
            The wx widget to use as the dock widget for this pane.

        """
        old_widget = self._dock_widget
        if old_widget:
            old_widget.Hide()
        self._dock_widget = widget
        self.GetSizer().Add(widget)
        self.UpdateSizing()

    def UpdateSizing(self):
        """ Trigger a sizing update of the pane manager.

        """
        def closure(pane):
            pane.MinSize(self.GetBestSize())
        self._PaneInfoOperation(closure)

    def IsOpen(self):
        """ Get whether or not the dock pane is open.

        Returns
        -------
        result : bool
            True if the pane is open, False otherwise.

        """
        return self._is_open

    def Open(self):
        """ Open the dock pane in the main window.

        If the pane is already open, this method is a no-op.

        """
        self._is_open = True
        def closure(pane):
            if not pane.IsShown():
                pane.Show(True)
        self._PaneInfoOperation(closure)

    def Close(self):
        """ Close the dock pane in the main window.

        If the pane is already closed, this method is no-op.

        """
        self._is_open = False
        def closure(pane):
            if pane.IsShown():
                pane.Show(False)
        self._PaneInfoOperation(closure)

    def GetTitle(self):
        """ Get the title for the dock pane.

        Returns
        -------
        result : unicode
            The title of the dock pane.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for the dock pane.

        Parameters
        ----------
        title : unicode
            The title to use for the dock pane.

        """
        if self._title != title:
            self._title = title
            def closure(pane):
                pane.Caption(title)
            self._PaneInfoOperation(closure)

    def GetTitleBarVisible(self):
        """ Get the title bar visibility state for the dock pane.

        Returns
        -------
        result : bool
            Whether or not the title bar is visible.

        """
        return self._title_bar_visible

    def SetTitleBarVisible(self, visible):
        """ Set the title bar visibility state for the dock pane.

        Parameters
        ----------
        visible : bool
            Whether or not the title bar should be visible.

        """
        if self._title_bar_visible != visible:
            self._title_bar_visible = visible
            def closure(pane):
                left = self._title_bar_orientation == wx.VERTICAL
                pane.CaptionVisible(visible, left)
            self._PaneInfoOperation(closure)

    def GetTitleBarOrientation(self):
        """ Get the title bar orientation for the dock pane.

        Returns
        -------
        result : int
            The orientation of the title bar. Either wx.HORIZONTAL
            or wx.VERTICAL

        """
        return self._title_bar_orientation

    def SetTitleBarOrientation(self, orientation):
        """ Set the title bar orientation for the dock pane.

        Parameters
        ----------
        result : int
            The orientation of the title bar. Either wx.HORIZONTAL
            or wx.VERTICAL

        """
        if self._title_bar_orientation != orientation:
            self._title_bar_orientation = orientation
            def closure(pane):
                visible = self._title_bar_visible
                left = orientation == wx.VERTICAL
                pane.CaptionVisible(visible, left)
            self._PaneInfoOperation(closure)

    def GetClosable(self):
        """ Get the closable state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is closable.

        """
        return self._closable

    def SetClosable(self, closable):
        """ Set the closable state of the pane.

        Parameters
        ----------
        closable : bool
            Whether or not the pane is closable.

        """
        if self._closable != closable:
            self._closable = closable
            def closure(pane):
                pane.CloseButton(closable)
            self._PaneInfoOperation(closure)

    def GetMovable(self):
        """ Get the movable state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is movable.

        """
        return self._movable

    def SetMovable(self, movable):
        """ Set the movable state of the pane.

        Parameters
        ----------
        movable : bool
            Whether or not the pane is movable.

        """
        if self._movable != movable:
            self._movable = movable
            def closure(pane):
                pane.Movable(movable)
            self._PaneInfoOperation(closure)

    def GetFloatable(self):
        """ Get the floatable state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is floatable.

        """
        return self._floatable

    def SetFloatable(self, floatable):
        """ Set the floatable state of the pane.

        Parameters
        ----------
        floatable : bool
            Whether or not the pane is floatable.

        """
        if self._floatable != floatable:
            self._floatable = floatable
            def closure(pane):
                pane.Floatable(floatable)
            self._PaneInfoOperation(closure)

    def GetFloating(self):
        """ Get the floating state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is floating.

        """
        return self._floating

    def SetFloating(self, floating):
        """ Set the floating state of the pane.

        Parameters
        ----------
        floating : bool
            Whether or not the pane should be floating.

        """
        if self._floating != floating:
            self._floating = floating
            def closure(pane):
                if floating:
                    pane.Float()
                else:
                    pane.Dock()
            self._PaneInfoOperation(closure)

    def GetDockArea(self):
        """ Get the current dock area of the pane.

        Returns
        -------
        result : int
            The current dock area of the pane. One of the wx enums
            LEFT, RIGHT, TOP, or BOTTOM.

        """
        return self._dock_area

    def SetDockArea(self, dock_area):
        """ Set the dock area for the pane.

        Parameters
        ----------
        dock_area : int
            The dock area for the pane. One of the wx enums LEFT,
            RIGHT, TOP, or BOTTOM.

        """
        if self._dock_area != dock_area:
            self._dock_area = dock_area
            def closure(pane):
                pane.Direction(dock_area)
            self._PaneInfoOperation(closure)

    def GetAllowedDockAreas(self):
        """ Get the allowed dock areas for the pane.

        Returns
        -------
        result : int
            The allowed dock areas for the pane. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        return self._allowed_dock_areas

    def SetAllowedDockAreas(self, dock_areas):
        """ Set the allowed dock areas for the pane.

        Parameters
        ----------
        dock_areas : int
            The allowed dock areas for the pane. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        if self._allowed_dock_areas != dock_areas:
            self._allowed_dock_areas = dock_areas
            def closure(pane):
                pane.TopDockable(bool(dock_areas & wx.TOP))
                pane.RightDockable(bool(dock_areas & wx.RIGHT))
                pane.LeftDockable(bool(dock_areas & wx.LEFT))
                pane.BottomDockable(bool(dock_areas & wx.BOTTOM))
            self._PaneInfoOperation(closure)


class WxDockPane(WxWidget):
    """ A Wx implementation of an Enaml DockPane.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxDockPane widget.

        """
        return wxDockPane(parent)

    def create(self, tree):
        """ Create and initialize the dock pane control.

        """
        super(WxDockPane, self).create(tree)
        self.set_title(tree['title'])
        self.set_title_bar_visible(tree['title_bar_visible'])
        self.set_title_bar_orientation(tree['title_bar_orientation'])
        self.set_closable(tree['closable'])
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])
        widget = self.widget()
        widget.Bind(EVT_DOCK_PANE_FLOATED, self.on_dock_pane_floated)
        widget.Bind(EVT_DOCK_PANE_DOCKED, self.on_dock_pane_docked)
        widget.Bind(EVT_DOCK_PANE_CLOSED, self.on_dock_pane_closed)

    def init_layout(self):
        """ Handle the layout initialization for the dock pane.

        """
        super(WxDockPane, self).init_layout()
        self.widget().SetDockWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_widget(self):
        """ Find and return the dock widget child for this widget.

        Returns
        -------
        result : wxWindow or None
            The dock widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, WxContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a WxDockPane.

        """
        if isinstance(child, WxContainer):
            self.widget().SetDockWidget(self.dock_widget())

    def child_added(self, child):
        """ Handle the child added event for a WxDockPane.

        """
        if isinstance(child, WxContainer):
            self.widget().SetDockWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_dock_pane_closed(self, event):
        """ The event handler for the EVT_DOCK_PANE_CLOSED event.

        """
        self.send_action('closed', {})

    def on_dock_pane_floated(self, event):
        """ The event handler for the EVT_DOCK_PANE_FLOATED event.

        """
        self.send_action('floated', {})

    def on_dock_pane_docked(self, event):
        """ The event handler for the EVT_DOCK_PANE_AREA event.

        """
        area = self.widget().GetDockArea()
        content = {'dock_area': _DOCK_AREA_INV_MAP[area]}
        self.send_action('docked', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_title_bar_visible(self, content):
        """ Handle the 'set_title_bar_visible' action from the Enaml
        widget.

        """
        self.set_title_bar_visible(content['title_bar_visible'])

    def on_action_set_title_bar_orientation(self, content):
        """ Handle the 'set_title_bar_orientation' action from the
        Enaml widget.

        """
        self.set_title_bar_orientation(content['title_bar_orientation'])

    def on_action_set_closable(self, content):
        """ Handle the 'set_closable' action from the Enaml widget.

        """
        self.set_closable(content['closable'])

    def on_action_set_movable(self, content):
        """ Handle the 'set_movable' action from the Enaml widget.

        """
        self.set_movable(content['movable'])

    def on_action_set_floatable(self, content):
        """ Handle the 'set_floatable' action from the Enaml widget.

        """
        self.set_floatable(content['floatable'])

    def on_action_set_floating(self, content):
        """ Handle the 'set_floating' action from the Enaml widget.

        """
        self.set_floating(content['floating'])

    def on_action_set_dock_area(self, content):
        """ Handle the 'set_dock_area' action from the Enaml widget.

        """
        self.set_dock_area(content['dock_area'])

    def on_action_set_allowed_dock_areas(self, content):
        """ Handle the 'set_allowed_dock_areas' action from the Enaml
        widget.

        """
        self.set_allowed_dock_areas(content['allowed_dock_areas'])

    def on_action_open(self, content):
        """ Handle the 'open' action from the Enaml widget.

        """
        self.widget().Open()

    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.widget().Close()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter which to opens|closes the
        dock pane.

        """
        widget = self.widget()
        if visible:
            widget.Open()
        else:
            widget.Close()

    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        self.widget().SetTitle(title)

    def set_title_bar_visible(self, visible):
        """ Set the title bar visibility of the underlying widget.

        """
        self.widget().SetTitleBarVisible(visible)

    def set_title_bar_orientation(self, orientation):
        """ Set the title bar orientation of the underyling widget.

        """
        self.widget().SetTitleBarOrientation(_ORIENTATION_MAP[orientation])

    def set_closable(self, closable):
        """ Set the closable state on the underlying widget.

        """
        self.widget().SetClosable(closable)

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        self.widget().SetMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget().SetFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        self.widget().SetFloating(floating)

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        self.widget().SetDockArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        wx_areas = 0
        for area in dock_areas:
            wx_areas |= _ALLOWED_AREAS_MAP[area]
        self.widget().SetAllowedDockAreas(wx_areas)

