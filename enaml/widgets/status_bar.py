#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Bool, observe

from enaml.core.declarative import d_

from .widget import Widget, ProxyWidget


class ProxyStatusBar(ProxyWidget):
    """ The abstract definition of a proxy StatusBar object

    """
    # A reference to the StatusBar declaration
    declaration = ForwardTyped(lambda: StatusBar)

    def show_message(self, message, timeout=0):
        raise NotImplementedError

    def clear_message(self):
        raise NotImplementedError



class StatusBar(Widget):
    """ A widget used as a status bar in a MainWindow.

    """

    #: Should the size grip in the bottom right corner be shown
    grip_enabled = d_(Bool(True))

    #: A reference to the ProxyStatusBar
    proxy = Typed(ProxyStatusBar)

    def items(self):
        """ Get the items defined on the status bar

        """
        isinst = isinstance
        allowed = (PermanentStatusWidgets, TransientStatusWidgets)
        return tuple(c for c in self.children if isinst(c, allowed))

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('grip_enabled'))
    def _update_proxy(self, change):
        """ Update the ProxyStatusBar when the StatusBar data
        changes

        """
        super(StatusBar, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def show_message(self, message, timeout=0):
        """ Send the 'show_message' action to the client widget.

        Parameters
        ----------
            message : str
                The message to show in the status bar

            timeout : int
                The number of milliseconds to show the message. Defaults
                to 0, which will show the message until a new message is shown
                or the clear_message message is sent

        """
        if self.proxy_is_active:
            self.proxy.show_message(message, timeout)

    def clear_message(self):
        """ Send the 'clear_message' action to the client widget.

        """
        if self.proxy_is_active:
            self.proxy.clear_message()
