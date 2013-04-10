#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from PyQt4.QtCore import QRect, QPoint
from PyQt4.QtGui import QFrame, QImage, QPainter

from atom.api import Atom, Float, Typed


LOW_ALPHA = 0.75

FULL_ALPHA = 1.0


class GuideButton(Atom):

    image = Typed(QImage)

    rect = Typed(QRect, factory=lambda: QRect())

    opacity = Float(LOW_ALPHA)

    def contains(self, pos):
        return self.rect.contains(pos)

    def intersects(self, rect):
        return self.rect.intersects(rect)

    def paint(self, painter):
        image = self.image
        if image is None or image.isNull():
            return
        painter.save()
        painter.setOpacity(self.opacity)
        painter.drawImage(self.rect.topLeft(), image)
        painter.restore()


import time
def timer(f):
    def c(*a):
        t = time.clock()
        r = f(*a)
        print time.clock() - t
        return r
    return c


class QDockGuides(QFrame):

    def __init__(self, parent=None):
        super(QDockGuides, self).__init__(parent)
        self.setMouseTracking(True)
        d = os.path.dirname(__file__)
        j = lambda s: os.path.join(d, 'dockguides', s + '.png')
        self._left_img = QImage(j('left'))
        self._right_img = QImage(j('right'))
        self._top_img = QImage(j('top'))
        self._bottom_img = QImage(j('bottom'))
        self._center_img = QImage(j('center'))
        self._split_left_img = QImage(j('split_left'))
        self._split_right_img = QImage(j('split_right'))
        self._split_top_img = QImage(j('split_top'))
        self._split_bottom_img = QImage(j('split_bottom'))
        self._cross = QImage(j('cross'))
        self._box = QImage(j('box'))

        pads = self._pads = []
        a = lambda img: pads.append(GuideButton(image=img))
        a(self._left_img)
        a(self._top_img)
        a(self._right_img)
        a(self._bottom_img)
        a(self._center_img)
        a(self._left_img)
        a(self._top_img)
        a(self._right_img)
        a(self._bottom_img)

    def hover(self, pos):
        for pad in self._pads:
            o = pad.opacity
            if pad.contains(pos):
                if o != FULL_ALPHA:
                    pad.opacity = FULL_ALPHA
                    self.update(pad.rect)
            elif o != LOW_ALPHA:
                pad.opacity = LOW_ALPHA
                self.update(pad.rect)

    def resizeEvent(self, event):
        size = self._left_img.width()
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
            pad.rect = rect

    def mouseMoveEvent(self, event):
        self.hover(event.pos())

    #@timer
    def paintEvent(self, event):
        super(QDockGuides, self).paintEvent(event)
        pos = QPoint(self.width() / 2 - 55, self.height() / 2 - 55)
        painter = QPainter(self)
        painter.drawImage(pos, self._cross)
        rect = event.rect()
        for idx, pad in enumerate(self._pads):
            if pad.intersects(rect):
                if idx > 4:
                    r = pad.rect
                    x = r.x() - 5
                    y = r.y() - 5
                    painter.drawImage(QPoint(x, y), self._box)
                pad.paint(painter)
