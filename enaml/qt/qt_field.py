#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.field import ProxyField

from .QtCore import QTimer, Signal, Qt
from .QtWidgets import QLineEdit

from .qt_control import QtControl


ECHO_MODES = {
    'normal': QLineEdit.Normal,
    'password': QLineEdit.Password,
    'silent': QLineEdit.NoEcho
}

ALIGN_OPTIONS = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'center': Qt.AlignCenter,
}


class QFocusLineEdit(QLineEdit):
    """ A QLineEdit which converts a lost focus event into a signal.

    """
    lostFocus = Signal()

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

    #: A collapsing timer for auto sync text.
    _text_timer = Typed(QTimer)

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
        self.set_submit_triggers(d.submit_triggers)
        self.set_text_align(d.text_align)
        self.widget.textEdited.connect(self.on_text_edited)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _validate_and_apply(self):
        """ Validate and apply the text in the control.

        """
        d = self.declaration
        v = d.validator

        text = self.widget.text()
        if v and not v.validate(text):
            text = v.fixup(text)
            if not v.validate(text):
                return

        if text != self.widget.text():
            self.widget.setText(text)

        self._clear_error_state()
        d.text = text

    def _set_error_state(self):
        """ Set the error state of the widget.

        """
        # A temporary hack until styles are implemented
        if not self._guard & ERROR_FLAG:
            self._guard |= ERROR_FLAG
            s = u'QLineEdit { border: 2px solid red; background: rgb(255, 220, 220); }'
            self.widget.setStyleSheet(s)
            v = self.declaration.validator
            self.widget.setToolTip(v and v.message or u'')

    def _clear_error_state(self):
        """ Clear the error state of the widget.

        """
        # A temporary hack until styles are implemented
        if self._guard & ERROR_FLAG:
            self._guard &= ~ERROR_FLAG
            self.widget.setStyleSheet(u'')
            self.widget.setToolTip(u'')

    def _maybe_valid(self, text):
        """ Get whether the text is valid or can be valid.

        Returns
        -------
        result : bool
            True if the text is valid, or can be made to be valid,
            False otherwise.

        """
        v = self.declaration.validator
        return v is None or v.validate(text) or v.validate(v.fixup(text))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_submit_text(self):
        """ The signal handler for the text submit triggers.

        """
        self._guard |= TEXT_GUARD
        try:
            self._validate_and_apply()
        finally:
            self._guard &= ~TEXT_GUARD

    def on_text_edited(self):
        """ The signal handler for the 'textEdited' signal.

        """
        if not self._maybe_valid(self.widget.text()):
            self._set_error_state()
        else:
            self._clear_error_state()

        if self._text_timer is not None:
            self._text_timer.start()

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

    def set_submit_triggers(self, triggers):
        """ Set the submit triggers for the widget.

        """
        widget = self.widget
        handler = self.on_submit_text
        try:
            widget.lostFocus.disconnect()
        except (TypeError, RuntimeError):  # was never connected
            pass
        try:
            widget.returnPressed.disconnect()
        except (TypeError, RuntimeError):  # was never connected
            pass
        if 'lost_focus' in triggers:
            widget.lostFocus.connect(handler)
        if 'return_pressed' in triggers:
            widget.returnPressed.connect(handler)
        if 'auto_sync' in triggers:
            if self._text_timer is None:
                timer = self._text_timer = QTimer()
                timer.setSingleShot(True)
                timer.setInterval(300)
                timer.timeout.connect(handler)
        else:
            if self._text_timer is not None:
                self._text_timer.stop()
                self._text_timer = None

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

    def set_text_align(self, text_align):
        """ Set the alignment for the text in the field.

        """
        qt_align = ALIGN_OPTIONS[text_align]
        self.widget.setAlignment(qt_align)

    def field_text(self):
        """ Get the text stored in the widget.

        """
        return self.widget.text()
