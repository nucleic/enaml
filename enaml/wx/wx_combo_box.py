#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl


class WxComboBox(WxControl):
    """ A Wx implementation of an Enaml ComboBox.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.ComboBox widget.

        """
        return wx.ComboBox(parent, style=wx.CB_READONLY)

    def create(self, tree):
        """ Create and initialize the combo box control.

        """
        super(WxComboBox, self).create(tree)
        self.set_items(tree['items'])
        self.set_index(tree['index'])
        self.widget().Bind(wx.EVT_COMBOBOX, self.on_index_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_index(self, content):
        """ Handle the 'set_index' action from the Enaml widget.

        """
        self.set_index(content['index'])

    def on_action_set_items(self, content):
        """ Handle the 'set_items' action from the Enaml widget.

        """
        self.set_items(content['items'])

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self, event):
        """ The signal handler for the index changed signal.

        """
        content = {'index': self.widget().GetCurrentSelection()}
        self.send_action('index_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget()
        sel = widget.GetCurrentSelection()
        widget.SetItems(items)
        widget.SetSelection(sel)

    def set_index(self, index):
        """ Set the current index of the ComboBox

        """
        self.widget().SetSelection(index)

