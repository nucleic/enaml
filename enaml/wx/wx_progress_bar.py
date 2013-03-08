#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl


class WxProgressBar(WxControl):
    """ A Wx implementation of an Enaml ProgressBar.

    """
    #: The minimum value of the progress bar
    _minimum = 0

    #: The maximum value of the progress bar
    _maximum = 100

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Gauge widget.

        """
        return wx.Gauge(parent)

    def create(self, tree):
        """ Create and initialize the progress bar control.

        """
        super(WxProgressBar, self).create(tree)
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
        self._minimum = value
        self.widget().SetRange(self._maximum - value)

    def set_maximum(self, value):
        """ Set the maximum value of the progress bar

        """
        self._maximum = value
        self.widget().SetRange(value - self._minimum)

    def set_value(self, value):
        """ Set the value of the progress bar

        """
        self.widget().SetValue(value - self._minimum)

