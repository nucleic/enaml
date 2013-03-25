
from PyQt4.QtCore import Qt, QPoint, QEvent
from PyQt4.QtGui import (
    QStyle, QStyleOptionSlider, QPainter, QPolygon, QColor, QRegion, QPen
)

from enaml.qt.qt_dual_slider import QDualSlider


class QHistogramSlider(QDualSlider):
    """ A Qt implementation of a dual slider with a density distribution.

    """
    def __init__(self, parent=None):
        """ Initialize a QHistogramSlider.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget for the dual slider, or None.

        """
        super(QHistogramSlider, self).__init__(parent)
        self.setOrientation(Qt.Horizontal)
        self._points = QPolygon()
        self._clip = QRegion()
        self._show_thumbs = False
        self._midpoint = -1
        self._histogram = []

    def setThumbsVisible(self, visible):
        """ Set whether to hide or show the thumbs.

        """
        self._show_thumbs = visible
        self.update()

    def setHistogram(self, histogram):
        """ Set the histogram to draw

        """
        self._histogram = histogram
        self._calculate_points()
        self.update()

    def setMidpoint(self, midpoint):
        """ Set the midpoint

        """
        self._midpoint = midpoint
        self.update()

    def resizeEvent(self, event):
        super(QHistogramSlider, self).resizeEvent(event)
        self._calculate_points()
        self._calculate_clipping()

    def paintEvent(self, event):
        """ Override the paint event to draw both slider handles.

        """
        # based on the paintEvent for QSlider:
        # http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp
        painter = QPainter(self)
        style = self.style()

        low, high = self._low, self._high
        width, height = self.width(), self.height()

        # Draw the histogram
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.transparent)
        painter.setBrush(QColor(220, 220, 220))
        painter.drawPolygon(self._points)

        # Shade the areas up to the low and high sliders
        painter.save()
        painter.setClipRegion(self._clip)
        painter.setBrush(QColor(100, 100, 100))
        painter.drawPolygon(self._points)
        painter.restore()

        # Draw the midpoint
        if self._midpoint != -1:
            pos = self._midpoint_pos
            palette = self.palette()
            pen = QPen(palette.window().color())
            pen.setWidth(2.)
            painter.setPen(pen)
            painter.drawLine(pos, 0, pos, height)

        # Draw the low handle along with the groove and ticks.
        if self._show_thumbs:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            opt.subControls = QStyle.SC_SliderHandle
            #if self.tickPosition() != self.NoTicks:
            #    opt.subControls |= QStyle.SC_SliderTickmarks
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

    def mouseMoveEvent(self, event):
        """ Recalculate clipping for graying out histogram.

        """
        super(QHistogramSlider, self).mouseMoveEvent(event)
        self._calculate_clipping()

    def event(self, event):
        """ Handle hover enter and leave by showing the slider thumbs.

        """
        etype = event.type()
        if etype == QEvent.HoverEnter:
            self.setThumbsVisible(True)
        elif etype == QEvent.HoverLeave:
            self.setThumbsVisible(False)
        return super(QHistogramSlider, self).event(event)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _calculate_points(self):
        style = self.style()
        nbins = len(self._histogram)
        if nbins:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            thumb_rect = style.subControlRect(
                style.CC_Slider, opt, style.SC_SliderHandle, self
            )

            thumb_width = thumb_rect.width()/2.

            bounds = self.rect()
            width, h2 = bounds.width() - 2*thumb_width, bounds.height()/2
            xinc = width / float(nbins)
            points = ([QPoint(thumb_width, h2)] +
                [QPoint(thumb_width + i * xinc, (1 - val) * h2) for i, val in enumerate(self._histogram)] +
                [QPoint(thumb_width + width, h2)] +
                [QPoint(thumb_width + width - (i + 1) * xinc, (1 + val) * h2) for i, val in enumerate(reversed(self._histogram))] +
                [QPoint(thumb_width, h2)])
            self._points = QPolygon(points)

        self._midpoint_pos = style.sliderPositionFromValue(
            self.minimum(), self.maximum(), self._midpoint, self.width()
        )

    def _calculate_clipping(self):
        style = self.style()
        minimum, maximum = self.minimum(), self.maximum()
        low, high = self._low, self._high
        width = self.width()

        # Shade the areas up to the low and high sliders
        low_pos = style.sliderPositionFromValue(minimum, maximum, low, width)
        high_pos = style.sliderPositionFromValue(minimum, maximum, high, width)

        self._clip = QRegion(low_pos, 0, high_pos - low_pos, self.height())

    def _recalc_midpoint(self):
        minimum, maximum = self._minimum, self._maximum
        if minimum < 0:
            midpoint = int(100*(-minimum / (maximum - minimum)))
        else:
            midpoint = -1
        self.setMidpoint(midpoint)
