#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.ipython_console import ProxyIPythonConsole

from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager

from .QtGui import QFrame, QVBoxLayout
from .QtCore import Qt

from .qt_control import QtControl


class QtIPythonConsole(QtControl, ProxyIPythonConsole):
    """ A Qt4 implementation of an Enaml IPythonConsole.

    """
    #: The wrapper widget created by the proxy.
    widget = Typed(QFrame)

    #: The internal IPython console widget.
    ipy_widget = Typed(RichIPythonWidget)

    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QFrame(self.parent_widget())
        self.ipy_widget = RichIPythonWidget()

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtIPythonConsole, self).init_widget()
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        ipy_widget = self.ipy_widget
        ipy_widget.kernel_manager = kernel_manager
        ipy_widget.kernel_client = kernel_client
        control = ipy_widget._control
        control._d_proxy = self
        widget = self.widget
        widget.setFocusPolicy(Qt.StrongFocus)
        widget.setFocusProxy(control)

    def init_layout(self):
        """ Initialize the underlying widget layout.

        """
        super(QtIPythonConsole, self).init_layout()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.ipy_widget)
        self.widget.setLayout(layout)

    def destroy(self):
        """ Destroy the underlying widget.

        """
        ipy_widget = self.ipy_widget
        ipy_widget.kernel_client.stop_channels()
        ipy_widget.kernel_manager.shutdown_kernel()
        ipy_widget._control._d_proxy = None
        super(QtIPythonConsole, self).destroy()
