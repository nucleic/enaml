#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.label import ProxyLabel

from .wx_control import WxControl


ALIGN_MAP = {
    'left': wx.ALIGN_LEFT,
    'right': wx.ALIGN_RIGHT,
    'center': wx.ALIGN_CENTER,
    'justify': wx.ALIGN_LEFT,  # wx doesn't support justification
}


ALIGN_MASK = wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER


class WxLabel(WxControl, ProxyLabel):
    """ A Wx implementation of an Enaml ProxyLabel.

    """
     #: A reference to the widget created by the proxy.
    widget = Typed(wx.StaticText)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying label widget.

        """
        self.widget = wx.StaticText(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(WxLabel, self).init_widget()
        d = self.declaration
        self.set_text(d.text, guard=False)
        self.set_align(d.align)
        self.set_vertical_align(d.vertical_align)

    #--------------------------------------------------------------------------
    # ProxyLabel API
    #--------------------------------------------------------------------------
    def set_text(self, text, guard=True):
        """ Set the text in the underlying widget.

        """
        if guard:
            with self.geometry_guard():
                self.widget.SetLabel(text)
        else:
            self.widget.SetLabel(text)

    def set_align(self, align):
        """ Set the alignment of the text in the underlying widget.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~ALIGN_MASK
        style |= ALIGN_MAP[align]
        widget.SetWindowStyle(style)
        widget.Refresh()

    def set_vertical_align(self, align):
        """ Set the vertical alignment of the text in the widget.

        This is not supported on Wx.

        """
        pass
