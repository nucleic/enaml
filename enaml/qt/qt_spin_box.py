#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.spin_box import ProxySpinBox

from .QtWidgets import QSpinBox

from .qt_control import QtControl


#: Cyclic guard flag
VALUE_FLAG = 0x1


class QtSpinBox(QtControl, ProxySpinBox):
    """ A Qt implementation of an Enaml SpinBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QSpinBox)

    #: Cyclic guard flags
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QSpinBox widget.

        """
        widget = QSpinBox(self.parent_widget())
        widget.setKeyboardTracking(False)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtSpinBox, self).init_widget()
        d = self.declaration
        self.set_maximum(d.maximum)
        self.set_minimum(d.minimum)
        self.set_value(d.value)
        self.set_prefix(d.prefix)
        self.set_suffix(d.suffix)
        self.set_special_value_text(d.special_value_text)
        self.set_single_step(d.single_step)
        self.set_read_only(d.read_only)
        self.set_wrapping(d.wrapping)
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ The signal handler for the 'valueChanged' signal.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.declaration.value = self.widget.value()
            finally:
                self._guard &= ~VALUE_FLAG

    #--------------------------------------------------------------------------
    # ProxySpinBox API
    #--------------------------------------------------------------------------
    def set_maximum(self, maximum):
        """ Set the widget's maximum value.

        """
        self.widget.setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the widget's minimum value.

        """
        self.widget.setMinimum(minimum)

    def set_value(self, value):
        """ Set the spin box's value.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.widget.setValue(value)
            finally:
                self._guard &= ~VALUE_FLAG

    def set_prefix(self, prefix):
        """ Set the prefix for the spin box.

        """
        self.widget.setPrefix(prefix)

    def set_suffix(self, suffix):
        """ Set the suffix for the spin box.

        """
        self.widget.setSuffix(suffix)

    def set_special_value_text(self, text):
        """ Set the special value text for the spin box.

        """
        self.widget.setSpecialValueText(text)

    def set_single_step(self, step):
        """ Set the widget's single step value.

        """
        self.widget.setSingleStep(step)

    def set_read_only(self, read_only):
        """ Set the widget's read only flag.

        """
        self.widget.setReadOnly(read_only)

    def set_wrapping(self, wrapping):
        """ Set the widget's wrapping flag.

        """
        self.widget.setWrapping(wrapping)
