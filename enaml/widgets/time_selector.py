#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, observe, set_default

from enaml.core.declarative import d_

from .bounded_time import BoundedTime


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

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(TimeSelector, self).snapshot()
        snap['time_format'] = self.time_format
        return snap

    @observe('time_format', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass implementation is sufficient.
        super(TimeSelector, self).send_member_change(change)

