#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

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
        max_w, max_h= self.ClientToWindowSize(sizer.CalcMax())
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


class WxWindow(WxWidget):
    """ A Wx implementation of an Enaml Window.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Frame widget.

        """
        return wxCustomWindow(parent)

    def create(self, tree):
        """ Create and initialize the window control.

        """
        super(WxWindow, self).create(tree)
        self.set_title(tree['title'])
        self.set_initial_size(tree['initial_size'])
        self.set_modality(tree['modality'])
        self.widget().Bind(wx.EVT_CLOSE, self.on_close)

    def init_layout(self):
        """ Perform layout initialization for the control.

        """
        super(WxWindow, self).init_layout()
        widget = self.widget()
        widget.SetCentralWidget(self.central_widget())
        widget.Bind(EVT_COMMAND_LAYOUT_REQUESTED, self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Find and return the central widget child for this widget.

        Returns
        -------
        result : wxWindos or None
            The central widget defined for this widget, or None if one
            is not defined.

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
        """ Handle the child removed event for a QtWindow.

        """
        if isinstance(child, WxContainer):
            self.widget().SetCentralWidget(self.central_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtWindow.

        """
        if isinstance(child, WxContainer):
            self.widget().SetCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_close(self, event):
        """ The event handler for the EVT_CLOSE event.

        """
        event.Skip()
        # Make sure the frame is not modal when closing, or no other
        # windows will be unblocked.
        self.widget().MakeModal(False)
        self.send_action('closed', {})

    def on_layout_requested(self, event):
        """ Handle the layout request event from the central widget.

        """
        self.widget().UpdateClientSizeHints()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.close()

    def on_action_maximize(self, content):
        """ Handle the 'maximize' action from the Enaml widget.

        """
        self.maximize()

    def on_action_minimize(self, content):
        """ Handle the 'minimize' action from the Enaml widget.

        """
        self.minimize()

    def on_action_restore(self, content):
        """ Handle the 'restore' action from the Enaml widget.

        """
        self.restore()

    def on_action_set_icon_source(self, content):
        """ Handle the 'set_icon_source' action from the Enaml widget.

        """
        pass

    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_modality(self, content):
        """ Handle the 'set_modality' action from the Enaml widget.

        """
        self.set_modality(content['modality'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget().Close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget().Maximize(True)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget().Iconize(True)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget().Maximize(False)

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget().SetTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        self.widget().SetSize(wx.Size(*size))

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        if modality == 'non_modal':
            self.widget().MakeModal(False)
        else:
            self.widget().MakeModal(True)

    def set_visible(self, visible):
        """ Set the visibility on the window.

        This is an overridden parent class method to set the visibility
        at a later time, so that layout can be initialized before the
        window is displayed.

        """
        # XXX this could be done better.
        wx.CallAfter(super(WxWindow, self).set_visible, visible)

