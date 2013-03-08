#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QProgressBar
from .qt_control import QtControl


class QtProgressBar(QtControl):
    """ A Qt implementation of an Enaml ProgressBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying progress bar widget.

        """
        widget = QProgressBar(parent)
        widget.setTextVisible(False)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtProgressBar, self).create(tree)
        self.set_minimum(tree['minimum'])
        self.set_maximum(tree['maximum'])
        self.set_value(tree['value'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_minimum(self, value):
        """ Set the minimum value of the progress bar

        """
        self.widget().setMinimum(value)

    def set_maximum(self, value):
        """ Set the maximum value of the progress bar

        """
        self.widget().setMaximum(value)

    def set_value(self, value):
        """ Set the value of the progress bar

        """
        self.widget().setValue(value)

