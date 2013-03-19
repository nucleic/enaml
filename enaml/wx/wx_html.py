#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx.html

from atom.api import Typed

from enaml.widgets.html import ProxyHtml

from .wx_control import WxControl


class wxProperHtmlWindow(wx.html.HtmlWindow):
    """ A custom wx Html window that returns a non-braindead best size.

    """
    _best_size = wx.Size(256, 192)

    def GetBestSize(self):
        """ Returns the best size for the html window.

        """
        return self._best_size


class WxHtml(WxControl, ProxyHtml):
    """ A Wx implementation of the Enaml ProxyHtml widget.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxProperHtmlWindow)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        self.widget = wxProperHtmlWindow(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(WxHtml, self).init_widget()
        self.set_source(self.declaration.source)

    #--------------------------------------------------------------------------
    # ProxyHtml API
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.SetPage(source)
