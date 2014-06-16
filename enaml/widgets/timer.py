#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Event, Int, ForwardTyped, Typed, observe

from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyTimer(ProxyToolkitObject):
    """ The abstract definition of a proxy Timer object.

    """
    #: A reference to the Timer declaration.
    declaration = ForwardTyped(lambda: Timer)

    def set_interval(self, interval):
        raise NotImplementedError

    def set_single_shot(self, single_shot):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def is_running(self):
        raise NotImplementedError


class Timer(ToolkitObject):
    """ An object which represents a toolkit independent timer.

    """
    #: The interval of the timer, in milliseconds. The default is 0 and
    #: indicates that the timer will fire as soon as the event queue is
    #: emptied of all pending events.
    interval = d_(Int(0))

    #: Whether the timer fires only once, or repeatedly until stopped.
    single_shot = d_(Bool(False))

    #: An event fired when the timer times out.
    timeout = d_(Event(), writable=False)

    #: A reference to the ProxyTimer object.
    proxy = Typed(ProxyTimer)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('single_shot', 'interval')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the state changes.

        """
        # The superclass implementation is sufficient.
        super(Timer, self)._update_proxy(change)

    def start(self):
        """ Start or restart the timer.

        If the timer is already started, it will be stopped and
        restarted.

        """
        if self.proxy_is_active:
            self.proxy.start()

    def stop(self):
        """ Stop the timer.

        If the timer is already stopped, this is a no-op.

        """
        if self.proxy_is_active:
            self.proxy.stop()

    def is_active(self):
        """ Returns True if the timer is running, False otherwise.

        """
        if self.proxy_is_active:
            return self.proxy.is_running()
        return False
