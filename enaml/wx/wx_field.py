#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from enaml.validation.client_validators import null_validator, make_validator

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


class WxField(WxControl):
    """ A Wx implementation of an Enaml Field.

    """
    #: The client side validator function for the field.
    _validator = null_validator

    #: The validator message for the validator.
    _validator_message = ''

    #: The list of submit triggers for when to submit a text change.
    _submit_triggers = []

    #: The last text value submitted to or sent from the server.
    _last_value = None

    #: A flag indicating whether the current field is invalid.
    _is_error_state = False

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wxLineEdit.

        """
        # We have to do a bit of initialization in the create method
        # since wx requires the style of certain things to be set at
        # the point of instantiation
        style = wx.TE_PROCESS_ENTER
        if tree['read_only']:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        echo_mode = tree['echo_mode']
        if echo_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        else:
            style |= wx.TE_PASSWORD
        read_only = tree['read_only']
        if read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        return wxLineEdit(parent, style=style)

    def create(self, tree):
        """ Create and initialize the wx field control.

        """
        super(WxField, self).create(tree)
        self.set_text(tree['text'])
        self.set_validator(tree['validator'])
        self.set_submit_triggers(tree['submit_triggers'])
        self.set_placeholder(tree['placeholder'])
        self.set_max_length(tree['max_length'])
        widget = self.widget()
        widget.Bind(wx.EVT_KILL_FOCUS, self.on_lost_focus)
        widget.Bind(wx.EVT_TEXT_ENTER, self.on_return_pressed)
        widget.Bind(wx.EVT_TEXT, self.on_text_edited)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _submit_text(self, text):
        """ Submit the given text as an update to the server widget.

        Parameters
        ----------
        text : unicode
            The unicode text to send to the server widget.

        """
        content = {'text': text}
        self.send_action('submit_text', content)

    def _validate_and_submit(self):
        """ Validate the current text in the control, and submit it to
        the server widget if it's valid.

        """
        text = self.widget().GetValue()
        if text != self._last_value:
            if self._validator(text):
                self._clear_error_style()
                self._submit_text(text)
                self._last_value = text
            else:
                self._set_error_style()

    def _set_error_style(self):
        # A temporary hack until styles are implemented
        self._is_error_state = True
        # XXX attempting to change the field style here is futile

    def _clear_error_style(self):
        # A temporary hack until styles are implemented
        self._is_error_state = False
        # XXX attempting to change the field style here is futile

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def on_lost_focus(self, event):
        """ The event handler for EVT_KILL_FOCUS event.

        """
        event.Skip()
        if 'lost_focus' in self._submit_triggers:
            self._validate_and_submit()

    def on_return_pressed(self, event):
        """ The event handler for EVT_TEXT_ENTER event.

        """
        # don't skip or Wx triggers the system beep, grrrrrrr.....
        #event.Skip()
        if 'return_pressed' in self._submit_triggers:
            self._validate_and_submit()

    def on_text_edited(self, event):
        # Temporary kludge until styles are fully implemented
        event.Skip()
        widget = self.widget()
        if self._validator(widget.GetValue()):
            if self._is_error_state:
                self._clear_error_style()
                widget.SetToolTip(wx.ToolTip(''))
        else:
            if not self._is_error_state:
                self._set_error_style()
                widget.SetToolTip(wx.ToolTip(self._validator_message))

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_validator(self, content):
        """ Handle the 'set_validator' action from the Enaml widget.

        """
        self.set_validator(content['validator'])

    def on_action_set_submit_triggers(self, content):
        """ Handle the 'set_submit_triggers' action from the Enaml
        widget.

        """
        self.set_submit_triggers(content['sumbit_triggers'])

    def on_action_set_placeholder(self, content):
        """ Hanlde the 'set_placeholder' action from the Enaml widget.

        """
        self.set_placeholder(content['placeholder'])

    def on_action_set_echo_mode(self, content):
        """ Handle the 'set_echo_mode' action from the Enaml widget.

        """
        self.set_echo_mode(content['echo_mode'])

    def on_action_set_max_length(self, content):
        """ Handle the 'set_max_length' action from the Enaml widget.

        """
        self.set_max_length(content['max_length'])

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    def on_action_invalid_text(self, content):
        """ Handle the 'invalid_text' action from the Enaml widget.

        """
        if self.widget().GetValue() == content['text']:
            self._set_error_style()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        self.widget().ChangeValue(text)
        self._last_value = text
        self._clear_error_style()

    def set_validator(self, validator):
        """ Sets the validator for the control.

        """
        if validator is None:
            self._validator = null_validator
            self._validator_message = ''
        else:
            self._validator = make_validator(validator)
            self._validator_message = validator.get('message', '')

    def set_submit_triggers(self, triggers):
        """ Set the submit triggers for the underlying widget.

        """
        self._submit_triggers = triggers

    def set_placeholder(self, placeholder):
        """ Sets the placeholder text in the widget.

        """
        self.widget().SetPlaceHolderText(placeholder)

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
        self.widget().SetMaxLength(max_length)

    def set_read_only(self, read_only):
        """ Sets the read only state of the widget.

        """
        # Wx cannot change the read only state dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

