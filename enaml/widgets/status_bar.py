#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Bool, observe

from enaml.core.declarative import d_

from .status_item import StatusItem
from .widget import Widget, ProxyWidget


class ProxyStatusBar(ProxyWidget):
    """ The abstract definition of a proxy StatusBar object.

    """
    #: A reference to the StatusBar declaration.
    declaration = ForwardTyped(lambda: StatusBar)

    def set_size_grip_enabled(self, enabled):
        raise NotImplementedError

    def show_message(self, message, timeout=0):
        raise NotImplementedError

    def clear_message(self):
        raise NotImplementedError


class StatusBar(Widget):
    """ A widget used as a status bar in a MainWindow.

    A status bar can be used to display temporary messages or display
    persistent widgets by declaring StatusItem children.

    """
    #: Whether or not the size grip in the right corner is enabled.
    size_grip_enabled = d_(Bool(True))

    #: A reference to the ProxyStatusBar object.
    proxy = Typed(ProxyStatusBar)

    def status_items(self):
        """ Get the list of status items defined on the status bar.

        """
        return [c for c in self.children if isinstance(c, StatusItem)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('size_grip_enabled')
    def _update_proxy(self, change):
        """ Update the proxy when the status bar data changes.

        """
        # The superclass implementation is sufficient.
        super(StatusBar, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def show_message(self, message, timeout=0):
        """ Show a temporary message in the status bar.

        Parameters
        ----------
        message : unicode
            The message to show in the status bar.

        timeout : int, optional
            The number of milliseconds to show the message. The default
            is 0, which will show the message until a new message is
            shown or 'clear_message()' is called.

        """
        if self.proxy_is_active:
            self.proxy.show_message(message, timeout)

    def clear_message(self):
        """ Clear any temporary message displayed in the status bar.

        """
        if self.proxy_is_active:
            self.proxy.clear_message()
