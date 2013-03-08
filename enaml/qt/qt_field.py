#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.validation.client_validators import null_validator, make_validator

from .qt.QtGui import QLineEdit
from .qt.QtCore import Signal
from .qt_control import QtControl


ECHO_MODES = {
    'normal': QLineEdit.Normal,
    'password' : QLineEdit.Password,
    'silent' : QLineEdit.NoEcho
}


class QtFocusLineEdit(QLineEdit):
    """ A QLineEdit subclass which converts a lost focus event into
    a lost focus signal.

    """
    lostFocus = Signal()

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        return super(QtFocusLineEdit, self).focusOutEvent(event)


class QtField(QtControl):
    """ A Qt4 implementation of an Enaml Field.

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
        """ Creates the underlying QLineEdit widget.

        """
        return QtFocusLineEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtField, self).create(tree)
        self.set_text(tree['text'])
        self.set_validator(tree['validator'])
        self.set_submit_triggers(tree['submit_triggers'])
        self.set_placeholder(tree['placeholder'])
        self.set_echo_mode(tree['echo_mode'])
        self.set_max_length(tree['max_length'])
        self.set_read_only(tree['read_only'])
        widget = self.widget()
        widget.lostFocus.connect(self.on_lost_focus)
        widget.returnPressed.connect(self.on_return_pressed)
        widget.textEdited.connect(self.on_text_edited)

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
        text = self.widget().text()
        if text != self._last_value:
            if self._validator(text):
                self._clear_error_style()
                self._submit_text(text)
                self._last_value = text
            else:
                self._set_error_style()

    def _set_error_style(self):
        # A temporary hack until styles are implemented
        s = 'QLineEdit { border: 2px solid red; background: rgb(255, 220, 220); }'
        self.widget().setStyleSheet(s)
        self._is_error_state = True

    def _clear_error_style(self):
        # A temporary hack until styles are implemented
        self.widget().setStyleSheet('')
        self._is_error_state = False

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_lost_focus(self):
        """ The signal handler for 'lostFocus' signal.

        """
        if 'lost_focus' in self._submit_triggers:
            self._validate_and_submit()

    def on_return_pressed(self):
        """ The signal handler for 'returnPressed' signal.

        """
        if 'return_pressed' in self._submit_triggers:
            self._validate_and_submit()

    def on_text_edited(self):
        # Temporary kludge until styles are fully implemented
        widget = self.widget()
        if self._validator(widget.text()):
            if self._is_error_state:
                self._clear_error_style()
                widget.setToolTip('')
        else:
            if not self._is_error_state:
                self._set_error_style()
                widget.setToolTip(self._validator_message)

    #--------------------------------------------------------------------------
    # Message Handlers
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
        self.set_submit_triggers(content['submit_triggers'])

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
        if self.widget().text() == content['text']:
            self._set_error_style()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget().setText(text)
        self._last_value = text
        self._clear_error_style()

    def set_validator(self, validator):
        """ Set the validator for the underlying widget.

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

    def set_placeholder(self, text):
        """ Set the placeholder text of the underlying widget.

        """
        self.widget().setPlaceholderText(text)

    def set_echo_mode(self, mode):
        """ Set the echo mode of the underlying widget.

        """
        self.widget().setEchoMode(ECHO_MODES[mode])

    def set_max_length(self, length):
        """ Set the maximum text length in the underlying widget.

        """
        if length <= 0 or length > 32767:
            length = 32767
        self.widget().setMaxLength(length)

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget().setReadOnly(read_only)

