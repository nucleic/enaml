#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Int, Typed

from enaml.widgets.combo_box import ProxyComboBox

from .wx_control import WxControl


# cyclic notification guard flags
INDEX_GUARD = 0x1


class WxComboBox(WxControl, ProxyComboBox):
    """ A Wx implementation of an Enaml ProxyComboBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wx.ComboBox)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QComboBox widget.

        """
        self.widget = wx.ComboBox(self.parent_widget(), style=wx.CB_READONLY)

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(WxComboBox, self).init_widget()
        d = self.declaration
        self.set_items(d.items)
        self.set_index(d.index)
        self.set_editable(d.editable)
        self.widget.Bind(wx.EVT_COMBOBOX, self.on_index_changed)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self, event):
        """ The signal handler for the index changed signal.

        """
        if not self._guard & INDEX_GUARD:
            self.declaration.index = self.widget.GetCurrentSelection()

    #--------------------------------------------------------------------------
    # ProxyComboBox API
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget
        sel = widget.GetCurrentSelection()
        widget.SetItems(items)
        widget.SetSelection(sel)

    def set_index(self, index):
        """ Set the current index of the ComboBox

        """
        self._guard |= INDEX_GUARD
        try:
            self.widget.SetSelection(index)
        finally:
            self._guard &= ~INDEX_GUARD

    def set_editable(self, editable):
        """ Set whether the combo box is editable.

        This is not supported on wx.

        """
        pass
