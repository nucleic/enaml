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

from atom.api import Atom, Float, Typed, Value


#: The default alpha value for guide transparency.
LOW_ALPHA = 0.60


#: The default alpha value for no guide transparency.
FULL_ALPHA = 1.0


#: A cache of QImage instances for the loaded guide images.
_images = {}


def load_image(name):
    """ Load the guide image for the given name into a QImage.

    This function is hard-coded to return the named .png image from
    the ./dockguides directory located alongside this file. It is not
    a generic image loading routine.

    """
    image = _images.get(name)
    if image is None:
        dirname = os.path.dirname(__file__)
        image = QImage(os.path.join(dirname, 'dockguides', name + '.png'))
        _images[name] = image
    return image


class Guide(object):
    """ An enum class for identifying guide locations.

    """
    #: No relevant guide.
    NoGuide = 0

    #: The north border guide.
    BorderNorth = 1

    #: The east border guide.
    BorderEast = 2

    #: The south border guide.
    BorderSouth = 3

    #: The west border guide.
    BorderWest = 4

    #: The north compass guide.
    CompassNorth = 5

    #: The east compass guide.
    CompassEast = 6

    #: The south compass guide.
    CompassSouth = 7

    #: The west compass guide.
    CompassWest = 8

    #: The center compass north guide.
    CompassCenterNorth = 9

    #: The center compass east guide.
    CompassCenterEast = 10

    #: The center compass south guide.
    CompassCenterSouth = 11

    #: The center compass west guide.
    CompassCenterWest = 12

    #: The vertical split guide.
    SplitVertical = 13

    #: The horizontal split guide.
    SplitHorizontal = 14

    #: The single center guide.
    SingleCenter = 15


class GuideMode(object):
    """ An enum class for defining the guide mode for a guide rose.

    These modes can be or'd together to dictate which guides are
    activated and painted on the screen.

    """
    #: Nothing will be shown.
    NoMode = 0x0

    #: Show the border guides.
    Border = 0x1

    #: Show the central compass.
    Compass = 0x2

    #: Show the horizontal split guide.
    SplitHorizontal = 0x4

    #: Show the vertical split guide.
    SplitVertical = 0x8

    #: Show the single center guide.
    SingleCenter = 0x10


class GuideImage(Atom):
    """ A class which manages the painting of a guide image.

    """
    #: The QImage to use when painting the guide.
    image = Typed(QImage, factory=lambda: QImage())

    #: The QRect specifying where to draw the image.
    rect = Typed(QRect, factory=lambda: QRect())

    #: The opacity to use when drawing the image.
    opacity = Float(LOW_ALPHA)

    def __init__(self, name):
        """ Initialize a GuideImage.

        Parameters
        ----------
        name : str
            The name of the image to load for the guide.

        """
        self.image = load_image(name)

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


class BorderGuides(Atom):
    """ A class which renders the border guides for the guide rose.

    """
    _guides = Value(factory=lambda: {
        Guide.BorderNorth: GuideImage('top'),
        Guide.BorderEast: GuideImage('right'),
        Guide.BorderSouth: GuideImage('bottom'),
        Guide.BorderWest: GuideImage('left'),
    })

    _boxes = Value(factory=lambda: {
        Guide.BorderNorth: GuideImage('box'),
        Guide.BorderEast: GuideImage('box'),
        Guide.BorderSouth: GuideImage('box'),
        Guide.BorderWest: GuideImage('box'),
    })

    _last = Value()

    def layout(self, rect):
        """ Layout the guides for the given rect.

        Parameters
        ----------
        rect : QRect
            The rectangle in which to layout the border guides.

        """
        boxes = self._boxes
        guides = self._guides
        w = rect.width()
        h = rect.height()
        cx = rect.left() + w / 2
        cy = rect.top() + h / 2
        guides[Guide.BorderNorth].rect = QRect(cx - 15, 15, 31, 31)
        boxes[Guide.BorderNorth].rect = QRect(cx - 20, 10, 41, 41)
        guides[Guide.BorderEast].rect = QRect(w - 45, cy - 15, 31, 31)
        boxes[Guide.BorderEast].rect = QRect(w - 50, cy - 20, 41, 41)
        guides[Guide.BorderSouth].rect = QRect(cx - 15, h - 45, 31, 31)
        boxes[Guide.BorderSouth].rect = QRect(cx - 20, h - 50, 41, 41)
        guides[Guide.BorderWest].rect = QRect(15, cy - 15, 31, 31)
        boxes[Guide.BorderWest].rect = QRect(10, cy - 20, 41, 41)

    def guide_at(self, pos):
        """ Get the guide under the given mouse position.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in layout coordinates.

        Returns
        -------
        result : Guide
            The enum value for the guide at the given position.

        """
        for enum, guide in self._guides.iteritems():
            if guide.contains(pos):
                return enum
        return Guide.NoGuide

    def mouse_over(self, pos):
        """ Perform a mouse over of the border guides.

        Parameters
        ----------
        pos : QPoint
            The position of interest expressed in layout coordinates.

        """
        for guide in self._guides.itervalues():
            if guide.contains(pos):
                last = self._last
                if last is not None and last is not guide:
                    last.opacity = LOW_ALPHA
                guide.opacity = FULL_ALPHA
                self._last = guide
                return
        if self._last is not None:
            self._last.opacity = LOW_ALPHA

    def paint(self, painter):
        """ Paint the border guides.

        Parameters
        ----------
        painter : QPainter
            The painter to use to paint the guides.

        """
        for box in self._boxes.itervalues():
            box.paint(painter)
        for guide in self._guides.itervalues():
            guide.paint(painter)


class CompassGuides(Atom):
    """ A class which renders the center compass for the guide rose.

    """
    _outer_guides = Value(factory=lambda: {
        Guide.CompassNorth: GuideImage('top'),
        Guide.CompassEast: GuideImage('right'),
        Guide.CompassSouth: GuideImage('bottom'),
        Guide.CompassWest: GuideImage('left'),
    })

    _center_guides = Value(factory=lambda: {
        Guide.CompassCenterNorth: GuideImage('center_top'),
        Guide.CompassCenterEast: GuideImage('center_right'),
        Guide.CompassCenterSouth: GuideImage('center_bottom'),
        Guide.CompassCenterWest: GuideImage('center_left',)
    })

    _box = Value(factory=lambda: GuideImage('cross'))

    _center = Value(Guide.CompassCenterNorth)

    _last = Value()

    _pos = Typed(QPoint)

    def iterguides(self):
        """ Iterate the guides for the compass.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (enum, guide) for
            the relevant guides in the compass.

        """
        for item in self._outer_guides.iteritems():
            yield item
        center = self._center
        yield (center, self._center_guides[center])

    def layout(self, pos):
        """ Layout the guides for the given position.

        Parameters
        ----------
        pos : QPoint
            The center point of the compass.

        """
        self._pos = pos
        x = pos.x()
        y = pos.y()
        outer_guides = self._outer_guides
        outer_guides[Guide.CompassNorth].rect = QRect(x - 15, y - 50, 31, 31)
        outer_guides[Guide.CompassEast].rect = QRect(x + 20, y - 15, 31, 31)
        outer_guides[Guide.CompassSouth].rect = QRect(x - 15, y + 20, 31, 31)
        outer_guides[Guide.CompassWest].rect = QRect(x - 50, y - 15, 31, 31)
        rect = QRect(x - 15, y - 15, 31, 31)
        center_guides = self._center_guides
        center_guides[Guide.CompassCenterNorth].rect = rect
        center_guides[Guide.CompassCenterEast].rect = rect
        center_guides[Guide.CompassCenterSouth].rect = rect
        center_guides[Guide.CompassCenterWest].rect = rect
        self._box.rect = QRect(x - 55, y - 55, 111, 111)

    def guide_at(self, pos):
        """ Get the guide under the given mouse position.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in layout coordinates.

        Returns
        -------
        result : Guide
            The enum value for the guide at the given position.

        """
        for enum, guide in self.iterguides():
            if guide.contains(pos):
                return enum
        return Guide.NoGuide

    def mouse_over(self, pos):
        """ Perform a mouse over of the compass guides.

        Parameters
        ----------
        pos : QPoint
            The position of interest expressed in layout coordinates.

        """
        for ignored, guide in self.iterguides():
            if guide.contains(pos):
                last = self._last
                if last is not None and last is not guide:
                    last.opacity = LOW_ALPHA
                guide.opacity = FULL_ALPHA
                self._last = guide
                return

        if self._last is not None:
            self._last.opacity = LOW_ALPHA

    def paint(self, painter):
        """ Paint the border guides.

        Parameters
        ----------
        painter : QPainter
            The painter to use to paint the guides.

        """
        self._box.paint(painter)
        for ignored, guide in self.iterguides():
            guide.paint(painter)


class CompassExGuides(Atom):
    """ A class which renders the center compass for the guide rose.

    """
    _outer_guides = Value(factory=lambda: {
        Guide.CompassNorth: GuideImage('top'),
        Guide.CompassEast: GuideImage('right'),
        Guide.CompassSouth: GuideImage('bottom'),
        Guide.CompassWest: GuideImage('left'),
    })

    _center_guides = Value(factory=lambda: {
        Guide.CompassCenterNorth: GuideImage('center_top'),
        Guide.CompassCenterEast: GuideImage('vbar'),
        Guide.CompassCenterSouth: GuideImage('hbar'),
        Guide.CompassCenterWest: GuideImage('vbar')
    })

    _box = Value(factory=lambda: GuideImage('cross_ex'))

    _last = Value()

    def iterguides(self):
        """ Iterate the guides for the compass.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (enum, guide) for
            the relevant guides in the compass.

        """
        for item in self._outer_guides.iteritems():
            yield item
        for item in self._center_guides.iteritems():
            yield item

    def layout(self, pos):
        """ Layout the guides for the given position.

        Parameters
        ----------
        pos : QPoint
            The center point of the compass.

        """
        x = pos.x()
        y = pos.y()
        outer_guides = self._outer_guides
        outer_guides[Guide.CompassNorth].rect = QRect(x - 15, y - 50, 31, 31)
        outer_guides[Guide.CompassEast].rect = QRect(x + 34, y - 15, 31, 31)
        outer_guides[Guide.CompassSouth].rect = QRect(x - 15, y + 34, 31, 31)
        outer_guides[Guide.CompassWest].rect = QRect(x - 64, y - 15, 31, 31)
        cguides = self._center_guides
        cguides[Guide.CompassCenterNorth].rect = QRect(x - 15, y - 15, 31, 31)
        cguides[Guide.CompassCenterEast].rect = QRect(x + 20, y - 15, 10, 31)
        cguides[Guide.CompassCenterSouth].rect = QRect(x - 15, y + 20, 31, 10)
        cguides[Guide.CompassCenterWest].rect = QRect(x - 29, y - 15, 10, 31)
        self._box.rect = QRect(x - 69, y - 55, 139, 125)

    def guide_at(self, pos):
        """ Get the guide under the given mouse position.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in layout coordinates.

        Returns
        -------
        result : Guide
            The enum value for the guide at the given position.

        """
        for enum, guide in self.iterguides():
            if guide.contains(pos):
                return enum
        return Guide.NoGuide

    def mouse_over(self, pos):
        """ Perform a mouse over of the compass guides.

        Parameters
        ----------
        pos : QPoint
            The position of interest expressed in layout coordinates.

        """
        for ignored, guide in self.iterguides():
            if guide.contains(pos):
                last = self._last
                if last is not None and last is not guide:
                    last.opacity = LOW_ALPHA
                guide.opacity = FULL_ALPHA
                self._last = guide
                return

        if self._last is not None:
            self._last.opacity = LOW_ALPHA

    def paint(self, painter):
        """ Paint the border guides.

        Parameters
        ----------
        painter : QPainter
            The painter to use to paint the guides.

        """
        self._box.paint(painter)
        for ignored, guide in self.iterguides():
            guide.paint(painter)


class SingleGuide(Atom):
    """ A class which renders a single guide for the guide rose.

    """
    # Reimplement in a subclass to hold the guide image.
    _guide = Value()

    # Reimplement in a subclass to store the guide enum.
    _enum = Value(Guide.NoGuide)

    _box = Value(factory=lambda: GuideImage('box'))

    def layout(self, pos):
        """ Layout the guides for the given position.

        Parameters
        ----------
        pos : QPoint
            The center point of the guide.

        """
        x = pos.x()
        y = pos.y()
        self._guide.rect = QRect(x - 15, y - 15, 31, 31)
        self._box.rect = QRect(x - 20, y - 20, 41, 41)

    def guide_at(self, pos):
        """ Get the guide under the given mouse position.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in layout coordinates.

        Returns
        -------
        result : Guide
            The enum value for the guide at the given position.

        """
        if self._guide.contains(pos):
            return self._enum
        return Guide.NoGuide

    def mouse_over(self, pos):
        """ Perform a mouse over of the guide.

        Parameters
        ----------
        pos : QPoint
            The position of interest expressed in layout coordinates.

        """
        guide = self._guide
        guide.opacity = FULL_ALPHA if guide.contains(pos) else LOW_ALPHA

    def paint(self, painter):
        """ Paint the border guide.

        Parameters
        ----------
        painter : QPainter
            The painter to use to paint the guide.

        """
        self._box.paint(painter)
        self._guide.paint(painter)


class HSplitGuide(SingleGuide):
    """ A single guide specialization for a horizontal split.

    """
    _guide = Value(factory=lambda: GuideImage('split_horizontal'))

    _enum = Value(Guide.SplitHorizontal)


class VSplitGuide(SingleGuide):
    """ A single guide specialization for a vertical split.

    """
    _guide = Value(factory=lambda: GuideImage('split_vertical'))

    _enum = Value(Guide.SplitVertical)


class SingleCenterGuide(SingleGuide):
    """ A single guide specialization for a center guide.

    """
    _guide = Value(factory=lambda: GuideImage('center_top'))

    _enum = Value(Guide.SingleCenter)


class QGuideRose(QFrame):
    """ A custom QFrame which implements a collection of docking guides.

    This widget must always be used as an independent top-level window.
    The dock area which uses the rose should manually set the geometry
    of the widget before showing it. The rose has a variety of guides:

    - Border Guides
        These are guides which stick to the top, left, right and
        bottom of the widget boundary with an offset of 10px. The
        locations of these guides are not adjustable.

    - Compass Guides
        These are five guides arranged in a compass. The center of
        the compass can be adjusted via the 'setCenter' method.
        The compass guide is (de)activated via 'setMode'.

    - Splitter Guides
        These are horizontal and vertical guides which can be used
        to indicate a hover over a splitter handle. The center of
        the guides can be adjusted via the 'setCenter' method.
        The splitter guides are (de)activated via 'setMode'.

    - Single Center Guide
        A single guide which will be displayed in the center of the
        of the layout area.

    """
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

        self._mode = GuideMode.NoMode
        self._center_point = QPoint()
        self._border_guides = BorderGuides()
        self._compass_guides = CompassExGuides()
        #self._compass_guides = CompassGuides()
        self._hsplit_guide = HSplitGuide()
        self._vsplit_guide = VSplitGuide()
        self._single_guide = SingleCenterGuide()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _layoutGuides(self):
        """ Layout the guides based on the current widget geometry.

        """
        self._border_guides.layout(self.rect())
        self._compass_guides.layout(self._center_point)
        self._hsplit_guide.layout(self._center_point)
        self._vsplit_guide.layout(self._center_point)
        self._single_guide.layout(self._center_point)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def centerPoint(self):
        """ Get the center point of the guide rose.

        Returns
        -------
        result : QPoint
            The location that will be used as the center of the portion
            of the rose with a configurable location.

        """
        return self._center_point

    def setCenterPoint(self, pos):
        """ Set the center point of the guide rose.

        Parameters
        ----------
        pos : QPoint
            The location that will be used as the center of the portion
            of the rose with a configurable location.

        """
        if pos != self._center_point:
            self._center_point = pos
            self._layoutGuides()
            self.update()

    def mode(self):
        """ Get the mode of the guide rose.

        Returns
        -------
        result : GuideMode
            The guide mode applied to the guide rose.

        """
        return self._mode

    def setMode(self, mode):
        """ Set the mode of the guide rose.

        Parameters
        ----------
        mode : GuideMode
            An or'd combination of mode flags for the guide rose.

        """
        if mode != self._mode:
            self._mode = mode
            self.update()

    def mouseOver(self, pos):
        """ Update the guide pads based on the mouse position.

        This current mode of the guide rose is used to determine which
        of the guide pads to should be updated.

        Parameters
        ----------
        pos : QPoint
            The position of the mouse expressed in local coordinates.

        """
        mode = self._mode
        if mode & GuideMode.Border:
            self._border_guides.mouse_over(pos)
        if mode & GuideMode.Compass:
            self._compass_guides.mouse_over(pos)
        if mode & GuideMode.SplitVertical:
            self._vsplit_guide.mouse_over(pos)
        if mode & GuideMode.SplitHorizontal:
            self._hsplit_guide.mouse_over(pos)
        if mode & GuideMode.SingleCenter:
            self._single_guide.mouse_over(pos)
        self.update()

    def guideAt(self, pos, mode=None):
        """ Get the guide which lies underneath a given position.

        Parameters
        ----------
        pos : QPoint
            The position of interest, expressed local coordinates.

        mode : QGuideRose.Mode, optional
            The mode to use for hit testing. If not provided, the
            current mode for the guide rose is used.

        Returns
        -------
        result : QGuideRose.Guide
            The enum value for the guide under the mouse position.

        """
        mode = mode if mode is not None else self._mode
        if mode & GuideMode.Border:
            g = self._border_guides.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        if mode & GuideMode.Compass:
            g = self._compass_guides.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        if mode & GuideMode.SplitHorizontal:
            g = self._hsplit_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        if mode & GuideMode.SplitVertical:
            g = self._vsplit_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        if mode & GuideMode.SingleCenter:
            g = self._single_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        return Guide.NoGuide

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def resizeEvent(self, event):
        """ Handle the resize event for the rose.

        This handler will relayout the guides on a resize.

        """
        self._layoutGuides()

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
        if mode & GuideMode.Border:
            self._border_guides.paint(painter)
        if mode & GuideMode.Compass:
            self._compass_guides.paint(painter)
        if mode & GuideMode.SplitHorizontal:
            self._hsplit_guide.paint(painter)
        if mode & GuideMode.SplitVertical:
            self._vsplit_guide.paint(painter)
        if mode & GuideMode.SingleCenter:
            self._single_guide.paint(painter)
