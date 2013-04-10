#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from PyQt4.QtCore import Qt, QRect, QPoint
from PyQt4.QtGui import QFrame, QImage, QPainter, QPixmap, QColor

from atom.api import Atom, Float, Typed, Enum


LOW_ALPHA = 0.60

FULL_ALPHA = 1.0


ImageKind = Enum(
    'top', 'left', 'right', 'bottom', 'center',
    'split_top', 'split_left', 'split_right', 'split_bottom'
)


class ImageLoader(object):

    _images = {}

    @classmethod
    def load(cls, kind):
        img = cls._images.get(kind)
        if img is None:
            d = os.path.dirname(__file__)
            img = QImage(os.path.join(d, 'dockguides', kind + '.png'))
            cls._images[kind] = img
        return img


class GuideImage(Atom):

    image = Typed(QImage, factory=lambda: QImage())

    rect = Typed(QRect, factory=lambda: QRect())

    opacity = Float(LOW_ALPHA)

    def paint(self, painter, point=None):
        image = self.image
        rect = self.rect
        point = point or rect.topLeft()
        if image.isNull() or point.isNull():
            return
        painter.save()
        painter.setOpacity(self.opacity)
        painter.drawImage(point, image)
        painter.restore()

import time
def timer(f):
    def c(*a):
        t = time.time()
        r = f(*a)
        print time.time() - t
        return r
    return c

class QDockGuides(QFrame):

    def __init__(self):
        super(QDockGuides, self).__init__()
        self.setAttribute(Qt.WA_MacNoShadow, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        flags = Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self._guide_center = QPoint()

        make = lambda kind: GuideImage(image=ImageLoader.load(kind))
        self._g_top = make('top')
        self._g_left = make('left')
        self._g_right = make('right')
        self._g_bottom = make('bottom')
        self._g_box = make('box')
        self._cg_top = make('top')
        self._cg_left = make('left')
        self._cg_right = make('right')
        self._cg_bottom = make('bottom')
        self._cg_center = make('center')
        self._cg_cross = make('cross')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _layoutGuides(self):
        # Target Guide Compass
        # FIXME hard-coded image dimensions. This is not so bad because
        # changing the icons will inevitable require a new layout.
        # Cross Box == 110 x 110
        # Guide Btn ==  30 x 30
        cpx = self._guide_center.x()
        cpy = self._guide_center.y()
        self._cg_top.rect = QRect(cpx - 15, cpy - 50, 30, 30)
        self._cg_left.rect = QRect(cpx - 50, cpy - 15, 30, 30)
        self._cg_right.rect = QRect(cpx + 20, cpy - 15, 30, 30)
        self._cg_bottom.rect = QRect(cpx - 15, cpy + 20, 30, 30)
        self._cg_center.rect = QRect(cpx - 15, cpy - 15, 30, 30)
        self._cg_cross.rect = QRect(cpx - 55, cpy - 55, 110, 110)

        # Border Guide Buttons
        # FIXME hard-coded image dimensions. This is not so bad because
        # changing custom guides will inevitably require a subclass.
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        self._g_top.rect = QRect(cx - 15, 15, 30, 30)
        self._g_left.rect = QRect(15, cy - 15, 30, 30)
        self._g_right.rect = QRect(w - 45, cy - 15, 30, 30)
        self._g_bottom.rect = QRect(cx - 15, h - 45, 30, 30)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def guideCenter(self):
        return self._guide_center

    def setGuideCenter(self, pos):
        if pos != self._guide_center:
            self._guide_center = pos
            self._layoutGuides()
            self.update()

    def hover(self, pos):
        pads = ('_g_top', '_g_left', '_g_right', '_g_bottom', '_cg_top',
                '_cg_left', '_cg_right', '_cg_bottom', '_cg_center')
        for p in pads:
            pad = getattr(self, p)
            if pad.rect.contains(pos):
                if pad.opacity != FULL_ALPHA:
                    pad.opacity = FULL_ALPHA
                    self.update(pad.rect)
            elif pad.opacity != LOW_ALPHA:
                pad.opacity = LOW_ALPHA
                self.update(pad.rect)

    def resizeEvent(self, event):
        self._layoutGuides()

    def paintEvent(self, event):
        super(QDockGuides, self).paintEvent(event)
        rect = event.rect()
        painter = QPainter(self)
        if not self._guide_center.isNull():
            if self._cg_cross.rect.intersects(rect):
                self._cg_cross.paint(painter)
                self._cg_top.paint(painter)
                self._cg_left.paint(painter)
                self._cg_right.paint(painter)
                self._cg_bottom.paint(painter)
                self._cg_center.paint(painter)
            else:
                if self._cg_top.rect.intersects(rect):
                    self._cg_top.paint(painter)
                if self._cg_left.rect.intersects(rect):
                    self._cg_left.paint(painter)
                if self._cg_right.rect.intersects(rect):
                    self._cg_right.paint(painter)
                if self._cg_bottom.rect.intersects(rect):
                    self._cg_bottom.paint(painter)
                if self._cg_center.rect.intersects(rect):
                    self._cg_center.paint(painter)
        p = QPoint(5, 5)
        if self._g_top.rect.intersects(rect):
            self._g_box.paint(painter, self._g_top.rect.topLeft() - p)
            self._g_top.paint(painter)
        if self._g_left.rect.intersects(rect):
            self._g_box.paint(painter, self._g_left.rect.topLeft() - p)
            self._g_left.paint(painter)
        if self._g_right.rect.intersects(rect):
            self._g_box.paint(painter, self._g_right.rect.topLeft() - p)
            self._g_right.paint(painter)
        if self._g_bottom.rect.intersects(rect):
            self._g_box.paint(painter, self._g_bottom.rect.topLeft() - p)
            self._g_bottom.paint(painter)
