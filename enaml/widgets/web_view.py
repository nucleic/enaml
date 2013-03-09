#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyWebView(ProxyControl):
    """ The abstract definition of a proxy WebView object.

    """
    #: A reference to the WebView declaration.
    declaration = ForwardTyped(lambda: WebView)

    def set_url(self, url):
        raise NotImplementedError

    def set_html(self, html):
        raise NotImplementedError


class WebView(Control):
    """ A widget which displays a web page.

    Unlike the simpler `Html` widget, this widget supports the features
    of a full web browser.

    """
    #: The URL to load in the web view. This can be a path to a remote
    #: resource or a path to a file on the local filesystem. This value
    #: is mutually exclusive of `html`.
    url = d_(Unicode())

    #: The html to load into the web view. This value is mutually
    #: exclusive of `url`.
    html = d_(Unicode())

    #: The base url for loading content in statically supplied 'html'.
    base_url = d_(Unicode())

    #: A web view expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyWebView object.
    proxy = Typed(ProxyWebView)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('url', 'html'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(WebView, self)._update_proxy(change)
