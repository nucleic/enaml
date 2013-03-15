#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QSlider, QStyle, QStyleOptionSlider, QPainter

from atom.api import Int, Typed

from enaml.widgets.dual_slider import ProxyDualSlider

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
LOW_VALUE_FLAG = 0x1
HIGH_VALUE_FLAG = 0x2

class QDualSlider(QSlider):
    """ A Qt implementation of a dual slider.

        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.

        Dragging on the slider track will cause both the low and high values to
        move equally (ie the difference between them stays constant).

    """

    lowValueChanged = pyqtSignal(int)

    highValueChanged = pyqtSignal(int)

    def __init__(self, *args):
        """ Configure some internal attributes needed to render the
        dual slider interaction. Modeled using the private class from
        QSlider

        """
        super(QDualSlider, self).__init__(*args)

        self._low = self.minimum()
        self._high = self.maximum()

        self._pressed_control = QStyle.SC_None
        self._hover_control = QStyle.SC_None
        self._click_offset = 0

        # 0 for the low, 1 for the high, -1 for both
        self._active_slider = 0

    def lowValue(self):
        """ Get the low value of the dual slider

        """
        return self._low

    def setLowValue(self, low):
        """ Set the low value of the dual slider

        """
        self._low = low
        self.update()

    def highValue(self):
        """ Get the high value of the dual slider

        """
        return self._high

    def setHighValue(self, high):
        """ Set the high value of the dual slider

        """
        self._high = high
        self.update()

    def paintEvent(self, event):
        """ Override the paint event to draw both slider handles

        """
        # based on http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp

        painter = QPainter(self)
        style = self.style()

        for i, value in enumerate([self._low, self._high]):
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            # Only draw the groove for the first slider so it doesn't get drawn
            # on top of the existing ones every time
            if i == 0:
                opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderHandle
            else:
                opt.subControls = QStyle.SC_SliderHandle

            if self.tickPosition() != self.NoTicks:
                opt.subControls |= QStyle.SC_SliderTickmarks

            if self._pressed_control and self._active_slider == i:
                opt.activeSubControls = self._pressed_control
                opt.state |= QStyle.State_Sunken
            else:
                opt.activeSubControls = self._hover_control

            opt.sliderPosition = value
            opt.sliderValue = value
            style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        """ Mouse press event to process clicking on either handle or
        the slider groove

        """
        event.accept()

        style = self.style()
        button = event.button()

        # In a normal slider control, when the user clicks on a point in the
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked.
        # For this control, clicks which are not direct hits will slide both
        # slider parts

        if button:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            self._active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)
                if sr.contains(event.pos()):
                    self._active_slider = i
                    self._pressed_control = style.SC_SliderHandle

                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    self._click_offset = self._pick(event.pos() - sr.topLeft())
                    break

            if self._active_slider < 0:
                self._pressed_control = QStyle.SC_SliderHandle
                self._click_offset = self._pixelPosToRangeValue(self._pick(event.pos()), opt)
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """ Mouse move event to handle dragging either slider handle or the
        slider groove

        """
        if self._pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        new_pos = self._pixelPosToRangeValue(self._pick(event.pos()) - self._click_offset, opt)

        if self._active_slider < 0:
            new_pos = self._pixelPosToRangeValue(self._pick(event.pos()), opt)
            offset = new_pos - self._click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff
            self._click_offset = new_pos
        elif self._active_slider == 0:
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
        else:
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos


        self.update()

        if self._active_slider != 1:
            self.lowValueChanged.emit(new_pos)
        if self._active_slider != 0:
            self.highValueChanged.emit(new_pos)

    def mouseReleaseEvent(self, event):
        """ Change the render state of the handles when the mouse is released
        if the user was dragging a handle

        """
        if self._pressed_control == QStyle.SC_None:
            event.ignore()
            return

        event.accept()
        if self._pressed_control == QStyle.SC_SliderHandle:
            self.setSliderDown(False)
        self._pressed_control = QStyle.SC_None
        self.setRepeatAction(self.SliderNoAction)
        self.update()

    def _pick(self, pt):
        """ Return either the x or y value of the point depending on the
        orientation of the slider

        """
        if self.orientation() == Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def _pixelPosToRangeValue(self, pos, opt):
        """ Map the pos argument to a value in the slider range

        """
        style = self.style()

        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(self.minimum(), self.maximum(),
                                             pos-slider_min, slider_max-slider_min,
                                             opt.upsideDown)


class QtDualSlider(QtControl, ProxyDualSlider):
    """ A Qt implementation of an Enaml ProxyDualSlider.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDualSlider)

    #: Cyclic notification guard flags.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDualSlider widget.

        """
        self.widget = QDualSlider(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDualSlider, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_low_value(d.low_value)
        self.set_high_value(d.high_value)
        self.set_orientation(d.orientation)
        self.set_tick_interval(d.tick_interval)
        self.set_tick_position(d.tick_position)
        self.set_tracking(d.tracking)
        self.widget.lowValueChanged.connect(self.on_low_value_changed)
        self.widget.highValueChanged.connect(self.on_high_value_changed)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_low_value_changed(self):
        """ Send the 'low_value_changed' action to the Enaml widget when the
        slider's low value has changed.

        """
        if not self._guard & LOW_VALUE_FLAG:
            self._guard |= LOW_VALUE_FLAG
            try:
                self.declaration.low_value = self.widget.lowValue()
            finally:
                self._guard &= ~LOW_VALUE_FLAG

    def on_high_value_changed(self):
        """ Send the 'high_value_changed' action to the Enaml widget when the
        slider's high value has changed.

        """
        if not self._guard & HIGH_VALUE_FLAG:
            self._guard |= HIGH_VALUE_FLAG
            try:
                self.declaration.high_value = self.widget.highValue()
            finally:
                self._guard &= ~HIGH_VALUE_FLAG

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

    def set_low_value(self, value):
        """ Set the value of the underlying widget.

        """
        if not self._guard & LOW_VALUE_FLAG:
            self._guard |= LOW_VALUE_FLAG
            try:
                self.widget.setLowValue(value)
            finally:
                self._guard &= ~LOW_VALUE_FLAG

    def set_high_value(self, value):
        """ Set the value of the underlying widget.

        """
        if not self._guard & HIGH_VALUE_FLAG:
            self._guard |= HIGH_VALUE_FLAG
            try:
                self.widget.setHighValue(value)
            finally:
                self._guard &= ~HIGH_VALUE_FLAG

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
