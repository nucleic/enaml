#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.web_view import ProxyWebView

from .QtCore import QUrl
from .QtWebKit import QWebView

from .qt_control import QtControl


class QtWebView(QtControl, ProxyWebView):
    """ A Qt implementation of an Enaml ProxyWebView.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QWebView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QWebView control.

        """
        self.widget = QWebView(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying control.

        """
        super(QtWebView, self).init_widget()
        d = self.declaration
        if d.html:
            self.set_html(d.html)
        elif d.url:
            self.set_url(d.url)

    #--------------------------------------------------------------------------
    # ProxyWebView API
    #--------------------------------------------------------------------------
    def set_url(self, url):
        """ Set the url for the underlying control.

        """
        self.widget.setUrl(QUrl(url))

    def set_html(self, html):
        """ Set the html source for the underlying control.

        """
        self.widget.setHtml(html, QUrl(self.declaration.base_url))
