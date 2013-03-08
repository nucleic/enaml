#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import datetime, time as pytime

from atom.api import Typed, observe
from dateutil.parser import parse as parse_iso_dt

from enaml.core.declarative import d_

from .control import Control


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

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(BoundedTime, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['time'] = self.time.isoformat()
        return snap

    @observe(r'^(minimum|maximum|date)$', regex=True)
    def send_time_change(self, change):
        """ An observer which sends state change to the client.

        """
        name = change.name
        if name not in self.loopback_guard:
            content = {name: change.new.isoformat()}
            self.send_action('set_' + name, content)

    #--------------------------------------------------------------------------
    # Widget Updates
    #--------------------------------------------------------------------------
    def on_action_time_changed(self, content):
        """ Handle for the 'time_changed' action sent by the client.

        """
        time = parse_iso_dt(content['time']).time()
        self.set_guarded(time=time)

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_minimum(self, old, new):
        """ Post validate the minimum time.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.time:
            self.time = new
        return new

    def _post_validate_maximum(self, old, new):
        """ Post validate the maximum time.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.time:
            self.date = new
        return new

    def _post_validate_time(self, old, new):
        """ Post validate the time for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))

