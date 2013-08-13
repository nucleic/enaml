#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import date as pydate

from atom.api import Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyBoundedDate(ProxyControl):
    """ The abstract defintion of a proxy BoundedDate object.

    """
    #: A reference to the BoundedDate declaration.
    declaration = ForwardTyped(lambda: BoundedDate)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_date(self, date):
        raise NotImplementedError


class BoundedDate(Control):
    """ A base class for components which edit a Python datetime.date
    object bounded between minimum and maximum values.

    This class is not meant to be used directly.

    """
    #: The minimum date available in the date edit. If the minimum value
    #: is changed such that it becomes greater than the current value or
    #: the maximum value, then those values will be adjusted. The default
    #: value is September 14, 1752.
    minimum = d_(Typed(pydate, args=(1752, 9, 14)))

    #: The maximum date available in the date edit. If the maximum value
    #: is changed such that it becomes smaller than the current value or
    #: the minimum value, then those values will be adjusted. The default
    #: value is December 31, 7999.
    maximum = d_(Typed(pydate, args=(7999, 12, 31)))

    #: The date in the control. This will be clipped to the supplied
    #: maximum and minimum values. The default is date.today().
    date = d_(Typed(pydate, factory=pydate.today))

    #: A reference to the ProxyBoundedDate object.
    proxy = Typed(ProxyBoundedDate)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('minimum', 'maximum', 'date')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(BoundedDate, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Post Setattr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum date.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.date:
            self.date = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum date.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.date:
            self.date = new

    #--------------------------------------------------------------------------
    # Post Validate Handlers
    #--------------------------------------------------------------------------
    def _post_validate_date(self, old, new):
        """ Post validate the date for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))
