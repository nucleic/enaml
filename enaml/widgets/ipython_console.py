#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Dict, Event, Typed, ForwardTyped, set_default

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyIPythonConsole(ProxyControl):
    """ The abstract definition of a proxy IPythonConsole object.

    """
    #: A reference to the IPythonConsole declaration.
    declaration = ForwardTyped(lambda: IPythonConsole)

    def get_var(self, name, default):
        raise NotImplementedError

    def update_ns(self, ns):
        raise NotImplementedError


class IPythonConsole(Control):
    """ A widget which hosts an embedded IPython console.

    """
    #: The initial namespace to apply to the console. Runtime changes
    #: to this value will be ignored. Use 'update_ns' to add variables
    #: to the console at runtime.
    initial_ns = d_(Dict())

    #: An event fired when the user invokes a console exit command.
    exit_requested = d_(Event(), writable=False)

    #: The ipython console expands freely by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyIPythonConsole object.
    proxy = Typed(ProxyIPythonConsole)

    def get_var(self, name, default=None):
        """ Get a variable from the console namespace.

        Parameters
        ----------
        name : basestring
            The name of the variable to retrieve.

        default : object, optional
            The value to return if the variable does not exist. The
            default is None.

        Returns
        -------
        result : object
            The variable in the namespace, or the provided default.

        """
        if self.proxy_is_active:
            return self.proxy.get_var(name, default)
        return default

    def update_ns(self, **kwargs):
        """ Update the variables in the console namespace.

        Parameters
        ----------
        **kwargs
            The variables to update in the console namespace.

        """
        if self.proxy_is_active:
            self.proxy.update_ns(kwargs)
