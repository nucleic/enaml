#------------------------------------------------------------------------------
# Copyright (c) 2014-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed
from future.utils import raise_from

from enaml.widgets.ipython_console import ProxyIPythonConsole

try:
    #: IPython >= 4.0
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess import QtInProcessKernelManager
except ImportError as e:
    try:
        from IPython.qt.console.rich_ipython_widget\
            import RichIPythonWidget as RichJupyterWidget
        from IPython.qt.inprocess import QtInProcessKernelManager
    except ImportError as e2:
        msg = ('qtconsole is required to use the IPythonConsole with '
               'IPython>=4.0.\nLoading qtconsole failed with: {}\nLoading '
               'from IPython < 4.0 failed with: {}')
        raise ImportError(msg.format(e, e2))

from .QtWidgets import QFrame, QVBoxLayout

from . import focus_registry
from .q_deferred_caller import deferredCall
from .qt_control import QtControl


class QtIPythonConsole(QtControl, ProxyIPythonConsole):
    """ A Qt4 implementation of an Enaml IPythonConsole.

    """
    #: The wrapper widget created by the proxy. A wrapper is necessary
    #: since the IPython widget overrides critical Qt API methods which
    #: renders the widget incompatible with the ancestor hierarchy.
    widget = Typed(QFrame)

    #: The internal IPython console widget.
    ipy_widget = Typed(RichJupyterWidget)

    #--------------------------------------------------------------------------
    # Lifecycle API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QFrame(self.parent_widget())
        self.ipy_widget = RichJupyterWidget()
        assert self.page_control is not None  # always use paging

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtIPythonConsole, self).init_widget()
        self._setup_kernel()
        focus_registry.register(self.text_control, self)
        focus_registry.register(self.page_control, self)
        self.update_ns(self.declaration.initial_ns)
        self.ipy_widget.exit_requested.connect(self._on_exit_requested)

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
        self._teardown_kernel()
        focus_registry.unregister(self.text_control)
        focus_registry.unregister(self.page_control)
        super(QtIPythonConsole, self).destroy()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _setup_kernel(self):
        """ Setup the kernel for the widget.

        """
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel(show_banner=False)

        kernel = kernel_manager.kernel
        kernel.gui = 'qt'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        ipy_widget = self.ipy_widget
        ipy_widget.kernel_manager = kernel_manager
        ipy_widget.kernel_client = kernel_client

    def _teardown_kernel(self):
        """ Teardown the kernel for the widget.

        """
        ipy_widget = self.ipy_widget
        ipy_widget.kernel_client.stop_channels()
        ipy_widget.kernel_manager.shutdown_kernel()

    def _on_exit_requested(self, obj):
        """ Handle the 'exit_requested' signal on the widget.

        """
        deferredCall(self.declaration.exit_requested)

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def focus_target(self):
        """ Returns the current focus target for the widget.

        """
        page = self.page_control
        if page.isVisibleTo(self.widget):
            return page
        return self.text_control

    def hook_focus_events(self):
        """ Hook the focus events for the underlyling widget.

        """
        text = self.text_control
        text.focusInEvent = self.textFocusInEvent
        text.focusOutEvent = self.textFocusOutEvent
        page = self.page_control
        page.focusInEvent = self.pageFocusInEvent
        page.focusOutEvent = self.pageFocusOutEvent

    def unhook_focus_events(self):
        """ Unhook the focus events for the underling widget.

        """
        text = self.text_control
        del text.focusInEvent
        del text.focusOutEvent
        page = self.page_control
        del page.focusInEvent
        del page.focusOutEvent

    def textFocusInEvent(self, event):
        """ Handle the focusInEvent for the text widget.

        """
        self.handleFocusInEvent(self.text_control, event)

    def textFocusOutEvent(self, event):
        """ Handle the focusOutEvent for the text widget.

        """
        self.handleFocusOutEvent(self.text_control, event)

    def pageFocusInEvent(self, event):
        """ Handle the focusInEvent for the page widget.

        """
        self.handleFocusInEvent(self.page_control, event)

    def pageFocusOutEvent(self, event):
        """ Handle the focusOutEvent for the page widget.

        """
        self.handleFocusOutEvent(self.page_control, event)

    def handleFocusInEvent(self, widget, event):
        """ Handle the focusInEvent for the given widget.

        """
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def handleFocusOutEvent(self, widget, event):
        """ Handle the focusOutEvent for the given widget.

        """
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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

    #--------------------------------------------------------------------------
    # ProxyIPythonConsole API
    #--------------------------------------------------------------------------
    def get_var(self, name, default):
        """ Get a variable from the console namespace.

        """
        kernel = self.ipy_widget.kernel_manager.kernel
        return kernel.shell.user_ns.get(name, default)

    def update_ns(self, ns):
        """ Update the namespace of the underlying console.

        """
        if len(ns) > 0:
            kernel = self.ipy_widget.kernel_manager.kernel
            kernel.shell.push(ns)
