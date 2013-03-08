#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import datetime as pydatetime

from atom.api import Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyBoundedDatetime(ProxyControl):
    """ The abstract defintion of a proxy BoundedDate object.

    """
    #: A reference to the BoundedDatetime declaration.
    declaration = ForwardTyped(lambda: BoundedDatetime)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_datetime(self, datetime):
        raise NotImplementedError


class BoundedDatetime(Control):
    """ A base class for use with widgets that edit a Python
    datetime.datetime object bounded between minimum and maximum
    values. This class is not meant to be used directly.

    """
    #: The minimum datetime available in the datetime edit. If not
    #: defined then the default value is midnight September 14, 1752.
    minimum = d_(Typed(pydatetime, args=(1752, 9, 14, 0, 0, 0, 0)))

    #: The maximum datetime available in the datetime edit. If not
    #: defined then the default value is the second before midnight
    #: December 31, 7999.
    maximum = d_(Typed(pydatetime, args=(7999, 12, 31, 23, 59, 59, 999000)))

    #: The currently selected date. Default is datetime.now(). The
    #: value is bounded between :attr:`minimum` and :attr:`maximum`.
    datetime = d_(Typed(pydatetime, factory=pydatetime.now))

    #: A reference to the ProxyBoundedDatetime object.
    proxy = Typed(ProxyBoundedDatetime)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('minimum', 'maximum', 'datetime'))
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(BoundedDatetime, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Post Setattr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum datetime.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.datetime:
            self.datetime = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum datetime.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.datetime:
            self.datetime = new

    #--------------------------------------------------------------------------
    # Post Validate Handlers
    #--------------------------------------------------------------------------
    def _post_validate_datetime(self, old, new):
        """ Post validate the datetime for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))
