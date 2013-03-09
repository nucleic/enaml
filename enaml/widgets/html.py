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


class ProxyHtml(ProxyControl):
    """ The abstract definition of a proxy Html object.

    """
    #: A reference to the Html declaration.
    declaration = ForwardTyped(lambda: Html)

    def set_source(self, source):
        raise NotImplementedError


class Html(Control):
    """ An extremely simple widget for displaying HTML.

    """
    #: The Html source code to be rendered.
    source = d_(Unicode())

    #: An html control expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyHtml object
    proxy = Typed(ProxyHtml)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('source')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(Html, self)._update_proxy(change)
