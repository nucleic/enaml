#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import datetime as pydatetime

from atom.api import Typed, observe
from dateutil.parser import parse as parse_iso_dt

from enaml.core.declarative import d_

from .control import Control


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

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(BoundedDatetime, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['datetime'] = self.datetime.isoformat()
        return snap

    @observe(r'^(minimum|maximum|date)$', regex=True)
    def send_datetime_change(self, change):
        """ An observer which sends state change to the client.

        """
        name = change.name
        if name not in self.loopback_guard:
            content = {name: change.new.isoformat()}
            self.send_action('set_' + name, content)

    #--------------------------------------------------------------------------
    # Widget Updates
    #--------------------------------------------------------------------------
    def on_action_datetime_changed(self, content):
        """ Handle the 'datetime_changed' action from the client widget.

        """
        datetime = parse_iso_dt(content['datetime'])
        self.set_guarded(datetime=datetime)

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_minimum(self, old, new):
        """ Post validate the minimum datetime.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.datetime:
            self.datetime = new
        return new

    def _post_validate_maximum(self, old, new):
        """ Post validate the maximum datetime.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.datetime:
            self.date = new
        return new

    def _post_validate_datetime(self, old, new):
        """ Post validate the datetime for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))

