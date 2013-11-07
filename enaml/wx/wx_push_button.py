#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.push_button import ProxyPushButton

from .wx_abstract_button import WxAbstractButton


class WxPushButton(WxAbstractButton, ProxyPushButton):
    """ A Wx implementation of the Enaml ProxyPushButton.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wx.Button)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wxButton widget.

        """
        self.widget = wx.Button(self.parent_widget())

    def init_widget(self):
        """ Handle layout initialization for the push button.

        """
        super(WxPushButton, self).init_widget()
        self.widget.Bind(wx.EVT_BUTTON, self.on_clicked)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        This is not supported on Wx.

        """
        pass

    def get_checked(self):
        """ Returns the checked state of the widget.

        """
        return False

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        pass

    #--------------------------------------------------------------------------
    # ProxyPushButton API
    #--------------------------------------------------------------------------
    def set_default(self, default):
        """ This is not supported on Wx.

        """
        pass
