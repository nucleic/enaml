#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Int, Typed

from enaml.widgets.field import ProxyField

from .wx_control import WxControl


class wxLineEdit(wx.TextCtrl):
    """ A wx.TextCtrl subclass which is similar to a QLineEdit in terms
    of features and behavior.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxLineEdit.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.TextCtrl.

        """
        super(wxLineEdit, self).__init__(*args, **kwargs)
        self._placeholder_text = ''
        self._placeholder_active = False
        self._user_fgcolor = None
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _UpdatePlaceholderDisplay(self):
        """ Updates the display with the placeholder text if no text
        is currently set for the control.

        """
        if not self.GetValue() and self._placeholder_text:
            self.ChangeValue(self._placeholder_text)
            color = wx.Color(95, 95, 95)
            super(wxLineEdit, self).SetForegroundColour(color)
            self._placeholder_active = True

    def _RemovePlaceholderDisplay(self):
        """ Removes the placeholder text if it is currently active.

        """
        if self._placeholder_active:
            self.ChangeValue('')
            color = self._user_fgcolor or wx.Color(0, 0, 0)
            super(wxLineEdit, self).SetForegroundColour(color)
            self._placeholder_active = False

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnKillFocus(self, event):
        """ Refreshes the placeholder display when the control loses
        focus.

        """
        self._UpdatePlaceholderDisplay()
        event.Skip()

    def OnSetFocus(self, event):
        """ Removes the placeholder display when the control receives
        focus.

        """
        self._RemovePlaceholderDisplay()
        event.Skip()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden best size method to add 44 pixels in width to the
        field. This makes Wx consistent with Qt.

        """
        size = super(wxLineEdit, self).GetBestSize()
        return wx.Size(size.GetWidth() + 44, size.GetHeight())

    def SetPlaceHolderText(self, placeholder_text):
        """ Sets the placeholder text to the given value. Pass an empty
        string to turn off the placeholder text functionality.

        """
        self._placeholder_text = placeholder_text
        self._UpdatePlaceholderDisplay()

    def GetPlaceHolderText(self):
        """ Returns the placeholder text for this control.

        """
        return self._placeholder_text

    def ChangeValue(self, text):
        """ Overridden method which moves the insertion point to the end
        of the field when changing the text value. This causes the field
        to behave like Qt.

        """
        super(wxLineEdit, self).ChangeValue(text)
        self.SetInsertionPoint(len(text))

    def GetValue(self):
        """ Returns string value in the control, or an empty string if
        the placeholder text is active.

        """
        if self._placeholder_active:
            return ''
        return super(wxLineEdit, self).GetValue()

    def SetForegroundColour(self, wxColor, force=False):
        """ Sets the foreground color of the field. If the placeholder
        text is being shown, `force` must be True in order to override
        the placeholder text color.

        """
        self._user_fgcolor = wxColor
        if self._placeholder_active and not force:
            return
        super(wxLineEdit, self).SetForegroundColour(wxColor)


# Guard flags
TEXT_GUARD = 0x1
ERROR_FLAG = 0x2


class WxField(WxControl, ProxyField):
    """ A Wx implementation of an Enaml ProxyField.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxLineEdit)

    #: A collapsing timer for auto sync text.
    _text_timer = Typed(wx.Timer)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wxLineEdit widget.

        """
        # We have to do a bit of initialization in the create method
        # since wx requires the style of certain things to be set at
        # the point of instantiation
        d = self.declaration
        style = wx.TE_PROCESS_ENTER
        if d.read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        if d.echo_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        else:
            style |= wx.TE_PASSWORD
        self.widget = wxLineEdit(self.parent_widget(), style=style)

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(WxField, self).init_widget()
        d = self.declaration
        if d.text:
            self.set_text(d.text)
        if d.mask:
            self.set_mask(d.mask)
        if d.placeholder:
            self.set_placeholder(d.placeholder)
        self.set_echo_mode(d.echo_mode)
        self.set_max_length(d.max_length)
        self.set_read_only(d.read_only)
        self.set_submit_triggers(d.submit_triggers)
        self.widget.Bind(wx.EVT_TEXT, self.on_text_edited)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _validate_and_apply(self):
        """ Validate and apply the text in the control.

        """
        d = self.declaration
        text = self.widget.GetValue()
        if d.validator and not d.validator.validate(text):
            text = d.validator.fixup(text)
            if not d.validator.validate(text):
                return
        self._clear_error_state()
        d.text = text

    def _set_error_state(self):
        """ Set the error state of the widget.

        """
        # A temporary hack until styles are implemented
        if not self._guard & ERROR_FLAG:
            self._guard |= ERROR_FLAG
            # XXX attempting to change the field style here is futile

    def _clear_error_state(self):
        """ Clear the error state of the widget.

        """
        # A temporary hack until styles are implemented
        if self._guard & ERROR_FLAG:
            self._guard &= ~ERROR_FLAG
            # XXX attempting to change the field style here is futile

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def on_submit_text(self, event):
        """ The event handler for the text submit triggers.

        """
        # Only skip the focus event: wx triggers the system beep if the
        # enter event is skipped.
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        self._guard |= TEXT_GUARD
        try:
            self._validate_and_apply()
        finally:
            self._guard &= ~TEXT_GUARD

    def on_text_edited(self, event):
        """ The event handler for the text edited event.

        """
        # Temporary kludge until error style is fully implemented
        d = self.declaration
        if d.validator and not d.validator.validate(self.widget.GetValue()):
            self._set_error_state()
            self.widget.SetToolTip(wx.ToolTip(d.validator.message))
        else:
            self._clear_error_state()
            self.widget.SetToolTip(wx.ToolTip(''))
        if self._text_timer is not None:
            self._text_timer.Start(300, oneShot=True)

    #--------------------------------------------------------------------------
    # ProxyField API
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        if not self._guard & TEXT_GUARD:
            self.widget.ChangeValue(text)
            self._clear_error_state()

    def set_mask(self, mask):
        """ Set the make for the widget.

        This is not supported in Wx.

        """
        pass

    def set_submit_triggers(self, triggers):
        """ Set the submit triggers for the widget.

        """
        widget = self.widget
        handler = self.on_submit_text
        widget.Unbind(wx.EVT_KILL_FOCUS, handler=handler)
        widget.Unbind(wx.EVT_TEXT_ENTER, handler=handler)
        if 'lost_focus' in triggers:
            widget.Bind(wx.EVT_KILL_FOCUS, handler)
        if 'return_pressed' in triggers:
            widget.Bind(wx.EVT_TEXT_ENTER, handler)
        if 'auto_sync' in triggers:
            if self._text_timer is None:
                timer = self._text_timer = wx.Timer()
                timer.Bind(wx.EVT_TIMER, handler)
        else:
            if self._text_timer is not None:
                self._text_timer.Stop()
                self._text_timer = None

    def set_placeholder(self, placeholder):
        """ Sets the placeholder text in the widget.

        """
        self.widget.SetPlaceHolderText(placeholder)

    def set_echo_mode(self, echo_mode):
        """ Sets the echo mode of the wiget.

        """
        # Wx cannot change the echo mode dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

    def set_max_length(self, max_length):
        """ Set the max length of the control to max_length. If the max
        length is <= 0 or > 32767 then the control will be set to hold
        32kb of text.

        """
        if (max_length <= 0) or (max_length > 32767):
            max_length = 32767
        self.widget.SetMaxLength(max_length)

    def set_read_only(self, read_only):
        """ Sets the read only state of the widget.

        """
        # Wx cannot change the read only state dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

    def field_text(self):
        """ Get the text stored in the widget.

        """
        return self.widget.GetValue()
