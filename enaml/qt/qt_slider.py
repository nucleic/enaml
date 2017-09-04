#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.slider import ProxySlider

from .QtCore import Qt
from .QtWidgets import QSlider

from .qt_control import QtControl


#: A map from Enaml constants to QSlider TickPosition values.
TICK_POSITION = {
    'no_ticks': QSlider.NoTicks,
    'left': QSlider.TicksLeft,
    'right': QSlider.TicksRight,
    'top': QSlider.TicksAbove,
    'bottom': QSlider.TicksBelow,
    'both': QSlider.TicksBothSides
}


#: A map from Enaml enums to Qt constants for horizontal or vertical
#: orientation.
ORIENTATION = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical
}


#: A cyclic guard flag
VALUE_FLAG = 0x1


class QtSlider(QtControl, ProxySlider):
    """ A Qt implementation of an Enaml ProxySlider.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QSlider)

    #: Cyclic notification guard flags.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QSlider widget.

        """
        self.widget = QSlider(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtSlider, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_value(d.value)
        self.set_orientation(d.orientation)
        self.set_page_step(d.page_step)
        self.set_single_step(d.single_step)
        self.set_tick_interval(d.tick_interval)
        self.set_tick_position(d.tick_position)
        self.set_tracking(d.tracking)
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ Send the 'value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.declaration.value = self.widget.value()
            finally:
                self._guard &= ~VALUE_FLAG

    #--------------------------------------------------------------------------
    # ProxySlider API
    #--------------------------------------------------------------------------
    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        self.widget.setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        self.widget.setMinimum(minimum)

    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        if not self._guard & VALUE_FLAG:
            self._guard |= VALUE_FLAG
            try:
                self.widget.setValue(value)
            finally:
                self._guard &= ~VALUE_FLAG

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget.setPageStep(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget.setSingleStep(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget.setTickInterval(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        self.widget.setTickPosition(TICK_POSITION[tick_position])

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget.setOrientation(ORIENTATION[orientation])

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget.setTracking(tracking)
