#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl


ALIGN_MAP = {
    'left': wx.ALIGN_LEFT,
    'right': wx.ALIGN_RIGHT,
    'center': wx.ALIGN_CENTER,
    'justify': wx.ALIGN_LEFT, # wx doesn't support justification
}


ALIGN_MASK = wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER


class WxLabel(WxControl):
    """ A Wx implementation of an Enaml Label.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.StaticText widget.

        """
        return wx.StaticText(parent)

    def create(self, tree):
        """ Create and initialize the label control.

        """
        super(WxLabel, self).create(tree)
        self.set_text(tree['text'])
        self.set_align(tree['align'])
        self.set_vertical_align(tree['vertical_align'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        widget = self.widget()
        old_hint = widget.GetBestSize()
        self.set_text(content['text'])
        new_hint = widget.GetBestSize()
        if old_hint != new_hint:
            self.size_hint_updated()

    def on_action_set_align(self, content):
        """ Handle the 'set_align' action from the Enaml widget.

        """
        self.set_align(content['align'])
        self.widget().Refresh()

    def on_action_set_vertical_align(self, content):
        """ Handle the 'set_vertical_align' action from the Enaml widget.

        """
        self.set_vertical_align(content['vertical_align'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget().SetLabel(text)

    def set_align(self, align):
        """ Set the alignment of the text in the underlying widget.

        """
        widget = self.widget()
        style = widget.GetWindowStyle()
        style &= ~ALIGN_MASK
        style |= ALIGN_MAP[align]
        widget.SetWindowStyle(style)

    def set_vertical_align(self, align):
        """ Set the vertical alignment of the text in the underlying
        widget.

        """
        # Wx does not support vertical alignment.
        pass

