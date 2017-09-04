#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Atom, Float, Int, Str, Typed, Value, set_default

from enaml.qt.QtCore import Qt, QRect, QPoint
from enaml.qt.QtGui import QImage, QPainter
from enaml.qt.QtWidgets import QFrame

# Make sure the resources get registered.
from . import dock_resources


class QGuideRose(QFrame):
    """ A custom QFrame which implements a collection of docking guides.

    This widget must always be used as an independent top-level window.
    The dock area which uses the rose should manually set the geometry
    of the widget before showing it.

    """
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

        #: The center compass guide.
        CompassCenter = 9

        #: The extended compass north guide.
        CompassExNorth = 10

        #: The extended compass east guide.
        CompassExEast = 11

        #: The extended compass south guide.
        CompassExSouth = 12

        #: The extended compass west guide.
        CompassExWest = 13

        #: The vertical split guide.
        SplitVertical = 14

        #: The horizontal split guide.
        SplitHorizontal = 15

        #: The area center guide.
        AreaCenter = 16

        #: The extended border north guide.
        BorderExNorth = 17

        #: The extended border east guide.
        BorderExEast = 18

        #: The extended border south guide.
        BorderExSouth = 19

        #: The extended border west guide.
        BorderExWest = 20

    class Mode(object):
        """ An enum class for defining the mode for the guide rose.

        A mode is an or'd combination of flags which dictate which parts
        of the guide rose are active on the screen. The modes related to
        the centerpiece should be considered mutually exclusive.

        """
        #: Nothing will be shown.
        NoMode = 0x0

        #: Show the border guides.
        Border = 0x1

        #: Show the standard compass as the centerpiece.
        Compass = 0x2

        #: Show the extended compass as the centerpiece.
        CompassEx = 0x4

        #: Show the horizontal split guide as the centerpiece.
        SplitHorizontal = 0x8

        #: Show the vertical split guide as the centerpiece.
        SplitVertical = 0x10

        #: Show the vertical area center as the centerpiece.
        AreaCenter = 0x20

    def __init__(self):
        """ Initialize a QGuideRose.

        """
        super(QGuideRose, self).__init__()
        # On Mac, setting the translucent background does not cause the
        # frame shadow to be hidden; it must be explicitly hidden. Mac
        # also requires the window to be a tooltip in order to be raised
        # above the rubber band in the Z-order. On Windows, the tooltip
        # leaves a dropshadow on Qt >= 4.8 whereas tool does not.
        if sys.platform == 'darwin':
            self.setAttribute(Qt.WA_MacNoShadow, True)
            flags = Qt.ToolTip
        else:
            flags = Qt.Tool
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        flags |= Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self._mode = self.Mode.NoMode
        self._center_point = QPoint()
        self._border_guide = BorderGuide()
        self._compass_guide = CompassGuide()
        self._compass_ex_guide = CompassExGuide()
        self._vsplit_guide = SplitVerticalGuide()
        self._hsplit_guide = SplitHorizontalGuide()
        self._area_guide = AreaCenterGuide()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _layoutGuides(self):
        """ Layout the guides based on the current widget geometry.

        """
        self._border_guide.layout(self.rect())
        self._compass_guide.layout(self._center_point)
        self._compass_ex_guide.layout(self._center_point)
        self._vsplit_guide.layout(self._center_point)
        self._hsplit_guide.layout(self._center_point)
        self._area_guide.layout(self._center_point)

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
        self._border_guide.mouse_over(pos)
        self._compass_guide.mouse_over(pos)
        self._compass_ex_guide.mouse_over(pos)
        self._vsplit_guide.mouse_over(pos)
        self._hsplit_guide.mouse_over(pos)
        self._area_guide.mouse_over(pos)
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
        Guide = self.Guide
        Mode = self.Mode
        mode = mode if mode is not None else self._mode
        if mode & Mode.Border:
            g = self._border_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        if mode & Mode.Compass:
            g = self._compass_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        elif mode & Mode.CompassEx:
            g = self._compass_ex_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        elif mode & Mode.SplitHorizontal:
            g = self._hsplit_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        elif mode & Mode.SplitVertical:
            g = self._vsplit_guide.guide_at(pos)
            if g != Guide.NoGuide:
                return g
        elif mode & Mode.AreaCenter:
            g = self._area_guide.guide_at(pos)
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
        super(QGuideRose, self).paintEvent(event)
        painter = QPainter(self)
        Mode = self.Mode
        mode = self._mode
        if mode & Mode.Border:
            self._border_guide.paint(painter)
        if mode & Mode.Compass:
            self._compass_guide.paint(painter)
        elif mode & Mode.CompassEx:
            self._compass_ex_guide.paint(painter)
        elif mode & Mode.SplitHorizontal:
            self._hsplit_guide.paint(painter)
        elif mode & Mode.SplitVertical:
            self._vsplit_guide.paint(painter)
        elif mode & Mode.AreaCenter:
            self._area_guide.paint(painter)


class GuideImage(Atom):
    """ A class which manages the painting of a guide image.

    """
    #: The default alpha value for guide transparency.
    TRANSPARENT = 0.60

    #: The default alpha value for no guide transparency.
    OPAQUE = 1.0

    #: The QImage to use when painting the guide.
    image = Typed(QImage, factory=lambda: QImage())

    #: The QRect specifying where to draw the image.
    rect = Typed(QRect, factory=lambda: QRect())

    #: The opacity to use when drawing the image.
    opacity = Float(TRANSPARENT)

    #: A cache of QImage instances for the loaded guide images.
    _images = {}

    @classmethod
    def load_image(cls, name):
        """ Load the guide image for the given name into a QImage.

        This function is hard-coded to return the named .png image from
        the ./dockguides directory located alongside this file. It is not
        a generic image loading routine.

        """
        image = cls._images.get(name)
        if image is None:
            image = QImage(':dock_images/%s.png' % name)
            cls._images[name] = image
        return image

    def __init__(self, name):
        """ Initialize a GuideImage.

        Parameters
        ----------
        name : string
            The name of the image to load for the guide.

        """
        self.image = self.load_image(name)

    def opacify(self):
        """ Make the guide image opaque.

        """
        self.opacity = self.OPAQUE

    def transparentize(self):
        """ Make the guide image transparent.

        """
        self.opacity = self.TRANSPARENT

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


class GuideHandler(Atom):
    """ A base class for defining guide handlers.

    """
    #: The last guide hit during a mouseover.
    _last_guide = Typed(GuideImage)

    def iterguides(self):
        """ Iterate the guides managed by this handler.

        Returns
        -------
        result : iterable
            An iterable of (Guide, GuideImage) pairs which are the
            guides managed by the handler.

        """
        raise NotImplementedError

    def iterboxes(self):
        """ Iterate the boxes which lie under the guides.

        Returns
        -------
        result : iterable
            An iterable of GuideImage instances which are the boxes
            to be painted under the guides.

        """
        raise NotImplementedError

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
        return QGuideRose.Guide.NoGuide

    def mouse_over(self, pos):
        """ Perform a mouse over of the guides.

        Parameters
        ----------
        pos : QPoint
            The position of interest expressed in layout coordinates.

        """
        for ignored, guide in self.iterguides():
            if guide.contains(pos):
                last = self._last_guide
                if last is not None and last is not guide:
                    last.transparentize()
                guide.opacify()
                self._last_guide = guide
                break
        else:
            if self._last_guide is not None:
                self._last_guide.transparentize()

    def paint(self, painter):
        """ Paint the guides using the supplied painter.

        Parameters
        ----------
        painter : QPainter
            The painter to use to paint the guides.

        """
        for box in self.iterboxes():
            box.paint(painter)
        for ignored, guide in self.iterguides():
            guide.paint(painter)


class BorderGuide(GuideHandler):
    """ A guide handler which manages the border guide.

    """
    _guides = Value(factory=lambda: {
        QGuideRose.Guide.BorderNorth: GuideImage('thin_horizontal'),
        QGuideRose.Guide.BorderExNorth: GuideImage('bar_horizontal'),
        QGuideRose.Guide.BorderEast: GuideImage('thin_vertical'),
        QGuideRose.Guide.BorderExEast: GuideImage('bar_vertical'),
        QGuideRose.Guide.BorderSouth: GuideImage('thin_horizontal'),
        QGuideRose.Guide.BorderExSouth: GuideImage('bar_horizontal'),
        QGuideRose.Guide.BorderWest: GuideImage('thin_vertical'),
        QGuideRose.Guide.BorderExWest: GuideImage('bar_vertical'),
    })

    _boxes = Value(factory=lambda: {
        QGuideRose.Guide.BorderNorth: GuideImage('guide_box'),
        QGuideRose.Guide.BorderEast: GuideImage('guide_box'),
        QGuideRose.Guide.BorderSouth: GuideImage('guide_box'),
        QGuideRose.Guide.BorderWest: GuideImage('guide_box'),
    })

    def iterguides(self):
        """ Iterate the guides managed by the handler.

        Returns
        -------
        result : iterable
            An iterable of (Guide, GuideImage) pairs which are the
            guides managed by the handler.

        """
        return iter(self._guides.items())

    def iterboxes(self):
        """ Iterate the boxes which lie under the guides.

        Returns
        -------
        result : iterable
            An iterable of GuideImage instances which are the boxes
            to be painted under the guides.

        """
        return iter(self._boxes.values())

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
        Guide = QGuideRose.Guide
        guides[Guide.BorderNorth].rect = QRect(cx - 15, 27, 31, 19)
        guides[Guide.BorderExNorth].rect = QRect(cx - 15, 15, 31, 10)
        boxes[Guide.BorderNorth].rect = QRect(cx - 20, 10, 41, 41)
        guides[Guide.BorderEast].rect = QRect(w - 45, cy - 15, 19, 31)
        guides[Guide.BorderExEast].rect = QRect(w - 24, cy - 15, 10, 31)
        boxes[Guide.BorderEast].rect = QRect(w - 50, cy - 20, 41, 41)
        guides[Guide.BorderSouth].rect = QRect(cx - 15, h - 45, 31, 19)
        guides[Guide.BorderExSouth].rect = QRect(cx - 15, h - 24, 31, 10)
        boxes[Guide.BorderSouth].rect = QRect(cx - 20, h - 50, 41, 41)
        guides[Guide.BorderWest].rect = QRect(27, cy - 15, 19, 31)
        guides[Guide.BorderExWest].rect = QRect(15, cy - 15, 10, 31)
        boxes[Guide.BorderWest].rect = QRect(10, cy - 20, 41, 41)


class CompassGuide(GuideHandler):
    """ A guide handler which manages the standard compass guide.

    """
    _guides = Value(factory=lambda: {
        QGuideRose.Guide.CompassNorth: GuideImage('arrow_north'),
        QGuideRose.Guide.CompassEast: GuideImage('arrow_east'),
        QGuideRose.Guide.CompassSouth: GuideImage('arrow_south'),
        QGuideRose.Guide.CompassWest: GuideImage('arrow_west'),
        QGuideRose.Guide.CompassCenter: GuideImage('center'),
    })

    _box = Value(factory=lambda: GuideImage('cross_box'))

    def iterguides(self):
        """ Iterate the guides for the compass.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (enum, guide) for
            the relevant guides in the compass.

        """
        return iter(self._guides.items())

    def iterboxes(self):
        """ Iterate the boxes which lie under the guides.

        Returns
        -------
        result : iterable
            An iterable of GuideImage instances which are the boxes
            to be painted under the guides.

        """
        yield self._box

    def layout(self, pos):
        """ Layout the guides for the given position.

        Parameters
        ----------
        pos : QPoint
            The center point of the compass.

        """
        x = pos.x()
        y = pos.y()
        Guide = QGuideRose.Guide
        guides = self._guides
        guides[Guide.CompassNorth].rect = QRect(x - 15, y - 50, 31, 31)
        guides[Guide.CompassEast].rect = QRect(x + 20, y - 15, 31, 31)
        guides[Guide.CompassSouth].rect = QRect(x - 15, y + 20, 31, 31)
        guides[Guide.CompassWest].rect = QRect(x - 50, y - 15, 31, 31)
        guides[Guide.CompassCenter].rect = QRect(x - 15, y - 15, 31, 31)
        self._box.rect = QRect(x - 55, y - 55, 111, 111)


class CompassExGuide(GuideHandler):
    """ A class which renders the extended compass guide.

    """
    _guides = Value(factory=lambda: {
        QGuideRose.Guide.CompassNorth: GuideImage('arrow_north'),
        QGuideRose.Guide.CompassEast: GuideImage('arrow_east'),
        QGuideRose.Guide.CompassSouth: GuideImage('arrow_south'),
        QGuideRose.Guide.CompassWest: GuideImage('arrow_west'),
        QGuideRose.Guide.CompassCenter: GuideImage('center'),
        QGuideRose.Guide.CompassExNorth: GuideImage('bar_horizontal'),
        QGuideRose.Guide.CompassExEast: GuideImage('bar_vertical'),
        QGuideRose.Guide.CompassExSouth: GuideImage('bar_horizontal'),
        QGuideRose.Guide.CompassExWest: GuideImage('bar_vertical'),
    })

    _box = Value(factory=lambda: GuideImage('cross_ex_box'))

    def iterguides(self):
        """ Iterate the guides for the extented compass.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (enum, guide) for
            the relevant guides in the compass.

        """
        return iter(self._guides.items())

    def iterboxes(self):
        """ Iterate the boxes which lie under the guides.

        Returns
        -------
        result : iterable
            An iterable of GuideImage instances which are the boxes
            to be painted under the guides.

        """
        yield self._box

    def layout(self, pos):
        """ Layout the guides for the extended compass.

        Parameters
        ----------
        pos : QPoint
            The center point of the compass.

        """
        x = pos.x()
        y = pos.y()
        Guide = QGuideRose.Guide
        guides = self._guides
        guides[Guide.CompassNorth].rect = QRect(x - 15, y - 64, 31, 31)
        guides[Guide.CompassEast].rect = QRect(x + 34, y - 15, 31, 31)
        guides[Guide.CompassSouth].rect = QRect(x - 15, y + 34, 31, 31)
        guides[Guide.CompassWest].rect = QRect(x - 64, y - 15, 31, 31)
        guides[Guide.CompassCenter].rect = QRect(x - 15, y - 15, 31, 31)
        guides[Guide.CompassExNorth].rect = QRect(x - 15, y - 29, 31, 10)
        guides[Guide.CompassExEast].rect = QRect(x + 20, y - 15, 10, 31)
        guides[Guide.CompassExSouth].rect = QRect(x - 15, y + 20, 31, 10)
        guides[Guide.CompassExWest].rect = QRect(x - 29, y - 15, 10, 31)
        self._box.rect = QRect(x - 69, y - 69, 139, 139)


class SingleGuide(GuideHandler):
    """ A base class for defining a single guide.

    """
    guide_enum = Int(QGuideRose.Guide.NoGuide)

    image_name = Str('')

    _box = Value(factory=lambda: GuideImage('guide_box'))

    _guide = Typed(GuideImage)

    def _default__guide(self):
        """ The default value handler for the '_guide' attribute.

        """
        return GuideImage(self.image_name)

    def iterguides(self):
        """ Iterate the guides for the compass.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (enum, guide) for
            the relevant guides in the compass.

        """
        yield (self.guide_enum, self._guide)

    def iterboxes(self):
        """ Iterate the boxes which lie under the guides.

        Returns
        -------
        result : iterable
            An iterable of GuideImage instances which are the boxes
            to be painted under the guides.

        """
        yield self._box

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


class SplitHorizontalGuide(SingleGuide):
    """ A single guide which uses the horizontal split image.

    """
    guide_enum = set_default(QGuideRose.Guide.SplitHorizontal)

    image_name = set_default('split_horizontal')


class SplitVerticalGuide(SingleGuide):
    """ A single guide which uses the vertical split image.

    """
    guide_enum = set_default(QGuideRose.Guide.SplitVertical)

    image_name = set_default('split_vertical')


class AreaCenterGuide(SingleGuide):
    """ A single guide which uses the area center image.

    """
    guide_enum = set_default(QGuideRose.Guide.AreaCenter)

    image_name = set_default('center')
