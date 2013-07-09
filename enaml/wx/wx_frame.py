#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.frame import ProxyFrame

import wx

from .wx_constraints_widget import WxConstraintsWidget


class WxFrame(WxConstraintsWidget, ProxyFrame):
    """ A Wx implementation of an Enaml ProxyFrame.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(wx.Panel)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the QContainer widget.

        """
        self.widget = wx.Panel(self.parent_widget())

    #--------------------------------------------------------------------------
    # ProxyFrame API
    #--------------------------------------------------------------------------
    def set_border(self, border):
        """ Set the border for the widget.

        This is not supported on Wx.

        """
        pass
