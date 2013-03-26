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

from enaml.widgets.check_box import ProxyCheckBox

from .wx_abstract_button import WxAbstractButton, CHECKED_GUARD


#: A check box event emitted when the button is clicked.
wxCheckBoxClicked, EVT_CHECKBOX_CLICKED = wx.lib.newevent.NewEvent()

#: A check event emitted when the button value is changed.
wxCheckBoxToggled, EVT_CHECKBOX_TOGGLED = wx.lib.newevent.NewEvent()


class wxProperCheckBox(wx.CheckBox):
    """ A custom subclass of wx.CheckBox.

    This checkbox emits an EVT_CHECKBOX_CLICKED event whenever the
    button is clicked. It also emits an EVT_CHECKBOX_TOGGLED whenever
    the checkbox changes state.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxProperCheckBox.

        *args, **kwargs
            The positional and keyword arguments required to initialize
            a wx.RadioButton.

        """
        super(wxProperCheckBox, self).__init__(*args, **kwargs)
        self._in_click = False
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggled)

    def OnLeftDown(self, event):
        """ Handles the left down mouse event for the check box.

        This is first part of generating a click event.

        """
        event.Skip()
        self._in_click = True

    def OnLeftUp(self, event):
        """ Handles the left up mouse event for the check box.

        This is the second part of generating a click event.

        """
        event.Skip()
        if self._in_click:
            self._in_click = False
            event = wxCheckBoxClicked()
            wx.PostEvent(self, event)

    def OnToggled(self, event):
        """ Handles the standard toggle event and emits the custom
        toggle event for the check box.

        """
        event = wxCheckBoxToggled()
        wx.PostEvent(self, event)

    def SetValue(self, val):
        """ Overrides the default SetValue method to emit proper events.

        """
        old = self.GetValue()
        if old != val:
            super(wxProperCheckBox, self).SetValue(val)
            self._last = val
            event = wxCheckBoxToggled()
            wx.PostEvent(self, event)


class WxCheckBox(WxAbstractButton, ProxyCheckBox):
    """ A Wx implementation of an Enaml ProxyCheckBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxProperCheckBox)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying check box widget.

        """
        self.widget = wxProperCheckBox(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the check box control.

        """
        super(WxCheckBox, self).init_widget()
        widget = self.widget
        widget.Bind(EVT_CHECKBOX_CLICKED, self.on_clicked)
        widget.Bind(EVT_CHECKBOX_TOGGLED, self.on_toggled)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        This is not supported in Wx.

        """
        pass

    def get_checked(self):
        """ Returns the checked state of the widget.

        """
        return self.widget.GetValue()

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        self._guard |= CHECKED_GUARD
        try:
            self.widget.SetValue(checked)
        finally:
            self._guard &= ~CHECKED_GUARD
