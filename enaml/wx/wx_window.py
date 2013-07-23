#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.layout.geometry import Pos, Rect, Size
from enaml.widgets.window import ProxyWindow

from .wx_action import wxAction
from .wx_container import WxContainer
from .wx_layout_request import EVT_COMMAND_LAYOUT_REQUESTED
from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_widget import WxWidget


class wxCustomWindow(wx.Frame):
    """ A custom wxFrame which manages a central widget.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxCustomWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxFrame.

        """
        super(wxCustomWindow, self).__init__(*args, **kwargs)
        self._central_widget = None
        self.SetSizer(wxSingleWidgetSizer())
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
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
    def UpdateClientSizeHints(self):
        """ Update the client size hints for the window.

        This will update the min and max sizes for the window according
        to the current window state. This method is called automatically
        when the central widget is changed.

        """
        sizer = self.GetSizer()
        min_w, min_h = self.ClientToWindowSize(sizer.CalcMin())
        max_w, max_h = self.ClientToWindowSize(sizer.CalcMax())
        self.SetSizeHints(min_w, min_h, max_w, max_h)
        cur_w, cur_h = self.GetSize()
        new_w = min(max_w, max(min_w, cur_w))
        new_h = min(max_h, max(min_h, cur_h))
        if cur_w != new_w or cur_h != new_h:
            self.SetSize(wx.Size(new_w, new_h))

    def GetCentralWidget(self):
        """ Returns the central widget for the window.

        Returns
        -------
        result : wxWindow or None
            The central widget of the window, or None if no widget
            was provided.

        """
        return self._central_widget

    def SetCentralWidget(self, widget):
        """ Set the central widget for this window.

        Parameters
        ----------
        widget : wxWindow
            The widget to use as the content of the window.

        """
        self._central_widget = widget
        self.GetSizer().Add(widget)
        self.UpdateClientSizeHints()


class WxWindow(WxWidget, ProxyWindow):
    """ A Wx implementation of an Enaml ProxyWindow.

    """
    #: A reference tot he toolkit widget created by the proxy.
    widget = Typed(wxCustomWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wxCustomWindow widget.

        """
        self.widget = wxCustomWindow(self.parent_widget())

    def init_widget(self):
        """ Initialize the window control.

        """
        super(WxWindow, self).init_widget()
        d = self.declaration
        if d.title:
            self.set_title(d.title)
        if -1 not in d.initial_size:
            self.widget.SetClientSize(wx.Size(*d.initial_size))
        if -1 not in d.initial_position:
            self.widget.Move(wx.Point(*d.initial_position))
        if d.icon:
            self.set_icon(d.icon)
        self.widget.Bind(wx.EVT_CLOSE, self.on_close)

    def init_layout(self):
        """ Perform layout initialization for the control.

        """
        super(WxWindow, self).init_layout()
        widget = self.widget
        widget.SetCentralWidget(self.central_widget())
        widget.Bind(EVT_COMMAND_LAYOUT_REQUESTED, self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Find and return the central widget child for this widget.

        Returns
        -------
        result : wxWindow or None
            The central widget defined for this widget, or None if one
            is not defined.

        """
        d = self.declaration.central_widget()
        if d is not None:
            return d.proxy.widget or None

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtWindow.

        """
        if isinstance(child, WxContainer):
            self.widget.SetCentralWidget(self.central_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtWindow.

        """
        if isinstance(child, WxContainer):
            self.widget.SetCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_close(self, event):
        """ The event handler for the EVT_CLOSE event.

        """
        event.Skip()
        # Make sure the frame is not modal when closing, or no other
        # windows will be unblocked.
        self.widget.MakeModal(False)
        self.declaration._handle_close()

    def on_layout_requested(self, event):
        """ Handle the layout request event from the central widget.

        """
        # wx likes to send events after the widget is destroyed.
        if self.widget:
            self.widget.UpdateClientSizeHints()

    #--------------------------------------------------------------------------
    # ProxyWindow API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.SetTitle(title)

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        if modality == 'non_modal':
            self.widget.MakeModal(False)
        else:
            self.widget.MakeModal(True)

    def set_icon(self, icon):
        """ This is not supported on Wx.

        """
        pass

    def position(self):
        """ Get the position of the of the window.

        """
        point = self.widget.GetPosition()
        return Pos(point.x, point.y)

    def set_position(self, pos):
        """ Set the position of the window.

        """
        self.widget.SetPosition(wx.Point(*pos))

    def size(self):
        """ Get the size of the window.

        """
        size = self.widget.GetClientSize()
        return Size(size.GetWidth(), size.GetHeight())

    def set_size(self, size):
        """ Set the size of the window.

        """
        size = wx.Size(*size)
        if size.IsFullySpecified():
            self.widget.SetClientSize(size)

    def geometry(self):
        """ Get the geometry of the window.

        """
        # Wx has no standard way of taking into account the size of
        # the window frame. I'm not spending time on a workaround.
        point = self.widget.GetPosition()
        size = self.widget.GetClientSize()
        return Rect(point.x, point.y, size.GetWidth(), size.GetHeight())

    def set_geometry(self, rect):
        """ Set the geometry of the window.

        """
        self.set_position(rect[:2])
        self.set_size(rect[2:])

    def frame_geometry(self):
        """ Get the geometry of the window.

        """
        r = self.widget.GetRect()
        return Rect(r.GetX(), r.GetY(), r.GetWidth(), r.GetHeight())

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.Maximize(True)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.Iconize(True)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.maximize(False)

    def send_to_front(self):
        """ Move the window to the top of the Z order.

        """
        self.widget.Raise()

    def send_to_back(self):
        """ Move the window to the bottom of the Z order.

        """
        self.widget.Lower()

    def center_on_screen(self):
        """ Center the window on the screen.

        """
        self.widget.CenterOnScreen()

    def center_on_widget(self, other):
        """ Center the window on another widget.

        """
        widget = self.widget
        rect = widget.GetRect()
        geo = other.proxy.widget.GetScreenRect()
        widget.Move(rect.CenterIn(geo).GetPosition())

    def close(self):
        """ Close the window

        """
        self.widget.Close()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        This override sets the modality to false when hiding the window
        and enabled it when showing the window (if requested).

        """
        modality = self.declaration.modality
        self.widget.MakeModal(visible and modality != 'non_modal')
        self.widget.Show(visible)

    def ensure_visible(self):
        """ Ensure the widget is visible.

        This override forwards to the 'set_visible' method so that the
        window modality is handled properly.

        """
        self.set_visible(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        This override forwards to the 'set_visible' method so that the
        window modality is handled properly.

        """
        self.set_visible(False)
