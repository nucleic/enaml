#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, set_default

from enaml.core.declarative import d_func

from .control import Control, ProxyControl


class ProxyIPythonConsole(ProxyControl):
    """ The abstract defintion of a proxy IPythonConsole object.

    """
    #: A reference to the IPythonConsole declaration.
    declaration = ForwardTyped(lambda: IPythonConsole)

    def update_namespace(self, ns):
        raise NotImplementedError

    def snap_namespace(self):
        raise NotImplementedError


class IPythonConsole(Control):
    """ A widget which hosts an embedded IPython console.

    """
    #: The ipython console expands freely by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyIPythonConsole object.
    proxy = Typed(ProxyIPythonConsole)

    @d_func
    def initial_namespace(self):
        """ Compute and return the initial console namespace.

        This method is invoked during startup to retrieve the initial
        variables to add to the console. The default implementation
        returns an empty dictionary.

        Returns
        -------
        result : dict
            A dictionary of local variables to add to the console.

        """
        return {}

    def update_namespace(self, **ns):
        """ Inject variables into the console namespace.

        Parameters
        ----------
        **ns
            The variables to inject into the namespace.

        """
        if self.proxy_is_active:
            self.proxy.update_namespace(ns)

    def snap_namespace(self):
        """ Snap a copy of the current console namespace.

        Returns
        -------
        result : dict
            A copy of the current console namespace.

        """
        if self.proxy_is_active:
            return self.proxy.snap_namespace()
        return {}

    @d_func
    def exit_requested(self):
        """ A method invoked when user attemps to exit the console.

        This will be called when the user invokes a console command
        which would otherwise close the terminal. User code should
        reimplement this method to take appropriate action. By
        default, the request is ignored.

        """
        pass
