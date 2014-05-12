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

from . import focus_registry
from .qt_control import QtControl


class QtIPythonConsole(QtControl, ProxyIPythonConsole):
    """ A Qt4 implementation of an Enaml IPythonConsole.

    """
    #: The wrapper widget created by the proxy. A wrapper is necessary
    #: since the IPython widget overrides critical Qt API methods which
    #: renders the widget incompatible with the ancestor hierarchy.
    widget = Typed(QFrame)

    #: The internal IPython console widget.
    ipy_widget = Typed(RichIPythonWidget)

    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QFrame(self.parent_widget())
        self.ipy_widget = RichIPythonWidget()
        assert self.page_control is not None  # always use paging

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtIPythonConsole, self).init_widget()
        self.setup_kernel()
        focus_registry.register(self.text_control, self)
        focus_registry.register(self.page_control, self)

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
        self.teardown_kernel()
        focus_registry.unregister(self.text_control)
        focus_registry.unregister(self.page_control)
        super(QtIPythonConsole, self).destroy()

    def setup_kernel(self):
        """ Setup the kernel for the widget.

        """
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        ipy_widget = self.ipy_widget
        ipy_widget.kernel_manager = kernel_manager
        ipy_widget.kernel_client = kernel_client

    def teardown_kernel(self):
        """ Teardown the kernel for the widget.

        """
        ipy_widget = self.ipy_widget
        ipy_widget.kernel_client.stop_channels()
        ipy_widget.kernel_manager.shutdown_kernel()

    @property
    def text_control(self):
        """ Return the text control for the IPython widget.

        Returns
        -------
        result : QTextEdit
            The text control for the IPython widget.

        """
        return self.ipy_widget._control

    @property
    def page_control(self):
        """ Return the page control for the IPython widget.

        Returns
        -------
        result : QTextEdit
            The page control for the IPython widget.

        """
        return self.ipy_widget._page_control

    def focus_target(self):
        """ Returns the current focus target for the widget.

        """
        page = self.page_control
        if page.isVisibleTo(self.widget):
            return page
        return self.text_control
