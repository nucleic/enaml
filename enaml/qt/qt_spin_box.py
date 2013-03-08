#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QSpinBox
from .qt_control import QtControl


class QtSpinBox(QtControl):
    """ A Qt implementation of an Enaml SpinBox.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QSpinBox widget.

        """
        widget = QSpinBox(parent)
        widget.setKeyboardTracking(False)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtSpinBox, self).create(tree)
        self.set_maximum(tree['maximum'])
        self.set_minimum(tree['minimum'])
        self.set_value(tree['value'])
        self.set_prefix(tree['prefix'])
        self.set_suffix(tree['suffix'])
        self.set_special_value_text(tree['special_value_text'])
        self.set_single_step(tree['single_step'])
        self.set_read_only(tree['read_only'])
        self.set_wrapping(tree['wrapping'])
        self.widget().valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Signal Handler
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ The signal handler for the 'valueChanged' signal.

        """
        # Guard against loopback recursion since Qt will emit the
        # valueChanged signal when programatically setting the value.
        if 'value' not in self.loopback_guard:
            content = {'value': self.widget().value()}
            self.send_action('value_changed', content)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_maximum(self, content):
        """ Handler for the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_minimum(self, content):
        """ Handler for the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_value(self, content):
        """ Handler for the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

    def on_action_set_prefix(self, content):
        """ Handler for the 'set_prefix' action from the Enaml widget.

        """
        self.set_prefix(content['prefix'])

    def on_action_set_suffix(self, content):
        """ Handler for the 'set_suffix' action from the Enaml widget.

        """
        self.set_suffix(content['suffix'])

    def on_action_set_special_value_text(self, content):
        """ Handler for the 'set_special_value_text' action from the
        Enaml widget.

        """
        self.set_special_value_text(content['special_value_text'])

    def on_action_set_single_step(self, content):
        """ Handler for the 'set_single_step' action from the Enaml
        widget.

        """
        self.set_single_step(content['single_step'])

    def on_action_set_read_only(self, content):
        """ Handler for the 'set_read_only' action from the Enaml
        widget.

        """
        self.set_read_only(content['read_only'])

    def on_action_set_wrapping(self, content):
        """ Handler for the 'set_wrapping' action from the Enaml
        widget.

        """
        self.set_wrapping(content['wrapping'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_maximum(self, maximum):
        """ Set the widget's maximum value.

        """
        self.widget().setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the widget's minimum value.

        """
        self.widget().setMinimum(minimum)

    def set_value(self, value):
        """ Set the spin box's value.

        """
        # The setValue will emit a changed signal. Since this will only
        # be called as a result of an Enaml action, we guard against
        # the loopback
        with self.loopback_guard('value'):
            self.widget().setValue(value)

    def set_prefix(self, prefix):
        """ Set the prefix for the spin box.

        """
        self.widget().setPrefix(prefix)

    def set_suffix(self, suffix):
        """ Set the suffix for the spin box.

        """
        self.widget().setSuffix(suffix)

    def set_special_value_text(self, text):
        """ Set the special value text for the spin box.

        """
        self.widget().setSpecialValueText(text)

    def set_single_step(self, step):
        """ Set the widget's single step value.

        """
        self.widget().setSingleStep(step)

    def set_read_only(self, read_only):
        """ Set the widget's read only flag.

        """
        self.widget().setReadOnly(read_only)

    def set_wrapping(self, wrapping):
        """ Set the widget's wrapping flag.

        """
        self.widget().setWrapping(wrapping)

