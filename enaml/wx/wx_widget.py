#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.widget import ProxyWidget

from .wx_layout_request import wxEvtLayoutRequested
from .wx_resource_helpers import get_cached_wxcolor, get_cached_wxfont
from .wx_toolkit_object import WxToolkitObject


class WxWidget(WxToolkitObject, ProxyWidget):
    """ A Wx implementation of an Enaml ProxyWidget.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(wx.Window)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.Window widget.

        """
        self.widget = wx.Window(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(WxWidget, self).init_widget()
        d = self.declaration
        if d.background:
            self.set_background(d.background)
        if d.foreground:
            self.set_foreground(d.foreground)
        if d.font:
            self.set_font(d.font)
        if -1 not in d.minimum_size:
            self.set_minimum_size(d.minimum_size)
        if -1 not in d.maximum_size:
            self.set_maximum_size(d.maximum_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        self.set_enabled(d.enabled)
        self.set_visible(d.visible)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def update_geometry(self):
        """ Notify the layout system that this widget has changed.

        This method should be called when the geometry of the widget has
        changed and the layout system should update the layout. This will
        post a wxEvtLayoutRequested event to the parent of this widget.

        """
        widget = self.widget
        if widget:
            parent = widget.GetParent()
            if parent:
                event = wxEvtLayoutRequested(widget.GetId())
                wx.PostEvent(parent, event)

    #--------------------------------------------------------------------------
    # ProxyWidget API
    #--------------------------------------------------------------------------
    def set_minimum_size(self, min_size):
        """ Sets the minimum size on the underlying widget.

        """
        self.widget.SetMinSize(wx.Size(*min_size))

    def set_maximum_size(self, max_size):
        """ Sets the maximum size on the underlying widget.

        """
        self.widget.SetMaxSize(wx.Size(*max_size))

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying widget.

        """
        self.widget.Enable(enabled)

    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        """
        self.widget.Show(visible)

    def set_background(self, background):
        """ Set the background color on the underlying widget.

        """
        if background is None:
            wxcolor = wx.NullColour
        else:
            wxcolor = get_cached_wxcolor(background)
        widget = self.widget
        widget.SetBackgroundColour(wxcolor)
        widget.Refresh()

    def set_foreground(self, foreground):
        """ Set the foreground color on the underlying widget.

        """
        if foreground is None:
            wxcolor = wx.NullColour
        else:
            wxcolor = get_cached_wxcolor(foreground)
        widget = self.widget
        widget.SetForegroundColour(wxcolor)
        widget.Refresh()

    def set_font(self, font):
        """ Set the font on the underlying widget.

        """
        wxfont = get_cached_wxfont(font)
        widget = self.widget
        widget.SetFont(wxfont)
        widget.Refresh()

    def set_show_focus_rect(self, show):
        """ This is not supported on Wx.

        """
        pass

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip of for this widget.

        """
        self.widget.SetToolTipString(tool_tip)

    def set_status_tip(self, status_tip):
        """ This is not supported on Wx.

        """
        pass

    def ensure_visible(self):
        """ Ensure the widget is visible.

        """
        self.widget.Show(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        """
        self.widget.Show(False)
