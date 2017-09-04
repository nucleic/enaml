#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.multiline_field import ProxyMultilineField

from .QtCore import QTimer, Signal
from .QtWidgets import QTextEdit

from .qt_control import QtControl


class QMultilineEdit(QTextEdit):
    """ A QTextEdit which notifies on a collapsing timer.

    """
    #: A signal emitted on a collapsing timer. Delayed text must be
    #: enabled for this signal to be fired.
    delayedTextChanged = Signal()

    #: Internal storage for the timer object.
    _dtimer = None

    def delayedTextEnabled(self):
        """ Get when the delayedTextChanged signal is enabled.

        """
        return self._dtimer is not None

    def setDelayedTextEnabled(self, enabled):
        """ Set whether the delayedTextChanged signal is enabled.

        """
        if enabled:
            if not self._dtimer:
                self._dtimer = timer = QTimer()
                timer.setInterval(300)
                timer.setSingleShot(True)
                timer.timeout.connect(self.delayedTextChanged)
                self.textChanged.connect(timer.start)
        else:
            if self._dtimer:
                self.textChanged.disconnect(self._dtimer.start)
                self._dtimer.timeout.disconnect(self.delayedTextChanged)
                self._dtimer = None


#: cyclic notification guard flag
TEXT_GUARD = 0x1


class QtMultilineField(QtControl, ProxyMultilineField):
    """ A Qt4 implementation of an Enaml ProxyMultilineField.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QMultilineEdit)

    #: A bitfield of guard flags.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QFocusMultiLineEdit widget.

        """
        self.widget = QMultilineEdit(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtMultilineField, self).init_widget()
        d = self.declaration
        self.set_text(d.text)
        self.set_read_only(d.read_only)
        self.set_auto_sync_text(d.auto_sync_text)
        self.widget.delayedTextChanged.connect(self.on_delayed_text_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_delayed_text_changed(self):
        """ The signal handler for 'delayedTextChanged' signal.

        This handler will only be invoked if auto sync is enabled on the
        declaration.

        """
        self.sync_text()

    #--------------------------------------------------------------------------
    # ProxyMultilineField API
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        if not self._guard & TEXT_GUARD:
            self._guard |= TEXT_GUARD
            try:
                self.widget.setText(text)
            finally:
                self._guard &= ~TEXT_GUARD

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget.setReadOnly(read_only)

    def set_auto_sync_text(self, sync):
        """ Set the auto sync text behavior on the widget.

        """
        self.widget.setDelayedTextEnabled(sync)

    def sync_text(self):
        """ Force syncronize the text.

        """
        if not self._guard & TEXT_GUARD:
            self._guard |= TEXT_GUARD
            try:
                self.declaration.text = self.widget.toPlainText()
            finally:
                self._guard &= ~TEXT_GUARD

    def field_text(self):
        """ Get the text in the field.

        """
        return self.widget.toPlainText()
