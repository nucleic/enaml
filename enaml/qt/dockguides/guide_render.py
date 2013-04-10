""" An extremely hack script that was used to render the dock guide icons.

"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def timer(f):
    import time
    def c(*a):
        t = time.clock()
        r = f(*a)
        print time.clock() - t
        return r
    return c


class GuidePad(object):

    LeftPosition = 0

    TopPosition = 1

    RightPosition = 2

    BottomPosition = 3

    CenterPosition = 4

    SplitLeft = 5

    SplitTop = 6

    SplitRight = 7

    SplitBottom = 8

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
        elif position == self.CenterPosition:
            width = rect.width() - 8
            height = rect.height() - 8
            painter.drawRect(QRect(4, 4, width, height))
            painter.fillRect(QRect(5, 5, width - 1, 3), color)
            painter.fillRect(QRect(5, 8, width - 1, height - 4), fill_brush)
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

        # Draw the indicator
        painter.restore()


class QDiamondGuide(QFrame):

    def __init__(self, parent=None, pad_size=30):
        super(QDiamondGuide, self).__init__(parent)
        self._pad_size = 30
        self._pads = [GuidePad(QRect()) for _ in xrange(9)]
        self.setMouseTracking(True)

        pads = self._pads
        pads[0].setGuidePosition(GuidePad.LeftPosition)
        pads[1].setGuidePosition(GuidePad.TopPosition)
        pads[2].setGuidePosition(GuidePad.RightPosition)
        pads[3].setGuidePosition(GuidePad.BottomPosition)
        pads[4].setGuidePosition(GuidePad.CenterPosition)
        pads[5].setGuidePosition(GuidePad.LeftPosition)
        pads[6].setGuidePosition(GuidePad.TopPosition)
        pads[7].setGuidePosition(GuidePad.RightPosition)
        pads[8].setGuidePosition(GuidePad.BottomPosition)

    def hover(self, pos):
        for pad in self._pads:
            o = pad.opacity()
            if pad.contains(pos):
                if o != 1.0:
                    pad.setOpacity(1.0)
                    self.update(pad.rect())
            elif o != 0.8:
                pad.setOpacity(0.8)
                self.update(pad.rect())

    def resizeEvent(self, event):
        size = self._pad_size
        cx = self.width() / 2
        cy = self.height() / 2
        hs = size / 2

        # left
        r1 = QRect(cx - hs - 5 - size, cy - hs, size, size)

        # top
        r2 = QRect(cx - hs, cy - hs - 5 - size, size, size)

        # right
        r3 = QRect(cx + hs + 5, cy - hs, size, size)

        # bottom
        r4 = QRect(cx - hs, cy + hs + 5, size, size)

        # center
        r5 = QRect(cx - hs, cy - hs, size, size)

        # left border
        r6 = QRect(10, cy - hs, size, size)

        # top border
        r7 = QRect(cx - hs, 10, size, size)

        # right border
        r8 = QRect(cx * 2 - 10 - size, cy - hs, size, size)

        # bottom border
        r9 = QRect(cx - hs, cy * 2 - 10 - size, size, size)

        rects = (r1, r2, r3, r4, r5, r6, r7, r8, r9)
        for rect, pad in zip(rects, self._pads):
            pad.setRect(rect)

    def mouseMoveEvent(self, event):
        self.hover(event.pos())

    @timer
    def paintEvent(self, event):
        super(QDiamondGuide, self).paintEvent(event)
        painter = QPainter(self)
        rect = event.rect()
        for pad in self._pads:
            if pad.intersects(rect):
                pad.paint(painter)



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


app = QApplication([])
image = QImage(QSize(121, 121), QImage.Format_ARGB32_Premultiplied)
image.fill(0)
painter = QPainter(image)
#render_box(painter)
render_cross(painter)
painter.end()
#image.save()
