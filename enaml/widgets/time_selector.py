#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .bounded_time import BoundedTime, ProxyBoundedTime


class ProxyTimeSelector(ProxyBoundedTime):
    """ The abstract definition of a proxy TimeSelector object.

    """
    #: A reference to the TimeSelector declaration.
    declaration = ForwardTyped(lambda: TimeSelector)

    def set_time_format(self, format):
        raise NotImplementedError


class TimeSelector(BoundedTime):
    """ A time widget that displays a Python datetime.time object using
    an appropriate toolkit specific control.

    """
    #: A python time format string to format the time. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    time_format = d_(Str())

    #: A time selector is free to expand in width by default.
    hug_width = set_default('ignore')

    #: A reference to the ProxyDateSelector object.
    proxy = Typed(ProxyTimeSelector)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('time_format')
    def _update_proxy(self, change):
        """ An observer which updates the proxy with state change.

        """
        # The superclass implementation is sufficient.
        super(TimeSelector, self)._update_proxy(change)
