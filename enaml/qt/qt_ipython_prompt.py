#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.ipython_prompt import ProxyIPythonPrompt

from IPython.frontend.qt.console.ipython_widget import IPythonWidget
from IPython.frontend.qt.inprocess import QtInProcessKernelManager

from .qt_control import QtControl


class QtIPythonPrompt(QtControl, ProxyIPythonPrompt):
    """ A Qt implementation of an Enaml ProxyIPythonPrompt.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(IPythonWidget)

    #: The widget's kernel manager instance
    _kernel_manager = Typed(QtInProcessKernelManager)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying label widget.

        """
        self.widget = IPythonWidget(parent=self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtIPythonPrompt, self).init_widget()

        self._kernel_manager = QtInProcessKernelManager()
        self._kernel_manager.start_kernel()

        client = self._kernel_manager.client()
        client.start_channels()

        self.widget.kernel_manager = self._kernel_manager
        self.widget.kernel_client = client

        d = self.declaration
        self.set_context(d.context)

    #--------------------------------------------------------------------------
    # ProxyIPythonPrompt API
    #--------------------------------------------------------------------------
    def pull(self, identifier):
        """ Pull an identifier from the IPython namespace

        """
        namespace = self._kernel_manager.kernel.shell.user_ns
        return namespace.get(identifier, None)

    def set_context(self, context):
        """ Set the context for the IPython shell

        """
        self._kernel_manager.kernel.shell.push(context)
