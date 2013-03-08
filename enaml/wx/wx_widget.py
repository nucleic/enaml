#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from enaml.colors import parse_color

from .wx_layout_request import wxEvtLayoutRequested
from .wx_object import WxObject


def wx_parse_color(color):
    """ Convert a color string into a wxColour.

    Parameters
    ----------
    color : string
        A CSS3 color string to convert to a wxColour.

    Returns
    -------
    result : wxColour
        The wxColour for the given color string

    """
    rgba = parse_color(color)
    if rgba is None:
        wx_color = wx.NullColour
    else:
        r, g, b, a = rgba
        i = int
        wx_color = wx.Colour(i(r * 255), i(g * 255), i(b * 255), i(a * 255))
    return wx_color


class WxWidget(WxObject):
    """ A Wx implementation of an Enaml WidgetComponent.

    """
    #: An attribute which indicates whether or not the background
    #: color of the widget has been changed.
    _bgcolor_changed = False

    #: An attribute which indicates whether or not the foreground
    #: color of the widget has been changed.
    _fgcolor_changed = False

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wx.Panel widget.

        """
        return wx.Panel(parent)

    def create(self, tree):
        """ Create and initialize the widget control.

        """
        super(WxWidget, self).create(tree)
        self.set_minimum_size(tree['minimum_size'])
        self.set_maximum_size(tree['maximum_size'])
        self.set_bgcolor(tree['bgcolor'])
        self.set_fgcolor(tree['fgcolor'])
        self.set_font(tree['font'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])
        self.set_show_focus_rect(tree['show_focus_rect'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_status_tip(tree['status_tip'])

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def update_geometry(self):
        """ Notify the layout system that this widget has changed.

        This method should be called when the geometry of the widget has
        changed and the layout system should update the layout. This will
        post a wxEvtLayoutRequested event to the parent of this widget.

        """
        widget = self.widget()
        if widget:
            parent = widget.GetParent()
            if parent:
                event = wxEvtLayoutRequested(widget.GetId())
                wx.PostEvent(parent, event)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_enabled(self, content):
        """ Handle the 'set_enabled' action from the Enaml widget.

        """
        self.set_enabled(content['enabled'])

    def on_action_set_visible(self, content):
        """ Handle the 'set_visible' action from the Enaml widget.

        """
        self.set_visible(content['visible'])

    def on_action_set_bgcolor(self, content):
        """ Handle the 'set_bgcolor' action from the Enaml widget.

        """
        self.set_bgcolor(content['bgcolor'])

    def on_action_set_fgcolor(self, content):
        """ Handle the 'set_fgcolor' action from the Enaml widget.

        """
        self.set_fgcolor(content['fgcolor'])

    def on_action_set_font(self, content):
        """ Handle the 'set_font' action from the Enaml widget.

        """
        self.set_font(content['font'])

    def on_action_set_minimum_size(self, content):
        """ Handle the 'set_minimum_size' action from the Enaml widget.

        """
        self.set_minimum_size(content['minimum_size'])

    def on_action_set_maximum_size(self, content):
        """ Handle the 'set_maximum_size' action from the Enaml widget.

        """
        self.set_maximum_size(content['maximum_size'])

    def on_action_set_show_focus_rect(self, content):
        """ Handle the 'set_show_focus_rect' action from the Enaml
        widget.

        """
        self.set_show_focus_rect(content['show_focus_rect'])

    def on_action_set_tool_tip(self, content):
        """ Handle the 'set_tool_tip' action from the Enaml widget.

        """
        self.set_tool_tip(content['tool_tip'])

    def on_action_set_status_tip(self, content):
        """ Handle the 'set_status_tip' action from the Enaml widget.

        """
        self.set_status_tip(content['status_tip'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_minimum_size(self, min_size):
        """ Sets the minimum size on the underlying widget.

        Parameters
        ----------
        min_size : (int, int)
            The minimum size allowable for the widget. A value of
            (-1, -1) indicates the default min size.

        """
        self.widget().SetMinSize(wx.Size(*min_size))

    def set_maximum_size(self, max_size):
        """ Sets the maximum size on the underlying widget.

        Parameters
        ----------
        max_size : (int, int)
            The minimum size allowable for the widget. A value of
            (-1, -1) indicates the default max size.

        """
        self.widget().SetMaxSize(wx.Size(*max_size))

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying widget.

        Parameters
        ----------
        enabled : bool
            Whether or not the widget is enabled.

        """
        self.widget().Enable(enabled)

    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        Parameters
        ----------
        visible : bool
            Whether or not the widget is visible.

        """
        self.widget().Show(visible)

    def set_bgcolor(self, bgcolor):
        """ Set the background color on the underlying widget.

        Parameters
        ----------
        bgcolor : str
            The background color of the widget as a CSS color string.

        """
        if bgcolor or self._bgcolor_changed:
            wx_color = wx_parse_color(bgcolor)
            widget = self.widget()
            widget.SetBackgroundColour(wx_color)
            widget.Refresh()
            self._bgcolor_changed = True

    def set_fgcolor(self, fgcolor):
        """ Set the foreground color on the underlying widget.

        Parameters
        ----------
        fgcolor : str
            The foreground color of the widget as a CSS color string.

        """
        if fgcolor or self._fgcolor_changed:
            wx_color = wx_parse_color(fgcolor)
            widget = self.widget()
            widget.SetForegroundColour(wx_color)
            widget.Refresh()
            self._fgcolor_changed = True

    def set_font(self, font):
        """ Set the font on the underlying widget.

        Parameters
        ----------
        font : str
            The font for the widget as a CSS font string.

        """
        pass

    def set_show_focus_rect(self, show):
        """ Sets whether or not to show the focus rectangle around
        the widget.

        This is currently not supported on Wx.

        """
        pass

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip of for this widget.

        """
        self.widget().SetToolTipString(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip of for this widget.

        """
        # Status tips are not currently supported on Wx
        pass

