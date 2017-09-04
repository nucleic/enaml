#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .control import Control, ProxyControl


class ProxyRawWidget(ProxyControl):
    """ The abstract definition of a proxy RawWidget object.

    """
    #: A reference to the RawWidget declaration.
    declaration = ForwardTyped(lambda: RawWidget)

    def get_widget(self):
        raise NotImplementedError


class RawWidget(Control):
    """ A raw toolkit-specific control.

    Use this widget when the toolkit backend for the application is
    known ahead of time, and Enaml does provide an implementation of
    the required widget. This can be used as a hook to inject custom
    widgets into an Enaml widget hierarchy.
    
    Notes
    -----
    When using the Qt backend, note that PySide requires weakrefs for using 
    bound methods as slots. PyQt doesn't, but executes unsafe code if not using
    weakrefs. So you should add the following line to your class.
    __slots__ = '__weakref__'

    """
    #: A reference to the proxy Control object.
    proxy = Typed(ProxyRawWidget)

    def create_widget(self, parent):
        """ Create the toolkit widget for the control.

        This method should create and initialize the widget.

        Parameters
        ----------
        parent : toolkit widget or None
            The parent toolkit widget for the control.

        Returns
        -------
        result : toolkit widget
            The toolkit specific widget for the control.

        """
        raise NotImplementedError

    def get_widget(self):
        """ Retrieve the toolkit widget for the control.

        Returns
        -------
        result : toolkit widget or None
            The toolkit widget that was previously created by the
            call to 'create_widget' or None if the proxy is not
            active or the widget has been destroyed.

        """
        if self.proxy_is_active:
            return self.proxy.get_widget()
