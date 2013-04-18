#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys

from PyQt4.QtCore import Qt, QRect, QPoint
from PyQt4.QtGui import QFrame, QImage, QPainter

from atom.api import Atom, Float, Typed


#: The default alpha value for guide transparency.
LOW_ALPHA = 0.60

#: The default alpha value for no guide transparency.
FULL_ALPHA = 1.0


_images = {}
def load_image(name):
    """ Load the guide image for the given name into a QImage.

    This function is hard-coded to return the named .png image from
    the ./dockguides directory located alongside this file. It is not
    a generic image loading routine.

    """
    img = _images.get(name)
    if img is None:
        dirname = os.path.dirname(__file__)
        img = QImage(os.path.join(dirname, 'dockguides', name + '.png'))
        _images[name] = img
    return img


class GuideImage(Atom):
    """ A class which manages a guide image in a dock rose.

    """
    #: The QImage to use when painting the guide.
    image = Typed(QImage, factory=lambda: QImage())

    #: The QRect specifying where to draw the image.
    rect = Typed(QRect, factory=lambda: QRect())

    #: The opacity to use when drawing the image.
    opacity = Float(LOW_ALPHA)

    def pos(self):
        """ Get the position of the image.

        Returns
        -------
        result : QPoint
            The point representing the top-left corner of the image.

        """
        return self.rect.topLeft()

    def contains(self, point):
        """ Test whether the image contains a point.

        Parameters
        ----------
        rect : QPoint
            The rect to test for containment.

        Returns
        -------
        result : bool
            True if the image contains the point, False otherwise.

        """
        return self.rect.contains(point)

    def intersects(self, rect):
        """ Test whether the image intersects a rectangle.

        Parameters
        ----------
        rect : QRect
            The rect to test for intersection.

        Returns
        -------
        result : bool
            True if the image intersects the rect, False otherwise.

        """
        return self.rect.intersects(rect)

    def paint(self, painter):
        """ Paint the image using the given painter.

        Parameters
        ----------
        painter : QPainter
            An active QPainter to use for drawing the image. If the
            image is a null image, painting will be skipped.

        """
        image = self.image
        if image.isNull():
            return
        painter.save()
        painter.setOpacity(self.opacity)
        painter.drawImage(self.rect, image)
        painter.restore()


class QGuideRose(QFrame):
    """ A custom QFrame which implements a rose of docking guides.

    This widget must always be used as an independent top-level window.
    The dock area which uses the rose should manually set the geometry
    of the widget before showing it. The rose has a variety of guides:

    - Border Guides
        These are guides which stick to the top, left, right and
        bottom of the widget boundary with an offset of 10px. The
        locations of these guides are not adjustable.

    - Compass Guides
        These are five guides arranged in a compass. The center of
        the compass can be adjusted via the 'setRoseCenter' method.
        The compass guide is (de)activated via 'setRoseMode'.

    - Splitter Guides
        These are horizontal and vertical guides which can be used
        to indicate a hover over a splitter handle. The center of
        the guides can be adjusted via the 'setRoseCenter' method.
        The splitter guides are (de)activated via 'setRoseMode'.

    """
    class Mode(object):
        """ An enum class for defining the rose mode.

        """
        #: No guides will be active.
        NoMode = 0

        #: The compass rose and border guides will be active.
        Compass = 1

        #: The vertical split and border guides will be active.
        SplitVertical = 2

        #: The horizontal split and border guides will be active.
        SplitHorizontal = 3

        #: Only a single guide in the center will be active.
        SingleCenter = 4

        #: Only the compass rose will be active.
        CompassOnly = 5

        #: Only show the border guides will be active.
        BorderOnly = 6

    class Guide(object):
        """ An enum class for identifying guide locations.

        """
        #: The north border guide.
        BorderNorth = 0

        #: The east border guide.
        BorderEast = 1

        #: The south border guide.
        BorderSouth = 2

        #: The west border guide.
        BorderWest = 3

        #: The north compass guide.
        CompassNorth = 4

        #: The east compass guide.
        CompassEast = 5

        #: The south compass guide.
        CompassSouth = 6

        #: The west compass guide.
        CompassWest = 7

        #: The center compass guide.
        CompassCenter = 8

        #: The vertical split guide.
        SplitVertical = 9

        #: The horizontal split guide.
        SplitHorizontal = 10

        #: The single center guide.
        SingleCenter = 11

        #: The compass cross. (internal use only)
        CompassCross = 12

        #: No relevant guide.
        NoGuide = 13

    def __init__(self):
        """ Initialize a QGuideRose.

        """
        super(QGuideRose, self).__init__()

        # On Mac, setting the translucent background does not cause the
        # frame shadow to be hidden; it must be explicitly hidden.
        if sys.platform == 'darwin':
            self.setAttribute(Qt.WA_MacNoShadow, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # Window must be a tool tip to be raised above a QRubberBand on OSX
        flags = Qt.ToolTip | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        self.setWindowFlags(flags)

        # Setup the default rose modes and load the guide images.
        self._center = QPoint()
        self._mode = QGuideRose.Mode.NoMode
        self._last = QGuideRose.Guide.NoGuide
        make = lambda name: GuideImage(image=load_image(name))
        self._guides = [
            make('top'),                # BorderNorth
            make('right'),              # BorderEast
            make('bottom'),             # BorderSouth
            make('left'),               # BorderWest
            make('top'),                # CompassNorth
            make('right'),              # CompassEast
            make('bottom'),             # CompassSouth
            make('left'),               # CompassWest
            make('center'),             # CompassCenter
            make('split_vertical'),     # SplitVertical
            make('split_horizontal'),   # SplitHorizontal
            make('center'),             # SingleCenter
        ]
        self._boxes = [
            make('box'),                # BorderNorth
            make('box'),                # BorderEast
            make('box'),                # BorderSouth
            make('box'),                # BorderWest
            None,                       # CompassNorth
            None,                       # CompassEast
            None,                       # CompassSouth
            None,                       # CompassWest
            None,                       # CompassCenter
            make('box'),                # SplitVertical
            make('box'),                # SplitHorizontal
            make('box'),                # SingleCenter
            make('cross'),              # CompassCross
        ]

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _layoutGuides(self):
        """ Layout the guides based on the current widget geometry.

        """
        boxes = self._boxes
        guides = self._guides
        Guide = QGuideRose.Guide

        # Rose Guide Compass
        # FIXME hard-coded image dimensions. This is not so bad because
        # changing the icons will inevitable require a new layout.
        # Cross Box == 111 x 111
        # Guide Btn ==  31 x 31
        cpx = self._center.x()
        cpy = self._center.y()
        guides[Guide.CompassNorth].rect = QRect(cpx - 15, cpy - 50, 31, 31)
        guides[Guide.CompassEast].rect = QRect(cpx + 20, cpy - 15, 31, 31)
        guides[Guide.CompassSouth].rect = QRect(cpx - 15, cpy + 20, 31, 31)
        guides[Guide.CompassWest].rect = QRect(cpx - 50, cpy - 15, 31, 31)
        guides[Guide.CompassCenter].rect = QRect(cpx - 15, cpy - 15, 31, 31)
        boxes[Guide.CompassCross].rect = QRect(cpx - 55, cpy - 55, 111, 111)

        # Splitter Guides
        # FIXME hard-coded image dimensions. This is not so bad because
        # changing the icons will inevitable require a new layout.
        # Guide Box == 41 x 41
        # Guide Btn == 31 x 31
        guides[Guide.SplitHorizontal].rect = QRect(cpx - 15, cpy - 15, 31, 31)
        boxes[Guide.SplitHorizontal].rect = QRect(cpx - 20, cpy - 20, 41, 41)
        guides[Guide.SplitVertical].rect = QRect(cpx - 15, cpy - 15, 31, 31)
        boxes[Guide.SplitVertical].rect = QRect(cpx - 20, cpy - 20, 41, 41)

        # Border Guide Buttons
        # FIXME hard-coded image dimensions. This is not so bad because
        # changing custom guides will inevitably require a subclass.
        # Guide Box == 41 x 41
        # Guide Btn == 31 x 31
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        guides[Guide.BorderNorth].rect = QRect(cx - 15, 15, 31, 31)
        boxes[Guide.BorderNorth].rect = QRect(cx - 20, 10, 41, 41)
        guides[Guide.BorderEast].rect = QRect(w - 45, cy - 15, 31, 31)
        boxes[Guide.BorderEast].rect = QRect(w - 50, cy - 20, 41, 41)
        guides[Guide.BorderSouth].rect = QRect(cx - 15, h - 45, 31, 31)
        boxes[Guide.BorderSouth].rect = QRect(cx - 20, h - 50, 41, 41)
        guides[Guide.BorderWest].rect = QRect(15, cy - 15, 31, 31)
        boxes[Guide.BorderWest].rect = QRect(10, cy - 20, 41, 41)

        # Single Center Guide
        guides[Guide.SingleCenter].rect = QRect(cpx - 15, cpy - 15, 31, 31)
        boxes[Guide.SingleCenter].rect = QRect(cpx - 20, cpy - 20, 41, 41)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def center(self):
        """ Get the location of the rose center.

        Returns
        -------
        result : QPoint
            The location that will be used as the center of the portion
            of the rose with a configurable location.

        """
        return self._center

    def setCenter(self, pos):
        """ Set the location of the rose center.

        Parameters
        ----------
        pos : QPoint
            The location that will be used as the center of the portion
            of the rose with a configurable location.

        """
        if pos != self._center:
            self._center = pos
            self._layoutGuides()
            self.update()

    def mode(self):
        """ Get the mode of the guide rose.

        Returns
        -------
        result : QGuideRose.Mode
            The mode used when rendering the center of the guide.

        """
        return self._mode

    def setMode(self, mode):
        """ Set the mode of the guide rose.

        Returns
        -------
        result : QGuideRose.Mode
            The mode to use when rendering the center of the guide.

        """
        if mode != self._mode:
            self._mode = mode
            self.update()

    def mouseOver(self, pos):
        """ Update the state of the rose based on the mouse position.

        Parameters
        ----------
        pos : QPoint
            The position of the mouse expressed in local coordinates.

        """
        Guide = QGuideRose.Guide
        target = self.guideAt(pos, self._mode)
        last = self._last
        if last != target:
            self._last = target
            if last != Guide.NoGuide:
                self._guides[last].opacity = LOW_ALPHA
            if target != Guide.NoGuide:
                self._guides[target].opacity = FULL_ALPHA
        self.update()

    def guideAt(self, pos, mode):
        """ Get the guide enum for a given position.

        Parameters
        ----------
        pos : QPoint
            The position of interest, expressed local coordinates.

        mode : QGuideRose.Mode
            The mode to use for hit testing.

        Returns
        -------
        result : QGuideRose.Guide
            The enum value for the guide under the mouse position.

        """
        guides = self._guides
        Mode = QGuideRose.Mode
        Guide = QGuideRose.Guide
        if mode == Mode.SingleCenter:
            if guides[Guide.SingleCenter].contains(pos):
                return Guide.SingleCenter
        elif mode == Mode.Compass or mode == Mode.CompassOnly:
            if guides[Guide.CompassNorth].contains(pos):
                return Guide.CompassNorth
            if guides[Guide.CompassEast].contains(pos):
                return Guide.CompassEast
            if guides[Guide.CompassSouth].contains(pos):
                return Guide.CompassSouth
            if guides[Guide.CompassWest].contains(pos):
                return Guide.CompassWest
            if guides[Guide.CompassCenter].contains(pos):
                return Guide.CompassCenter
            if mode == Mode.CompassOnly:
                return Guide.NoGuide
        elif mode == Mode.SplitHorizontal:
            if guides[Guide.SplitHorizontal].contains(pos):
                return Guide.SplitHorizontal
        elif mode == Mode.SplitVertical:
            if guides[Guide.SplitVertical].contains(pos):
                return Guide.SplitVertical
        if guides[Guide.BorderNorth].contains(pos):
            return Guide.BorderNorth
        if guides[Guide.BorderEast].contains(pos):
            return Guide.BorderEast
        if guides[Guide.BorderSouth].contains(pos):
            return Guide.BorderSouth
        if guides[Guide.BorderWest].contains(pos):
            return Guide.BorderWest
        return Guide.NoGuide

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def resizeEvent(self, event):
        """ Handle the resize event for the rose.

        This handle will relayout the guides on a resize.

        """
        self._layoutGuides()

    def paintCompass(self, painter):
        """ Paint the compass for the rose.

        """
        boxes = self._boxes
        guides = self._guides
        Guide = QGuideRose.Guide
        boxes[Guide.CompassCross].paint(painter)
        guides[Guide.CompassNorth].paint(painter)
        guides[Guide.CompassEast].paint(painter)
        guides[Guide.CompassSouth].paint(painter)
        guides[Guide.CompassWest].paint(painter)
        guides[Guide.CompassCenter].paint(painter)

    def paintBorders(self, painter):
        """ Paint the border guides for the rose.

        """
        boxes = self._boxes
        guides = self._guides
        Guide = QGuideRose.Guide
        boxes[Guide.BorderNorth].paint(painter)
        guides[Guide.BorderNorth].paint(painter)
        boxes[Guide.BorderEast].paint(painter)
        guides[Guide.BorderEast].paint(painter)
        boxes[Guide.BorderSouth].paint(painter)
        guides[Guide.BorderSouth].paint(painter)
        boxes[Guide.BorderWest].paint(painter)
        guides[Guide.BorderWest].paint(painter)

    def paintEvent(self, event):
        """ Handle the paint event for the rose.

        This handler will redraw all of the guides for the rose.

        """
        # Attempting to paint only the invalid rects ends up being a
        # fruitless endeavor (at least on Windows). There appears to
        # be a subtle bug in the transparent window compositing that
        # randomly clips 1px from the edges of guides. This is not a
        # huge issue since this paint event only blits images and is
        # therefore relatively cheap.
        super(QGuideRose, self).paintEvent(event)
        painter = QPainter(self)
        mode = self._mode
        boxes = self._boxes
        guides = self._guides
        Mode = QGuideRose.Mode
        Guide = QGuideRose.Guide
        if mode == Mode.SingleCenter:
            boxes[Guide.SingleCenter].paint(painter)
            guides[Guide.SingleCenter].paint(painter)
        elif mode == Mode.Compass:
            self.paintCompass(painter)
            self.paintBorders(painter)
        elif mode == Mode.CompassOnly:
            self.paintCompass(painter)
        elif mode == Mode.SplitHorizontal:
            boxes[Guide.SplitHorizontal].paint(painter)
            guides[Guide.SplitHorizontal].paint(painter)
            self.paintBorders(painter)
        elif mode == Mode.SplitVertical:
            boxes[Guide.SplitVertical].paint(painter)
            guides[Guide.SplitVertical].paint(painter)
            self.paintBorders(painter)
        elif mode == Mode.BorderOnly:
            self.paintBorders(painter)
