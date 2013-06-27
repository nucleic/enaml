""" An extremely hack script that was used to render the dock guide icons.

"""
from enaml.qt.QtCore import *
from enaml.qt.QtGui import *


class GuidePad(object):

    LeftPosition = 0

    TopPosition = 1

    RightPosition = 2

    BottomPosition = 3

    CenterTop = 4

    SplitLeft = 5

    SplitTop = 6

    SplitRight = 7

    SplitBottom = 8

    SplitHorizontal = 9

    SplitVertical = 10

    CenterLeft = 11

    CenterRight = 12

    CenterBottom = 13

    @staticmethod
    def makePath(size):
        path = QPainterPath()
        rect = QRectF(0, 0, size.width(), size.height())
        path.addRoundedRect(rect, 2.0, 2.0)
        return path

    @staticmethod
    def makeTriPath():
        path = QPainterPath()
        path.moveTo(0.0, 0.0)
        path.lineTo(9.0, 0.0)
        path.lineTo(5.0, 4.0)
        path.lineTo(4.0, 4.0)
        path.lineTo(0.0, 0.0)
        return path

    def __init__(self, rect, position=None):
        self._rect = rect
        self._position = position
        self._opacity = 0.8
        self._path = GuidePad.makePath(rect.size())
        self._tri_path = GuidePad.makeTriPath()
        grad = QLinearGradient(0.0, 0.0, 0.0, 1.0)
        grad.setCoordinateMode(QGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QColor(0xF5, 0xF8, 0xFB))
        grad.setColorAt(0.33, QColor(0xF0, 0xF3, 0xF6))
        grad.setColorAt(0.66, QColor(0xE5, 0xE8, 0xEE))
        grad.setColorAt(1.0, QColor(0xDE, 0xE2, 0xE9))
        self._brush = QBrush(grad)
        grad = QLinearGradient(0.0, 0.0, 0.0, 1.0)
        grad.setCoordinateMode(QGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QColor(0xFC, 0xEC, 0xBE))
        grad.setColorAt(1.0, QColor(0xF7, 0xC7, 0x73))
        self._fill_brush = QBrush(grad)
        self._pen = QPen(QColor(0x8A, 0x91, 0x9C))

    def rect(self):
        return self._rect

    def setRect(self, rect):
        old = self._rect
        self._rect = rect
        if rect.isValid():
            if self._path is None or old.size() != rect.size():
                self._path = GuidePad.makePath(rect.size())
        else:
            self._path = None

    def contains(self, pos):
        return self._rect.contains(pos)

    def intersects(self, rect):
        return self._rect.intersects(rect)

    def guidePosition(self):
        return self._guide_pos

    def setGuidePosition(self, position):
        self._position = position

    def brush(self):
        return self._brush

    def setBrush(self, brush):
        self._brush = brush

    def pen(self):
        return self._pen

    def setPen(self, pen):
        self._pen = pen

    def opacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = opacity

    def paint(self, painter):
        rect = self._rect
        if not rect.isValid():
            return
        painter.save()
        painter.translate(rect.x(), rect.y())

        # Draw the background
        painter.setOpacity(1.0)#self._opacity)
        painter.fillPath(self._path, self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._path)

        color = QColor(0x44, 0x58, 0x79)
        fill_brush = self._fill_brush
        painter.setPen(color)
        position = self._position
        if position == self.TopPosition:
            width = rect.width() - 8
            height = rect.height() / 2 - 4
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            painter.fillRect(QRect(5, 8, width - 1, height - 4), fill_brush)
            painter.setRenderHint(QPainter.Antialiasing)
            w = rect.width() / 2 + 5
            h = rect.height() - 5
            painter.translate(w, h)
            painter.rotate(180)
            painter.fillPath(self._tri_path, color)
        elif position == self.BottomPosition:
            width = rect.width() - 8
            height = rect.height() / 2 - 4
            painter.drawRect(QRect(4, height + 4, width, height))
            painter.fillRect(QRect(5, height + 5, width - 1, 3), color)
            painter.fillRect(QRect(5, height + 8, width - 1, height - 4), fill_brush)
            painter.setRenderHint(QPainter.Antialiasing)
            w = rect.width() / 2 - 4
            painter.translate(w, 6)
            painter.fillPath(self._tri_path, color)
        elif position == self.LeftPosition:
            width = rect.width() / 2 - 4
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            painter.fillRect(QRect(5, 8, width - 1, height - 4), fill_brush)
            painter.setRenderHint(QPainter.Antialiasing)
            w = rect.width() - 5
            h = rect.height() / 2 - 4
            painter.translate(w, h)
            painter.rotate(90)
            painter.fillPath(self._tri_path, color)
        elif position == self.RightPosition:
            width = rect.width() / 2 - 4
            height = rect.height() - 8
            painter.drawRect(QRect(width + 4, 4, width, height))
            painter.fillRect(QRect(width + 5, 5, width - 1, 3), color)
            painter.fillRect(QRect(width + 5, 8, width - 1, height - 4), fill_brush)
            painter.setRenderHint(QPainter.Antialiasing)
            h = rect.height() / 2 + 5
            painter.translate(6, h)
            painter.rotate(-90)
            painter.fillPath(self._tri_path, color)
        elif position == self.CenterTop:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            painter.fillRect(QRect(5, 8, width - 1, height - 4), fill_brush)
        elif position == self.CenterBottom:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5 + height - 4, width - 1, 3), color)
            painter.fillRect(QRect(5, 5, width - 1, height - 4), fill_brush)
        elif position == self.CenterLeft:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, 3, height), color)
            painter.fillRect(QRect(8, 5, width - 4, height - 1), fill_brush)
        elif position == self.CenterRight:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(width + 1, 5, 3, height - 1), color)
            painter.fillRect(QRect(5, 5, width - 4, height - 1), fill_brush)
        elif position == self.SplitTop:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            painter.fillRect(QRect(5, 8, width - 1, height / 2 - 2), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            painter.setPen(pen)
            painter.drawLine(5, 8 + height / 2 - 3, 5 + width - 1, 8 + height / 2 - 3)
        elif position == self.SplitBottom:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            h = height / 2 - 2
            painter.fillRect(QRect(5, 8 + h, width - 1, h), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            painter.setPen(pen)
            painter.drawLine(5, 8 + height / 2 - 2, 5 + width - 1, 8 + height / 2 - 2)
        elif position == self.SplitLeft:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            w = width / 2
            h = height - 4
            painter.fillRect(QRect(5, 8, w - 1, h), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            pen.setDashOffset(1)
            painter.setPen(pen)
            painter.drawLine(3 + w, 8, 3 + w, 8 + h)
        elif position == self.SplitRight:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            w = width / 2
            h = height - 4
            painter.fillRect(QRect(5 + w, 8, w - 1, h), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            pen.setDashOffset(1)
            painter.setPen(pen)
            painter.drawLine(5 + w, 8, 5 + w, 8 + h)
        elif position == self.SplitHorizontal:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            w = width / 4
            h = height - 4
            painter.fillRect(QRect(6 + w, 8, 2 * w - 1, h), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            pen.setDashOffset(1)
            painter.setPen(pen)
            painter.drawLine(6 + w, 8, 6 + w, 8 + h)
            painter.drawLine(4 + 3 * w, 8, 4 + 3 * w, 8 + h)
        elif position == self.SplitVertical:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            h = height / 4
            painter.fillRect(QRect(5, 8 + h, width - 1, 2 * h - 2), fill_brush)
            pen = QPen(color, 0, Qt.DotLine)
            pen.setDashPattern([1, 1])
            painter.setPen(pen)
            painter.drawLine(5, 8 + h, 4 + width, 8 + h)
            painter.drawLine(5, 10 + 2 * h, 4 + width, 10 + 2 * h)
        # Draw the indicator
        painter.restore()


def render_cross(painter):
    path = QPainterPath()
    path.moveTo(35.0, 0)
    path.lineTo(75.0, 0)
    path.lineTo(75.0, 25.0)
    path.lineTo(85.0, 35.0)
    path.lineTo(110.0, 35.0)
    path.lineTo(110.0, 75.0)
    path.lineTo(85.0, 75.0)
    path.lineTo(75.0, 85.0)
    path.lineTo(75.0, 110.0)
    path.lineTo(35.0, 110.0)
    path.lineTo(35.0, 85.0)
    path.lineTo(25.0, 75.0)
    path.lineTo(0.0, 75.0)
    path.lineTo(0.0, 35.0)
    path.lineTo(25.0, 35.0)
    path.lineTo(35.0, 25.0)
    path.lineTo(35.0, 0.0)
    painter.fillPath(path, QColor(0xFF, 0xFF, 0xFF, 0x99))
    painter.setPen(QPen(QColor(0x77, 0x77, 0x77), 1.0))
    painter.drawPath(path)


def render_cross_ex(painter):
    path = QPainterPath()
    path.moveTo(49.0, 0)
    path.lineTo(89.0, 0)
    path.lineTo(89.0, 39.0)
    path.lineTo(99.0, 49.0)
    path.lineTo(138.0, 49.0)
    path.lineTo(138.0, 89.0)
    path.lineTo(99.0, 89.0)
    path.lineTo(89.0, 99.0)
    path.lineTo(89.0, 138.0)
    path.lineTo(49.0, 138.0)
    path.lineTo(49.0, 99.0)
    path.lineTo(39.0, 89.0)
    path.lineTo(0.0, 89.0)
    path.lineTo(0.0, 49.0)
    path.lineTo(39.0, 49.0)
    path.lineTo(49.0, 39.0)
    path.lineTo(49.0, 0.0)
    painter.fillPath(path, QColor(0xFF, 0xFF, 0xFF, 0x99))
    painter.setPen(QPen(QColor(0x77, 0x77, 0x77), 1.0))
    painter.drawPath(path)


def render_north_cross(painter):
    path = QPainterPath()
    path.moveTo(35.0, 0)
    path.lineTo(75.0, 0)
    path.lineTo(75.0, 25.0)
    path.lineTo(85.0, 35.0)
    path.lineTo(110.0, 35.0)
    path.lineTo(110.0, 75.0)
    path.lineTo(85.0, 75.0)
    path.lineTo(75.0, 85.0)
    path.lineTo(75.0, 110.0)
    path.lineTo(35.0, 110.0)
    path.lineTo(35.0, 85.0)
    path.lineTo(25.0, 75.0)
    path.lineTo(0.0, 75.0)
    path.lineTo(0.0, 35.0)
    path.lineTo(25.0, 35.0)
    path.lineTo(35.0, 25.0)
    path.lineTo(35.0, 0.0)
    painter.fillPath(path, QColor(0xFF, 0xFF, 0xFF, 0x99))
    painter.setPen(QPen(QColor(0x77, 0x77, 0x77), 1.0))
    painter.drawPath(path)


def render_box(painter):
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    path.lineTo(40.0, 0.0)
    path.lineTo(40.0, 40.0)
    path.lineTo(0.0, 40.0)
    path.lineTo(0.0, 0.0)
    painter.fillPath(path, QColor(0xFF, 0xFF, 0xFF, 0x99))
    painter.setPen(QPen(QColor(0x77, 0x77, 0x77), 1.0))
    painter.drawPath(path)


def render_vbar(painter):
    path = QPainterPath()
    rect = QRectF(0, 0, 9, 30)
    path.addRoundedRect(rect, 2.0, 2.0)
    grad = QLinearGradient(0.0, 0.0, 0.0, 1.0)
    grad.setCoordinateMode(QGradient.ObjectBoundingMode)
    grad.setColorAt(0.0, QColor(0xF5, 0xF8, 0xFB))
    grad.setColorAt(0.33, QColor(0xF0, 0xF3, 0xF6))
    grad.setColorAt(0.66, QColor(0xE5, 0xE8, 0xEE))
    grad.setColorAt(1.0, QColor(0xDE, 0xE2, 0xE9))
    brush = QBrush(grad)
    pen = QPen(QColor(0x8A, 0x91, 0x9C))

    painter.fillPath(path, brush)
    painter.setPen(pen)
    painter.drawPath(path)

    color = QColor(0x44, 0x58, 0x79)
    painter.fillRect(QRect(4, 4, 2, 23), color)


def render_hbar(painter):
    path = QPainterPath()
    rect = QRectF(0, 0, 30, 9)
    path.addRoundedRect(rect, 2.0, 2.0)
    grad = QLinearGradient(0.0, 0.0, 0.0, 1.0)
    grad.setCoordinateMode(QGradient.ObjectBoundingMode)
    grad.setColorAt(0.0, QColor(0xF5, 0xF8, 0xFB))
    grad.setColorAt(0.33, QColor(0xF0, 0xF3, 0xF6))
    grad.setColorAt(0.66, QColor(0xE5, 0xE8, 0xEE))
    grad.setColorAt(1.0, QColor(0xDE, 0xE2, 0xE9))
    brush = QBrush(grad)
    pen = QPen(QColor(0x8A, 0x91, 0x9C))

    painter.fillPath(path, brush)
    painter.setPen(pen)
    painter.drawPath(path)

    color = QColor(0x44, 0x58, 0x79)
    painter.setPen(color)
    painter.fillRect(QRect(4, 4, 23, 2), color)


def render_background(painter):
    brush = QBrush(QColor(0x00, 0x00, 0x00, 0x10), Qt.Dense6Pattern)
    painter.fillRect(QRect(0, 0, 129, 129), brush)
    brush = QBrush(QColor(0xFF, 0xFF, 0xFF, 0x10), Qt.Dense6Pattern)
    painter.translate(0, 1)
    painter.fillRect(QRect(0, 0, 129, 129), brush)


app = QApplication([])
image = QImage(QSize(128, 128), QImage.Format_ARGB32_Premultiplied)
image.fill(0)
painter = QPainter(image)
#render_box(painter)
#render_cross(painter)
#render_cross_ex(painter)
#render_vbar(painter)
#render_hbar(painter)
render_background(painter)
#pad = GuidePad(QRect(0, 0, 30, 30), GuidePad.CenterQuads)
#pad.paint(painter)
painter.end()

import os
path = os.path.join(os.path.dirname(__file__), 'background.png')
image.save(path)
