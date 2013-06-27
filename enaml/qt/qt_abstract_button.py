#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.abstract_button import ProxyAbstractButton

from .QtCore import QSize
from .QtGui import QAbstractButton, QIcon

from .q_resource_helpers import get_cached_qicon
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl


# cyclic notification guard flags
CHECKED_GUARD = 0x1


class QtAbstractButton(QtControl, ProxyAbstractButton):
    """ A Qt implementation of the Enaml ProxyAbstractButton.

    This class can serve as a base class for widgets that implement
    button behavior such as CheckBox, RadioButton and PushButtons.
    It is not meant to be used directly.

    """
    #: A reference to the widget created by the proxy
    widget = Typed(QAbstractButton)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Implement in a subclass to create the widget.

        """
        raise NotImplementedError

    def init_widget(self):
        """ Initialize the button widget.

        """
        super(QtAbstractButton, self).init_widget()
        d = self.declaration
        if d.text:
            self.set_text(d.text, sh_guard=False)
        if d.icon:
            self.set_icon(d.icon, sh_guard=False)
        if -1 not in d.icon_size:
            self.set_icon_size(d.icon_size, sh_guard=False)
        self.set_checkable(d.checkable)
        self.set_checked(d.checked)
        widget = self.widget
        widget.clicked.connect(self.on_clicked)
        widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self):
        """ The signal handler for the 'clicked' signal.

        """
        # PySide does pass the 'checked' arg to the slot like PyQt, so
        # grab the checked attribute directly, which works on both.
        checked = self.widget.isChecked()
        if not self._guard & CHECKED_GUARD:
            self.declaration.checked = checked
            self.declaration.clicked(checked)

    def on_toggled(self, checked):
        """ The signal handler for the 'toggled' signal.

        """
        if not self._guard & CHECKED_GUARD:
            self.declaration.checked = checked
            self.declaration.toggled(checked)

    #--------------------------------------------------------------------------
    # ProxyAbstractButton API
    #--------------------------------------------------------------------------
    def set_text(self, text, sh_guard=True):
        """ Sets the widget's text with the provided value.

        """
        if sh_guard:
            with size_hint_guard(self):
                self.widget.setText(text)
        else:
            self.widget.setText(text)

    def set_icon(self, icon, sh_guard=True):
        """ Set the icon on the widget.

        """
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        if sh_guard:
            with size_hint_guard(self):
                self.widget.setIcon(qicon)
        else:
            self.widget.setIcon(qicon)

    def set_icon_size(self, size, sh_guard=True):
        """ Sets the widget's icon size.

        """
        if sh_guard:
            with size_hint_guard(self):
                self.widget.setIconSize(QSize(*size))
        else:
            self.widget.setIconSize(QSize(*size))

    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        self.widget.setCheckable(checkable)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        widget = self.widget
        # This handles the case where, by default, Qt will not allow
        # all of the radio buttons in a group to be disabled. By
        # temporarily turning off auto-exclusivity, we are able to
        # handle that case.
        self._guard |= CHECKED_GUARD
        try:
            if not checked and widget.isChecked() and widget.autoExclusive():
                widget.setAutoExclusive(False)
                widget.setChecked(checked)
                widget.setAutoExclusive(True)
            else:
                widget.setChecked(checked)
        finally:
            self._guard &= ~CHECKED_GUARD
