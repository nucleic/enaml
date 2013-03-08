#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_abstract_button import WxAbstractButton


class WxPushButton(WxAbstractButton):
    """ A Wx implementation of the Enaml PushButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wx.Button control.

        """
        return wx.Button(parent)

    def create(self, tree):
        """ Create and initialize the PushButton control.

        """
        super(WxPushButton, self).create(tree)
        self.widget().Bind(wx.EVT_BUTTON, self.on_clicked)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        # XXX ignore this for now, wx has a completely separate control
        # wx.ToggleButton for handling this, that we'll need to swap
        # out dynamically.
        pass

    def get_checked(self):
        """ Returns the checked state of the widget.

        """
        return False

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        pass

