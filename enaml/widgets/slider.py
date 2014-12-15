#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Int, Range, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .control import Control, ProxyControl


#: The base tick position enum definition.
TickPosition = Enum('no_ticks', 'left', 'right', 'top', 'bottom', 'both')


class ProxySlider(ProxyControl):
    """ The abstract definition of a proxy Slider object.

    """
    #: A reference to the Slider declaration.
    declaration = ForwardTyped(lambda: Slider)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_value(self, value):
        raise NotImplementedError

    def set_single_step(self, step):
        raise NotImplementedError

    def set_page_step(self, step):
        raise NotImplementedError

    def set_tick_position(self, position):
        raise NotImplementedError

    def set_tick_interval(self, interval):
        raise NotImplementedError

    def set_orientation(self, orientation):
        raise NotImplementedError

    def set_tracking(self, tracking):
        raise NotImplementedError


class Slider(Control):
    """ A simple slider widget that can be used to select from a range
    of integral values.

    A `SliderTransform` can be used to transform the integer range
    of the slider into another data space. For more details, see
    `enaml.stdlib.slider_transform`.

    """
    #: The minimum slider value. If the minimum value is changed such
    #: that it becomes greater than the current value or the maximum
    #: value, then those values will be adjusted. The default is 0.
    minimum = d_(Int(0))

    #: The maximum slider value. If the maximum value is changed such
    #: that it becomes smaller than the current value or the minimum
    #: value, then those values will be adjusted. The default is 100.
    maximum = d_(Int(100))

    #: The position value of the Slider. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = d_(Int(0))

    #: Defines the number of steps that the slider will move when the
    #: user presses the arrow keys. The default is 1. An upper limit
    #: may be imposed according the limits of the client widget.
    single_step = d_(Range(low=1))

    #: Defines the number of steps that the slider will move when the
    #: user presses the page_up/page_down keys. The Default is 10. An
    #: upper limit may be imposed on this value according to the limits
    #: of the client widget.
    page_step = d_(Range(low=1, value=10))

    #: A TickPosition enum value indicating how to display the tick
    #: marks. Note that the orientation takes precedence over the tick
    #: mark position and an incompatible tick position will be adapted
    #: according to the current orientation. The default tick position
    #: is 'bottom'.
    tick_position = d_(TickPosition('bottom'))

    #: The interval to place between slider tick marks in units of
    #: value (as opposed to pixels). The minimum value is 0, which
    #: indicates that the choice is left up to the client.
    tick_interval = d_(Range(low=0))

    #: The orientation of the slider. The default orientation is
    #: horizontal. When the orientation is flipped the tick positions
    #: (if set) also adapt to reflect the changes  (e.g. the LEFT
    #: becomes TOP when the orientation becomes horizontal).
    orientation = d_(Enum('horizontal', 'vertical'))

    #: If True, the value is updated while sliding. Otherwise, it is
    #: only updated when the slider is released. Defaults to True.
    tracking = d_(Bool(True))

    #: Whether or not to automatically adjust the 'hug_width' and
    #: 'hug_height' values based on the value of 'orientation'.
    auto_hug = d_(Bool(True))

    #: A reference to the ProxySlider object.
    proxy = Typed(ProxySlider)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('minimum', 'maximum', 'value', 'single_step', 'page_step',
        'tick_position', 'tick_interval', 'orientation', 'tracking')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(Slider, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # DefaultValue Handlers
    #--------------------------------------------------------------------------
    def _default_hug_width(self):
        """ Get the default hug width for the separator.

        The default hug width is computed based on the orientation.

        """
        if self.orientation == 'horizontal':
            return 'ignore'
        return 'strong'

    def _default_hug_height(self):
        """ Get the default hug height for the separator.

        The default hug height is computed based on the orientation.

        """
        if self.orientation == 'vertical':
            return 'ignore'
        return 'strong'

    #--------------------------------------------------------------------------
    # PostSetAttr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_orientation(self, old, new):
        """ Post setattr the orientation for the tool bar.

        If auto hug is enabled, the hug values will be updated.

        """
        if self.auto_hug:
            if new == 'vertical':
                self.hug_width = 'strong'
                self.hug_height = 'ignore'
            else:
                self.hug_width = 'ignore'
                self.hug_height = 'strong'

    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum value for the slider.

        If the new minimum is greater than the current value or maximum,
        those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.value:
            self.value = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum value for the slider.

        If the new maximum is less than the current value or the minimum,
        those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.value:
            self.value = new

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_value(self, old, new):
        """ Post validate the value for the slider.

        The value is clipped to minimum and maximum bounds.

        """
        return max(self.minimum, min(new, self.maximum))
