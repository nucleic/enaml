#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx.html

from .wx_control import WxControl


class wxProperHtmlWindow(wx.html.HtmlWindow):
    """ A custom wx Html window that returns a non-braindead best size.

    """
    _best_size = wx.Size(256, 192)

    def GetBestSize(self):
        """ Returns the best size for the html window.

        """
        return self._best_size


class WxHtml(WxControl):
    """ A Wx implementation of the Enaml Html widget.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying html widget.

        """
        return wxProperHtmlWindow(parent)

    def create(self, tree):
        """ Create and initialize the html control.

        """
        super(WxHtml, self).create(tree)
        self.set_source(tree['source'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_source(self, content):
        """ Handle the 'set_source' action from the Enaml widget.

        """
        self.set_source(content['source'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget().SetPage(source)

