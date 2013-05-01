
from PyQt4.QtCore import Qt, QPoint, QEvent
from PyQt4.QtGui import (
    QStyle, QStyleOptionSlider, QPainter, QPolygon, QColor, QRegion,
    QPen, QCursor,
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
        histmax = max(histogram)/0.8
        self._histogram = [i/histmax for i in histogram]
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
        col = QColor("#ADD8E6")
        pen = QPen(col, 2)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderHandle
        opt.sliderPosition = low
        opt.sliderValue = low
        self.drawControl(opt, style, painter, pen, True)

        # Draw high handle. The groove and ticks do not need repainting.
        opt.sliderPosition = high
        opt.sliderValue = high
        self.drawControl(opt, style, painter, pen, False)

    def drawControl(self, opt, style, painter, pen, is_low=False):
        if not self._show_thumbs:
            p = QPen(Qt.gray)
            p.setWidth(0.5)
            overhang = 2
        else:
            p = QPen(Qt.black)
            overhang = 8

        rect = style.subControlRect(
            style.CC_Slider, opt, style.SC_SliderHandle, self
        )
        margin = 1
        painter.setPen(p)
        if is_low:
            x, height = rect.left()+1, self.height()
            factor = 1
        else:
            x, height = rect.right()-1, self.height()
            factor = -1

        top = QPoint(x, margin)
        bottom = QPoint(x, height - margin)

        offset = QPoint(factor * overhang, 0)
        painter.drawPolyline(*[top + offset, top, bottom, bottom + offset])

        if self._show_thumbs:
            offset = QPoint(factor * 4, 0)
            painter.drawLine(top + offset, bottom + offset)
            painter.setPen(pen)
            off1, off2 = QPoint(factor * 2, 2), QPoint(factor * 2, -2)
            painter.drawLine(top + off1, bottom + off2)

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
            #if new_pos >= self._high:
            #    new_pos = self._high - 1
            self._low = new_pos
            self.lowValueChanged.emit(new_pos)
        elif thumb == self.HighThumb:
            new_pos = self._pixelPosToRangeValue(point - click_offset, opt)
            #if new_pos <= self._low:
            #    new_pos = self._low + 1
            self._high = new_pos
            self.highValueChanged.emit(new_pos)
        else:
            raise ValueError('Invalid thumb enum value.')
        self._calculate_clipping()
        self.update()

    def hitTest(self, pos):
        style = self.style()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        low, high = self._low, self._high

        # hit-test the high handle
        opt.sliderPosition = high
        high_rect = style.subControlRect(
            style.CC_Slider, opt, style.SC_SliderHandle, self
        )
        if not high_rect.contains(pos):
            # hit-test the low handle if needed.
            opt.sliderPosition = low
            low_rect = style.subControlRect(
                style.CC_Slider, opt, style.SC_SliderHandle, self
            )
            return low_rect.contains(pos)
        else:
            return True

    def event(self, event):
        """ Handle hover enter and leave by showing the slider thumbs.

        """
        etype = event.type()
        if etype == QEvent.HoverEnter:
            self.setThumbsVisible(True)
        elif etype == QEvent.HoverLeave:
            self.setThumbsVisible(False)
        elif etype == QEvent.HoverMove:
            if self.hitTest(event.pos()):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        return super(QHistogramSlider, self).event(event)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _calculate_points(self):
        style = self.style()
        nbins = len(self._histogram)
        if nbins:
            bounds = self.rect()
            width, h2 = bounds.width(), bounds.height()/2
            xinc = width / float(nbins)
            points = ([QPoint(0, h2)] +
                [QPoint(i * xinc, (1 - val) * h2) for i, val in enumerate(self._histogram)] +
                [QPoint(width, h2)] +
                [QPoint(width - (i + 1) * xinc, (1 + val) * h2) for i, val in enumerate(reversed(self._histogram))] +
                [QPoint(0, h2)])
            self._points = QPolygon(points)

        self._midpoint_pos = style.sliderPositionFromValue(
            self.minimum(), self.maximum(), self._midpoint, self.width()
        )

    def _calculate_clipping(self):
        style = self.style()
        minimum, maximum = self.minimum(), self.maximum()
        low, high = self._low, self._high
        width, height = self.width(), self.height()

        # Shade the areas up to the low and high sliders
        low_pos = style.sliderPositionFromValue(minimum, maximum, low, width)
        high_pos = style.sliderPositionFromValue(minimum, maximum, high, width)

        if low_pos <= high_pos:
            self._clip = QRegion(low_pos, 0, high_pos - low_pos, height)
        else:
            self._clip = (QRegion(0, 0, high_pos, height) +
                          QRegion(low_pos, 0, width, height))

    def _recalc_midpoint(self):
        minimum, maximum = self._minimum, self._maximum
        if minimum < 0:
            midpoint = int(100*(-minimum / (maximum - minimum)))
        else:
            midpoint = -1
        self.setMidpoint(midpoint)
