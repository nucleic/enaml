#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QLineEdit
from PyQt4.QtCore import pyqtSignal

from atom.api import Int, Typed

from enaml.widgets.field import ProxyField

from .qt_control import QtControl


ECHO_MODES = {
    'normal': QLineEdit.Normal,
    'password': QLineEdit.Password,
    'silent': QLineEdit.NoEcho
}


class QFocusLineEdit(QLineEdit):
    """ A QLineEdit which converts a lost focus event into a signal.

    """
    lostFocus = pyqtSignal()

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        return super(QFocusLineEdit, self).focusOutEvent(event)


# Guard flags
TEXT_GUARD = 0x1
ERROR_FLAG = 0x2


class QtField(QtControl, ProxyField):
    """ A Qt4 implementation of an Enaml ProxyField.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFocusLineEdit)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QFocusLineEdit widget.

        """
        self.widget = QFocusLineEdit(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtField, self).init_widget()
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
        widget = self.widget
        widget.lostFocus.connect(self.on_lost_focus)
        widget.returnPressed.connect(self.on_return_pressed)
        widget.textEdited.connect(self.on_text_edited)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _validate_and_apply(self):
        """ Validate and apply the text in the control.

        """
        d = self.declaration
        text = self.widget.text()
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
            s = 'QLineEdit { border: 2px solid red; background: rgb(255, 220, 220); }'
            self.widget.setStyleSheet(s)

    def _clear_error_state(self):
        """ Clear the error state of the widget.

        """
        # A temporary hack until styles are implemented
        if self._guard & ERROR_FLAG:
            self._guard &= ~ERROR_FLAG
            self.widget.setStyleSheet('')

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_lost_focus(self):
        """ The signal handler for 'lostFocus' signal.

        """
        if 'lost_focus' in self.declaration.submit_triggers:
            self._guard |= TEXT_GUARD
            try:
                self._validate_and_apply()
            finally:
                self._guard &= ~TEXT_GUARD

    def on_return_pressed(self):
        """ The signal handler for 'returnPressed' signal.

        """
        if 'return_pressed' in self.declaration.submit_triggers:
            self._guard |= TEXT_GUARD
            try:
                self._validate_and_apply()
            finally:
                self._guard &= ~TEXT_GUARD

    def on_text_edited(self):
        """ The signal handler for the 'textEdited' signal.

        """
        # Temporary kludge until error style is fully implemented
        d = self.declaration
        if d.validator and not d.validator.validate(self.widget.text()):
            self._set_error_state()
            self.widget.setToolTip(d.validator.message)
        else:
            self._clear_error_state()
            self.widget.setToolTip(u'')

    #--------------------------------------------------------------------------
    # ProxyField API
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the widget.

        """
        if not self._guard & TEXT_GUARD:
            self.widget.setText(text)
            self._clear_error_state()

    def set_mask(self, mask):
        """ Set the make for the widget.

        """
        self.widget.setInputMask(mask)

    def set_placeholder(self, text):
        """ Set the placeholder text of the widget.

        """
        self.widget.setPlaceholderText(text)

    def set_echo_mode(self, mode):
        """ Set the echo mode of the widget.

        """
        self.widget.setEchoMode(ECHO_MODES[mode])

    def set_max_length(self, length):
        """ Set the maximum text length in the widget.

        """
        if length <= 0 or length > 32767:
            length = 32767
        self.widget.setMaxLength(length)

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget.setReadOnly(read_only)

    def field_text(self):
        """ Get the text stored in the widget.

        """
        return self.widget.text()
