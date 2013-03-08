#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, observe, set_default

from enaml.core.declarative import d_

from .control import Control


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

    #: A web view expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create the snapshot for the widget.

        """
        snap = super(WebView, self).snapshot()
        snap['url'] = self.url
        snap['html'] = self.html
        return snap

    @observe(r'^(url|html)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(WebView, self).send_member_change(change)

