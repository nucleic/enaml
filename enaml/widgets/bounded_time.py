#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import datetime, time as pytime

from atom.api import Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyBoundedTime(ProxyControl):
    """ The abstract defintion of a proxy BoundedTime object.

    """
    #: A reference to the BoundedTime declaration.
    declaration = ForwardTyped(lambda: BoundedTime)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_time(self, time):
        raise NotImplementedError


class BoundedTime(Control):
    """ A base class for use with widgets that edit a Python
    datetime.time object bounded between minimum and maximum
    values. This class is not meant to be used directly.

    """
    #: The minimum time available in the datetime edit. The default value
    #: is midnight.
    minimum = d_(Typed(pytime, args=(0, 0, 0)))

    #: The maximum time available in the datetime edit. The default is
    #: one second before midnight.
    maximum = d_(Typed(pytime, args=(23, 59, 59, 999000)))

    #: The currently selected time. Default is datetime.now().time().
    #: The value is clipped between :attr:`minimum` and :attr:`maximum`.
    time = d_(Typed(pytime, factory=lambda: datetime.now().time()))

    #: A reference to the ProxyBoundedTime object.
    proxy = Typed(ProxyBoundedTime)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('minimum', 'maximum', 'time'))
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(BoundedTime, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Post Setattr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum time.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.time:
            self.time = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum time.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.time:
            self.time = new

    #--------------------------------------------------------------------------
    # Post Validate Handlers
    #--------------------------------------------------------------------------
    def _post_validate_time(self, old, new):
        """ Post validate the time for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))
