#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.progress_bar import ProxyProgressBar

from .wx_control import WxControl


class WxProgressBar(WxControl, ProxyProgressBar):
    """ A Wx implementation of an Enaml ProxyProgressBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wx.Gauge)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wx.Gauge widget.

        """
        self.widget = wx.Gauge(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the progress bar control.

        """
        super(WxProgressBar, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_value(d.value)
        self.set_text_visible(d.text_visible)

    #--------------------------------------------------------------------------
    # ProxyProgressBar API
    #--------------------------------------------------------------------------
    def set_minimum(self, value):
        """ Set the minimum value of the progress bar

        """
        d = self.declaration
        self.widget.SetRange(d.maximum - value)

    def set_maximum(self, value):
        """ Set the maximum value of the progress bar

        """
        d = self.declaration
        self.widget.SetRange(value - d.minimum)

    def set_value(self, value):
        """ Set the value of the progress bar

        """
        d = self.declaration
        self.widget.SetValue(value - d.minimum)

    def set_text_visible(self, visible):
        """ Set the text visibility on the widget.

        This is not implemented on Wx.

        """
        pass
