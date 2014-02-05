#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Dict, observe

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyIPythonPrompt(ProxyControl):
    """ The abstract definition of a proxy IPythonWidget object.

    """
    #: A reference to the IPythonPrompt declaration.
    declaration = ForwardTyped(lambda: IPythonPrompt)

    def pull(self, identifier):
        raise NotImplementedError

    def set_context(self, context):
        raise NotImplementedError


class IPythonPrompt(Control):
    """ An embedded IPython prompt

    """
    #: The context namespace for the prompt
    context = d_(Dict())

    #: A reference to the ProxyIPythonPrompt object.
    proxy = Typed(ProxyIPythonPrompt)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('context')
    def _update_proxy(self, change):
        """ An observer which sends the state change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(IPythonPrompt, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def pull(self, identifier):
        """ Attempt to pull an identifier from the IPython context

        """
        if self.proxy_is_active:
            return self.proxy.pull(identifier)
        return None
