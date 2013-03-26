#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from weakref import WeakKeyDictionary

import wx
import wx.lib.newevent

from atom.api import Typed

from enaml.widgets.radio_button import ProxyRadioButton

from .wx_abstract_button import WxAbstractButton, CHECKED_GUARD


#: A radio button event that is emited when the button is clicked.
wxRadioClicked, EVT_RADIO_CLICKED = wx.lib.newevent.NewEvent()

#: A radio button event emitted when the button value is changed.
wxRadioToggled, EVT_RADIO_TOGGLED = wx.lib.newevent.NewEvent()


class wxProperRadioButton(wx.RadioButton):
    """ A custom stubclass of wx.RadioButton.

    The wx.RadioButton doesn't emit toggled events when it unchecks the
    other radio buttons in the same group. So, the only time an
    EVT_RADIOBUTTON is emitted is when the button changes from off to
    on. This custom subclass does some orchestration and will emit an
    EVT_RADIO_TOGGLED whenever the control changes its value. It also
    emits an EVT_RADIO_CLICKED event when the control is clicked, even
    if the click doesn't change the value in the control.

    """
    #: The WeakKeyDictionary which stores the sibling radio buttons
    #: for a given parent widget. When any radio button is toggled,
    #: the list of siblings is iterated and each child is given the
    #: the chance to see it's been toggled off. If it has, then it
    #: will emit a toggled event.
    _parents = WeakKeyDictionary()

    def __init__(self, *args, **kwargs):
        """ Initialize a wxProperRadioButton.

        *args, **kwargs
            The positional and keyword arguments required to initialize
            a wx.RadioButton.

        """
        super(wxProperRadioButton, self).__init__(*args, **kwargs)
        parent = self.GetParent()
        if parent:
            children = self._parents.setdefault(parent, [])
            children.append(self)
        self._last = self.GetValue()
        self._in_click = False
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnToggled)

    def OnLeftDown(self, event):
        """ Handles the left down mouse event for the radio button.

        This is first part of generating a click event.

        """
        event.Skip()
        self._in_click = True

    def OnLeftUp(self, event):
        """ Handles the left up mouse event for the radio button.

        This is the second part of generating a click event.

        """
        event.Skip()
        if self._in_click:
            self._in_click = False
            event = wxRadioClicked()
            wx.PostEvent(self, event)

    def OnToggled(self, event):
        """ Handles the standard toggle event and emits a toggle on
        event. After emitting that event, it will cycle through the
        list of its siblings and give them a change to emit a toggle
        off event.

        """
        self._last = self.GetValue()
        event = wxRadioToggled()
        wx.PostEvent(self, event)
        self.CheckSiblings()

    def CheckToggledOff(self):
        """ Checks the state of the radio button to see if it has been
        toggled from on to off. If it has, it will emit a toggle off
        event.

        """
        last = self._last
        curr = self.GetValue()
        if not curr and last:
            self._last = curr
            event = wxRadioToggled()
            wx.PostEvent(self, event)

    def CheckSiblings(self):
        """ Iterates over the siblings of this radio button, giving
        each a chance to respond to a possible toggle off.

        """
        parent = self.GetParent()
        if parent:
            parents = self._parents
            if parent in parents:
                for child in parents[parent]:
                    child.CheckToggledOff()

    def SetValue(self, val):
        """ Overrides the default SetValue method to emit proper events.

        """
        old = self.GetValue()
        if old != val:
            super(wxProperRadioButton, self).SetValue(val)
            self._last = val
            event = wxRadioToggled()
            wx.PostEvent(self, event)
            self.CheckSiblings()

    def Destroy(self):
        """ Overridden destroy method to remove the radio button from
        the list of siblings before it's destroyed.

        """
        parent = self.GetParent()
        if parent:
            parents = self._parents
            if parent in parents:
                children = parents[parent]
                try:
                    children.remove(self)
                except ValueError:
                    pass
        super(wxProperRadioButton, self).Destroy()


class WxRadioButton(WxAbstractButton, ProxyRadioButton):
    """ A Wx implementation of an Enaml ProxyRadioButton.

    WxRadioButton uses a custom wx.RadioButton control. Radio buttons
    with the same parent will be mutually exclusive. For independent
    groups, place them in their own parent component.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxProperRadioButton)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying custom wx.RadioButton control.

        """
        self.widget = wxProperRadioButton(self.parent_widget())

    def init_widget(self):
        """ Initialize the radio button control.

        """
        super(WxRadioButton, self).init_widget()
        widget = self.widget
        widget.Bind(EVT_RADIO_CLICKED, self.on_clicked)
        widget.Bind(EVT_RADIO_TOGGLED, self.on_toggled)

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
