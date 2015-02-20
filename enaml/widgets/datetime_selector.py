#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .bounded_datetime import BoundedDatetime, ProxyBoundedDatetime


class ProxyDatetimeSelector(ProxyBoundedDatetime):
    """ The abstract definition of a proxy DatetimeSelector object.

    """
    #: A reference to the DatetimeSelector declaration.
    declaration = ForwardTyped(lambda: DatetimeSelector)

    def set_datetime_format(self, format):
        raise NotImplementedError

    def set_calendar_popup(self, popup):
        raise NotImplementedError


class DatetimeSelector(BoundedDatetime):
    """ A widget to edit a Python datetime.datetime object.

    This is a geometrically smaller control than what is provided by
    Calendar.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = d_(Str())

    #: Whether to use a calendar popup for selecting the date.
    calendar_popup = d_(Bool(False))

    #: A datetime selector expands freely in width by default
    hug_width = set_default('ignore')

    #: A reference to the ProxyDateSelector object.
    proxy = Typed(ProxyDatetimeSelector)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('datetime_format', 'calendar_popup')
    def _update_proxy(self, change):
        """ An observer which updates the proxy with state change.

        """
        # The superclass implementation is sufficient.
        super(DatetimeSelector, self)._update_proxy(change)
