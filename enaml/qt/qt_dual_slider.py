#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.dual_slider import ProxyDualSlider

from .QtCore import Qt, Signal
from .QtGui import QPainter
from .QtWidgets import QSlider, QStyle, QStyleOptionSlider

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

    Dragging on the slider track will cause both the low and high values
    to move equally (i.e. the difference between them stays constant).

    TODO: Add support for tracking.

    """
    #: A signal emitted when the low value of the slider changes.
    lowValueChanged = Signal(int)

    #: A signal emitted when the high value of the slider changes.
    highValueChanged = Signal(int)

    #: Enums identifier the active slider thumb.
    BothThumbs = -1
    LowThumb = 0
    HighThumb = 1

    def __init__(self, parent=None):
        """ Initialize a QDualSlider.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget for the dual slider, or None.

        """
        super(QDualSlider, self).__init__(parent)
        self._low = self.minimum()
        self._high = self.maximum()
        self._active_thumb = self.LowThumb
        self._pressed_control = QStyle.SC_None
        self._click_offset = 0

    def lowValue(self):
        """ Get the low value of the dual slider.

        """
        return self._low

    def setLowValue(self, low):
        """ Set the low value of the dual slider.

        """
        self._low = low
        if low > self._high:
            self._high = low
        self.update()

    def highValue(self):
        """ Get the high value of the dual slider.

        """
        return self._high

    def setHighValue(self, high):
        """ Set the high value of the dual slider.

        """
        self._high = high
        if high < self._low:
            self._low = high
        self.update()

    def paintEvent(self, event):
        """ Override the paint event to draw both slider handles.

        """
        # based on the paintEvent for QSlider:
        # http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp
        painter = QPainter(self)
        style = self.style()
        low, high = self._low, self._high

        # Draw the low handle along with the groove and ticks.
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderHandle
        if self.tickPosition() != self.NoTicks:
            opt.subControls |= QStyle.SC_SliderTickmarks
        if (self._pressed_control and
            self._active_thumb == self.LowThumb or
            self._active_thumb == self.BothThumbs):
            opt.activeSubControls = self._pressed_control
            opt.state |= QStyle.State_Sunken
        else:
            opt.activeSubControls = QStyle.SC_None
        opt.sliderPosition = low
        opt.sliderValue = low
        style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

        # Draw high handle. The groove and ticks do not need repainting.
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderHandle
        if (self._pressed_control and
            self._active_thumb == self.HighThumb or
            self._active_thumb == self.BothThumbs):
            opt.activeSubControls = self._pressed_control
            opt.state |= QStyle.State_Sunken
        else:
            opt.activeSubControls = QStyle.SC_None
        opt.sliderPosition = high
        opt.sliderValue = high
        style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the control.

        In a typical slider control, when the user clicks on a point in
        the slider's total range but not on the thumbtrack, the control
        would jump to the value of the click location. For this control,
        clicks which are not direct hits will activate both slider
        handles for synchronized moving.

        """
        if event.button() != Qt.LeftButton:
            event.ignore()
            return

        event.accept()
        style = self.style()
        pos = event.pos()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        low, high = self._low, self._high

        # hit-test the high handle
        opt.sliderPosition = high
        high_rect = style.subControlRect(
            style.CC_Slider, opt, style.SC_SliderHandle, self
        )
        high_test = high_rect.contains(pos)

        # hit-test the low handle if needed.
        if high_test:
            low_test = False
        else:
            opt.sliderPosition = low
            low_rect = style.subControlRect(
                style.CC_Slider, opt, style.SC_SliderHandle, self
            )
            low_test = low_rect.contains(pos)

        # Set the internal state for painting and request an update.
        # The click offsets when clicking a thumbtrack are stored in
        # units of pixels. The offset for a click in the empty slider
        # area is stored in units of value.
        self._pressed_control = style.SC_SliderHandle
        if high_test:
            self._active_thumb = self.HighThumb
            self._click_offset = self._pick(pos - high_rect.topLeft())
        elif low_test:
            self._active_thumb = self.LowThumb
            self._click_offset = self._pick(pos - low_rect.topLeft())
        else:
            self._active_thumb = self.BothThumbs
            offset = self._pixelPosToRangeValue(self._pick(pos), opt)
            self._click_offset = offset
        self.setSliderDown(True)
        self.update()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the control.

        If the user has previously pressed the control, this will move
        the slider(s) to the appropriate position and request an update.

        """
        if self._pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        point = self._pick(event.pos())
        click_offset = self._click_offset

        thumb = self._active_thumb
        if thumb == self.BothThumbs:
            new_pos = self._pixelPosToRangeValue(point, opt)
            offset = new_pos - click_offset
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
            self.lowValueChanged.emit(new_pos)
            self.highValueChanged.emit(new_pos)
        elif thumb == self.LowThumb:
            new_pos = self._pixelPosToRangeValue(point - click_offset, opt)
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
            self.lowValueChanged.emit(new_pos)
        elif thumb == self.HighThumb:
            new_pos = self._pixelPosToRangeValue(point - click_offset, opt)
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos
            self.highValueChanged.emit(new_pos)
        else:
            raise ValueError('Invalid thumb enum value.')
        self.update()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event.

        This will update the internal state of the control and request
        an update.

        """
        if self._pressed_control == QStyle.SC_None:
            event.ignore()
            return
        event.accept()
        self._pressed_control = QStyle.SC_None
        self.setSliderDown(False)
        self.update()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _pick(self, pt):
        """ Pick the x or y coordinate of a point for the orientation.

        """
        return pt.x() if self.orientation() == Qt.Horizontal else pt.y()

    def _pixelPosToRangeValue(self, pos, opt):
        """ Map the pos argument to a value in the slider range

        """
        style = self.style()
        groove_rect = style.subControlRect(
            style.CC_Slider, opt, style.SC_SliderGroove, self
        )
        thumb_rect = style.subControlRect(
            style.CC_Slider, opt, style.SC_SliderHandle, self
        )
        if self.orientation() == Qt.Horizontal:
            thumb_width = thumb_rect.width()
            slider_min = groove_rect.x()
            slider_max = groove_rect.right() - thumb_width + 1
        else:
            thumb_height = thumb_rect.height()
            slider_min = groove_rect.y()
            slider_max = groove_rect.bottom() - thumb_height + 1
        value = style.sliderValueFromPosition(
            self.minimum(), self.maximum(), pos - slider_min,
            slider_max - slider_min, opt.upsideDown
        )
        return value


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
        #self.set_tracking(d.tracking)
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

    # def set_tracking(self, tracking):
    #     """ Set the tracking of the underlying widget.

    #     """
    #     self.widget.setTracking(tracking)
