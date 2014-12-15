#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .bounded_date import BoundedDate, ProxyBoundedDate


class ProxyDateSelector(ProxyBoundedDate):
    """ The abstract definition of a proxy DateSelector object.

    """
    #: A reference to the DateSelector declaration.
    declaration = ForwardTyped(lambda: DateSelector)

    def set_date_format(self, format):
        raise NotImplementedError

    def set_calendar_popup(self, popup):
        raise NotImplementedError


class DateSelector(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateSelector displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control
    than what is provided by Calendar.

    """
    #: A python date format string to format the date for display. If
    #: If none is supplied (or is invalid) the system locale setting
    #: is used. This may not be supported by all backends.
    date_format = d_(Str())

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = d_(Bool(False))

    #: A date selector expands freely in width by default.
    hug_width = set_default('ignore')

    #: A reference to the ProxyDateSelector object.
    proxy = Typed(ProxyDateSelector)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('date_format', 'calendar_popup')
    def _update_proxy(self, change):
        """ An observer which updates the proxy with state change.

        """
        # The superclass implementation is sufficient.
        super(DateSelector, self)._update_proxy(change)
