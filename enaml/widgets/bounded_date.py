#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from datetime import date as pydate

from atom.api import Typed, observe
from dateutil.parser import parse as parse_iso_dt

from enaml.core.declarative import d_

from .control import Control


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

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(BoundedDate, self).snapshot()
        snap['minimum'] = self.minimum.isoformat()
        snap['maximum'] = self.maximum.isoformat()
        snap['date'] = self.date.isoformat()
        return snap

    @observe(r'^(minimum|maximum|date)$', regex=True)
    def send_date_change(self, change):
        """ An observer which sends state change to the client.

        """
        name = change.name
        if name not in self.loopback_guard:
            content = {name: change.new.isoformat()}
            self.send_action('set_' + name, content)

    #--------------------------------------------------------------------------
    # Widget Updates
    #--------------------------------------------------------------------------
    def on_action_date_changed(self, content):
        """ Handle the 'date_changed' action from the UI control.

        """
        print 'datewidget', self
        date = parse_iso_dt(content['date']).date()
        self.set_guarded(date=date)

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_minimum(self, old, new):
        """ Post validate the minimum date.

        If the new minimum is greater than the current value or the
        maximum, those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.date:
            self.date = new
        return new

    def _post_validate_maximum(self, old, new):
        """ Post validate the maximum date.

        If the new maximum is less than the current value or the
        minimum, those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.date:
            self.date = new
        return new

    def _post_validate_date(self, old, new):
        """ Post validate the date for the control.

        If it lies outside of minimum and maximum bounds, it will be
        clipped to the bounds.

        """
        return max(self.minimum, min(new, self.maximum))

