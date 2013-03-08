#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import QUrl
from .qt.QtWebKit import QWebView
from .qt_control import QtControl


class QtWebView(QtControl):
    """ A Qt implementation of an Enaml WebView.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying QWebView control.

        """
        return QWebView(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtWebView, self).create(tree)
        html = tree['html']
        if html:
            self.set_html(html)
        else:
            self.set_url(tree['url'])

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_url(self, content):
        """ Handle the 'set_url' action from the Enaml widget.

        """
        self.set_url(content['url'])

    def on_action_set_html(self, content):
        """ Handle the 'set_html' action from the Enaml widget.

        """
        self.set_html(content['html'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_url(self, url):
        """ Set the url for the underlying control.

        """
        self.widget().setUrl(QUrl(url))

    def set_html(self, html):
        """ Set the html source for the underlying control.

        """
        self.widget().setHtml(html, 'c:/')

