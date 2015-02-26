#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Typed, ForwardTyped, Property, Bool, Int, observe, set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyProgressBar(ProxyControl):
    """ The abstract definition of a proxy ProgressBar object.

    """
    #: A reference to the ProgressBar declaration.
    declaration = ForwardTyped(lambda: ProgressBar)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_value(self, value):
        raise NotImplementedError

    def set_text_visible(self, visible):
        raise NotImplementedError


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
    maximum = d_(Int(100))

    #: The position value of the Slider. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = d_(Int(0))

    #: A read only cached property which computes the integer percentage.
    percentage = d_(Property(cached=True), writable=False)

    #: Whether or not to display progress percentage on the control.
    #: This may not be supported by all toolkits and platforms.
    text_visible = d_(Bool(False))

    #: How strongly a component hugs it's content. ProgressBars expand
    #: to fill the available horizontal space by default.
    hug_width = set_default('ignore')

    #: A reference to the ProxyProgressBar object.
    proxy = Typed(ProxyProgressBar)

    @percentage.getter
    def get_percentage(self):
        """ The getter function for the read only percentage property.

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

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('minimum', 'maximum', 'value', 'text_visible')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        This observer also resets the 'percentage' property.

        """
        # The superclass handler implementation is sufficient.
        super(ProgressBar, self)._update_proxy(change)

    @observe('minimum', 'maximum', 'value')
    def _reset_percentage(self, change):
        """ An observer which resets the percentage property.

        """
        if change['type'] == 'update':
            self.get_member('percentage').reset(self)

    #--------------------------------------------------------------------------
    # PostSetAttr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum value for the progress bar.

        If the new minimum is greater than the current value or maximum,
        those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.value:
            self.value = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum value for the progress bar.

        If the new maximum is less than the current value or the minimum,
        those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.value:
            self.value = new

    #--------------------------------------------------------------------------
    # PostValidate Handlers
    #--------------------------------------------------------------------------
    def _post_validate_value(self, old, new):
        """ Post validate the value for the progress bar.

        The value is clipped to minimum and maximum bounds.

        """
        return max(self.minimum, min(new, self.maximum))
