#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import CachedProperty, Int, observe, set_default

from enaml.core.declarative import d_

from .control import Control


class ProgressBar(Control):
    """ A control which displays a value as a ticking progress bar.

    """
    #: The minimum progress value. If the minimum value is changed such
    #: that it becomes greater than the current value or the maximum
    #: value, then those values will be adjusted. The default is 0.
    minimum = d_(Int(0))

    #: The maximum progress value. If the maximum value is changed such
    #: that it becomes smaller than the current value or the minimum
    #: value, then those values will be adjusted. The default is 100.
    maximum = d_(Int(10))

    #: The position value of the Slider. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = d_(Int(0))

    #: The percentage completed, rounded to an integer. This is a
    #: readonly value for convenient use by other Components.
    percentage = CachedProperty(Int())

    #: How strongly a component hugs it's content. ProgressBars expand
    #: to fill the available horizontal space by default.
    hug_width = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(ProgressBar, self).snapshot()
        snap['maximum'] = self.maximum
        snap['minimum'] = self.minimum
        snap['value'] = self.value
        return snap

    @observe(r'^(minimum|maximum|value)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ProgressBar, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    def _get_percentage(self):
        """ The property getter for the ProgressBar percentage.

        """
        minimum = self.minimum
        maximum = self.maximum
        value = self.value
        dy = maximum - minimum
        if dy == 0:
            res = 0
        elif value == maximum:
            res = 100
        else:
            dx = float(value - minimum)
            res = int(round(100.0 * dx / dy))
            # We already excluded the case where the value was exactly
            # the maximum, so we can't really be at 100%, so round this
            # down to 99% if necessary.
            res = min(res, 99)
        return res

    @observe(r'^(minimum|maximum|value)$', regex=True)
    def _reset_percentage(self, change):
        """ Reset the percentage property when its dependencies change.

        """
        CachedProperty.reset(self, 'percentage')

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_minimum(self, old, new):
        """ Post validate the minimum value for the progress bar.

        If the new minimum is greater than the current value or maximum,
        those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.value:
            self.value = new
        return new

    def _post_validate_maximum(self, old, new):
        """ Post validate the maximum value for the progress bar.

        If the new maximum is less than the current value or the minimum,
        those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.value:
            self.value = new
        return new

    def _post_validate_value(self, old, new):
        """ Post validate the value for the progress bar.

        The value is clipped to minimum and maximum bounds.

        """
        return max(self.minimum, min(new, self.maximum))

