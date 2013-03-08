#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Int, Range, observe

from enaml.core.declarative import d_

from .control import Control


TickPosition = Enum('no_ticks', 'left', 'right', 'top', 'bottom', 'both')


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

    #: A flag indicating whether the user has explicitly set the hug
    #: property. If it is not explicitly set, the hug values will be
    #: updated automatically when the orientation changes.
    _explicit_hug = Bool(False)

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the slider.

        """
        snap = super(Slider, self).snapshot()
        snap['minimum'] = self.minimum
        snap['maximum'] = self.maximum
        snap['value'] = self.value
        snap['single_step'] = self.single_step
        snap['page_step'] = self.page_step
        snap['tick_position'] = self.tick_position
        snap['tick_interval'] = self.tick_interval
        snap['orientation'] = self.orientation
        snap['tracking'] = self.tracking
        return snap

    @observe(r'^(minimum|maximum|value|single_step|page_step|tick_position|'
             r'tick_interval|orientation|tracking)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Slider, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Update Handlers
    #--------------------------------------------------------------------------
    def on_action_value_changed(self, content):
        """ Handle the 'value_changed' action from the client widget.

        The content will contain the 'value' of the slider.

        """
        self.set_guarded(value=content['value'])

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    def _observe_orientation(self, change):
        """ Updates the hug properties if they are not explicitly set.

        """
        if not self._explicit_hug:
            self.hug_width = self._default_hug_width()
            self.hug_height = self._default_hug_height()
            # Reset to False to remove the effect of the above.
            self._explicit_hug = False

    #--------------------------------------------------------------------------
    # Default Handlers
    #--------------------------------------------------------------------------
    def _default_hug_width(self):
        """ Get the default hug width for the slider.

        The default hug width is computed based on the orientation.

        """
        if self.orientation == 'horizontal':
            return 'ignore'
        return 'strong'

    def _default_hug_height(self):
        """ Get the default hug height for the slider.

        The default hug height is computed based on the orientation.

        """
        if self.orientation == 'vertical':
            return 'ignore'
        return 'strong'

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_minimum(self, old, new):
        """ Post validate the minimum value for the slider.

        If the new minimum is greater than the current value or maximum,
        those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.value:
            self.value = new
        return new

    def _post_validate_maximum(self, old, new):
        """ Post validate the maximum value for the slider.

        If the new maximum is less than the current value or the minimum,
        those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.value:
            self.value = new
        return new

    def _post_validate_value(self, old, new):
        """ Post validate the value for the slider.

        The value is clipped to minimum and maximum bounds.

        """
        return max(self.minimum, min(new, self.maximum))

    def _post_validate_hug_width(self, old, new):
        """ Post validate the hug width for the slider.

        This sets the explicit hug flag to True.

        """
        self._explicit_hug = True
        return new

    def _post_validate_hug_height(self, old, new):
        """ Post validate the hug height for the slider.

        This sets the explicit hug flag to True.

        """
        self._explicit_hug = True
        return new

