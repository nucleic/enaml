#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QSlider
from .qt_control import QtControl


#: A map from Enaml constants to QSlider TickPosition values.
_TICK_POSITION_MAP = {
    'no_ticks': QSlider.NoTicks,
    'left': QSlider.TicksLeft,
    'right': QSlider.TicksRight,
    'top': QSlider.TicksAbove,
    'bottom': QSlider.TicksBelow,
    'both':QSlider.TicksBothSides
}


#: A map from Enaml enums to Qt constants for horizontal or vertical
#: orientation.
_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical
}


class QtSlider(QtControl):
    """ A Qt implementation of an Enaml Slider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QSlider widget.

        """
        return QSlider(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtSlider, self).create(tree)
        # Initialize the value after the minimum and maximum to avoid
        # the potential for premature internal clipping of the value.
        self.set_minimum(tree['minimum'])
        self.set_maximum(tree['maximum'])
        self.set_value(tree['value'])
        self.set_orientation(tree['orientation'])
        self.set_page_step(tree['page_step'])
        self.set_single_step(tree['single_step'])
        self.set_tick_interval(tree['tick_interval'])
        self.set_tick_position(tree['tick_position'])
        self.set_tracking(tree['tracking'])
        self.widget().valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_page_step(self, content):
        """ Handle the 'set_page_step' action from the Enaml widget.

        """
        self.set_page_step(content['page_step'])

    def on_action_set_single_step(self, content):
        """ Handle the 'set_single_step' action from the Enaml widget.

        """
        self.set_single_step(content['single_step'])

    def on_action_set_tick_interval(self, content):
        """ Handle the 'set_tick_interval' action from the Enaml widget.

        """
        self.set_tick_interval(content['tick_interval'])

    def on_action_set_tick_position(self, content):
        """ Handle the 'set_tick_position' action from the Enaml widget.

        """
        self.set_tick_position(content['tick_position'])

    def on_action_set_tracking(self, content):
        """ Handle the 'set_tracking' action from the Enaml widget.

        """
        self.set_tracking(content['tracking'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ Send the 'value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        if 'value' not in self.loopback_guard:
            content = {'value': self.widget().value()}
            self.send_action('value_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        with self.loopback_guard('value'):
            self.widget().setValue(value)

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        self.widget().setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        self.widget().setMinimum(minimum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget().setOrientation(_ORIENTATION_MAP[orientation])

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget().setPageStep(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget().setSingleStep(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget().setTickInterval(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        self.widget().setTickPosition(_TICK_POSITION_MAP[tick_position])

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget().setTracking(tracking)

