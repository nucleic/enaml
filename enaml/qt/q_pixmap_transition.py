#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QPoint, QPointF, QRect, QVariantAnimation, Signal
from .QtGui import QPainter, QPixmap, QPainterPath


class QPixmapTransition(QVariantAnimation):
    """ A QVariantAnimation subclass for building transitions between
    two QPixmaps.

    This is an abstract base class which provides common functionality
    for creating concrete transitions.

    """
    #: A signal emmitted when the output pixmap has been updated with
    #: a new frame in the transition animation. The paylod will be the
    #: output pixmap of the transition.
    pixmapUpdated = Signal(QPixmap)

    def __init__(self):
        """ Initialize a QPixmapTransition.

        """
        super(QPixmapTransition, self).__init__()
        self._start_pixmap = None
        self._end_pixmap = None
        self._out_pixmap = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def startPixmap(self):
        """ Get the starting pixmap for the transition.

        Returns
        -------
        result : QPixmap or None
            The starting pixmap for the transition or None if it has
            not yet been provided.

        """
        return self._start_pixmap

    def endPixmap(self):
        """ Get the ending pixmap for the transition.

        Returns
        -------
        result : QPixmap or None
            The ending pixmap for the transition or None if it has
            not yet been provided.

        """
        return self._end_pixmap

    def outPixmap(self):
        """ Get the output pixmap for the transition.

        Returns
        -------
        result : QPixmap or None
            The output pixmap for the transition or None if it has
            not yet been provided.

        """
        return self._out_pixmap

    def setPixmaps(self, start, end, out):
        """ Set the pixmaps to use during the transition.

        Parameters
        ----------
        start : QPixmap
            The pixmap for the first frame of the transition.

        end : QPixmap
            The pixmap for the last frame of the transition.

        out : QPixmap
            The pixmap into which the intermediate transition frames
            will be drawn.

        """
        self._start_pixmap = start
        self._end_pixmap = end
        self._out_pixmap = out

    def start(self):
        """ Start the pixmap transition.

        This is an overridden parent class method which provides a
        hook for subclasses to prepare their working pixmaps before
        the animation is started.

        """
        start, end = self.preparePixmap()
        self.setStartValue(start)
        self.setEndValue(end)
        super(QPixmapTransition, self).start()

    def updateCurrentValue(self, value):
        """ Updates the current transition value.

        This method will dispatch to the `updatePixmap` method provided
        that the current animation state is `Running` and then emit
        the `pixmapUpdated` signal.

        Parameters
        ----------
        value : object
            The variant interpolated object value for the current step
            in the animation.

        """
        if self.state() == self.Running:
            self.updatePixmap(value)
            self.pixmapUpdated.emit(self.outPixmap())

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def preparePixmap(self):
        """ Prepare the underlying pixmap(s) for the transition.

        This method is abstract and must be implemented by subclasses.
        It is called directly before the transition is started. The
        subclass should do any required transition initialization in
        this method.

        Returns
        -------
        result : (start, end)
            The start and end values to use when interpolating the
            transition. The interpolated values will be passed to
            the `updatePixmap` method.

        """
        raise NotImplementedError

    def updatePixmap(self, value):
        """ Update the underlying output pixmap for the transition.

        This method is abstract and must be implemented by subclasses.
        It is called during the transition with an interpolated value
        appopriate for the current transition step.

        Parameters
        ----------
        value : object
            The interpolated value between the values of `start` and
            `end` returned by the `preparePixmap` method.

        """
        raise NotImplementedError


class QDirectedTransition(QPixmapTransition):
    """ A QPixmapTransition which adds a transition direction.

    This is a base class used by several concrete transition classes.
    It is not meant to be used directly.

    """
    #: Transition proceeds from left to right.
    LeftToRight = 0

    #: Transition proceeds from right to left.
    RightToLeft = 1

    #: Transition proceeds from top to bottom.
    TopToBottom = 2

    #: Transition proceeds from bottom to top.
    BottomToTop = 3

    def __init__(self):
        """ Initialize a QDirectedTransition.

        """
        super(QDirectedTransition, self).__init__()
        self._direction = self.RightToLeft

    def direction(self):
        """ Get the direction of the transition.

        Returns
        -------
        result : int
            The direction enum value for the transition.

        """
        return self._direction

    def setDirection(self, direction):
        """ Set the direction of the transition.

        Parameters
        ----------
        direction : int
            The direction enum value for the transition. Must be one
            of `LeftToRight`, `RightToLeft`, `TopToBottom`, or
            `BottomToTop`.

        """
        dirs = (
            self.LeftToRight, self.RightToLeft,
            self.TopToBottom, self.BottomToTop,
        )
        if direction not in dirs:
            raise ValueError('Invalid direction: %s' % direction)
        self._direction = direction


class QSlideTransition(QDirectedTransition):
    """ A QDirectedTransition which animates using a sliding effect.

    """
    def __init__(self):
        """ Initialize a QSlideTransition.

        """
        super(QSlideTransition, self).__init__()
        self._slide_pixmap = None

    def preparePixmap(self):
        """ Prepare the pixmap(s) for the transition.

        This method builds a temporary pixmap containing both the start
        and end pixmaps adjoined. The transition then draws a subrect
        of this pixmap into the output pixmap.

        """
        start = self.startPixmap()
        end = self.endPixmap()
        size = start.size().expandedTo(end.size())
        width = size.width()
        height = size.height()
        direction = self.direction()
        if direction == self.LeftToRight:
            pm = QPixmap(width * 2, height)
            painter = QPainter(pm)
            painter.drawPixmap(0, 0, end)
            painter.drawPixmap(width, 0, start)
            start_rect = QRect(width, 0, width * 2, height)
            end_rect = QRect(0, 0, width, height)
        elif direction == self.RightToLeft:
            pm = QPixmap(width * 2, height)
            painter = QPainter(pm)
            painter.drawPixmap(0, 0, start)
            painter.drawPixmap(width, 0, end)
            start_rect = QRect(0, 0, width, height)
            end_rect = QRect(width, 0, width * 2, height)
        elif direction == self.TopToBottom:
            pm = QPixmap(width, height * 2)
            painter = QPainter(pm)
            painter.drawPixmap(0, 0, end)
            painter.drawPixmap(0, height, start)
            start_rect = QRect(0, height, width, height * 2)
            end_rect = QRect(0, 0, width, height)
        elif direction == self.BottomToTop:
            pm = QPixmap(width, height * 2)
            painter = QPainter(pm)
            painter.drawPixmap(0, 0, start)
            painter.drawPixmap(0, height, end)
            start_rect = QRect(0, 0, width, height)
            end_rect = QRect(0, height, width, height * 2)
        else:
            raise ValueError('Invalid direction: %s' % direction)
        self._slide_pixmap = pm
        return start_rect, end_rect

    def updatePixmap(self, rect):
        """ Update the pixmap for the current transition.

        This method paints the current rect from the internal slide
        pixmap into the output pixmap.

        """
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(QPoint(0, 0), self._slide_pixmap, rect)


class QWipeTransition(QDirectedTransition):
    """ A QDirectedTransition which animates using a wipe effect.

    """
    def preparePixmap(self):
        """ Prepare the pixmap(s) for the transition.

        This method draws the starting pixmap into the output pixmap.
        The transition update then draws over the output with the
        proper portion of the ending pixmap.

        """
        start = self.startPixmap()
        end = self.endPixmap()
        size = start.size().expandedTo(end.size())
        width = size.width()
        height = size.height()
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(0, 0, start)
        direction = self.direction()
        if direction == self.LeftToRight:
            start_rect = QRect(0, 0, 0, height)
        elif direction == self.RightToLeft:
            start_rect = QRect(width, 0, 0, height)
        elif direction == self.TopToBottom:
            start_rect = QRect(0, 0, width, 0)
        elif direction == self.BottomToTop:
            start_rect = QRect(0, height, width, 0)
        else:
            raise ValueError('Invalid direction: %s' % direction)
        end_rect = QRect(0, 0, width, height)
        return start_rect, end_rect

    def updatePixmap(self, rect):
        """ Update the pixmap for the current transition.

        This method paints the current rect from the ending pixmap into
        the proper rect of the output pixmap.

        """
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(rect, self.endPixmap(), rect)


class QIrisTransition(QPixmapTransition):
    """ A QPixmap transition which animates using an iris effect.

    """
    def preparePixmap(self):
        """ Prepare the pixmap(s) for the transition.

        This method draws the starting pixmap into the output pixmap.
        The transition update then sets a circular clipping region on
        the ouput and draws in the ending pixmap.

        """
        start = self.startPixmap()
        end = self.endPixmap()
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(0, 0, start)
        size = start.size().expandedTo(end.size())
        width = size.width()
        height = size.height()
        radius = int((width**2 + height**2) ** 0.5) / 2
        start_rect = QRect(width / 2, height / 2, 0, 0)
        end_rect = QRect(width / 2, height / 2, radius, radius)
        return start_rect, end_rect

    def updatePixmap(self, rect):
        """ Update the pixmap for the current transition.

        This method sets a radial clipping region on the output pixmap
        and draws in the relevant portion of the ending pixamp.

        """
        x = rect.x()
        y = rect.y()
        rx = rect.width()
        ry = rect.height()
        path = QPainterPath()
        path.addEllipse(QPointF(x, y), float(rx), float(ry))
        painter = QPainter(self.outPixmap())
        painter.setClipPath(path)
        painter.drawPixmap(QPoint(0, 0), self.endPixmap())


class QFadeTransition(QPixmapTransition):
    """ A QPixmapTransition which animates using a fade effect.

    """
    def preparePixmap(self):
        """ Prepare the pixmap(s) for the transition.

        This method draws the starting pixmap into the output pixmap.
        The transition updates then draw the relevant pixmaps into
        the output using an appropriate alpha.

        """
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(QPoint(0, 0), self.startPixmap())
        return -1.0, 1.0

    def updatePixmap(self, alpha):
        """ Update the pixmap for the current transition.

        This method first clears the output pixmap. It then draws a
        pixmap using the given alpha value. An alpha value less than
        zero indicates that the starting pixmap should be drawn. A
        value greater than or equal to zero indicates the ending
        pixmap should be drawn.

        """
        out = self.outPixmap()
        painter = QPainter(out)
        painter.eraseRect(0, 0, out.width(), out.height())
        if alpha < 0.0:
            alpha = -1.0 * alpha
            source = self.startPixmap()
        else:
            source = self.endPixmap()
        painter.setOpacity(alpha)
        painter.drawPixmap(QPoint(0, 0), source)


class QCrossFadeTransition(QPixmapTransition):
    """ A QPixmapTransition which animates using a cross fade effect.

    """
    def preparePixmap(self):
        """ Prepare the pixmap(s) for the transition.

        This method draws the starting pixmap into the output pixmap.
        The transition updates then draw the two pixmaps with an
        appropriate alpha blending value.

        """
        painter = QPainter(self.outPixmap())
        painter.drawPixmap(QPoint(0, 0), self.startPixmap())
        return 0.0, 1.0

    def updatePixmap(self, alpha):
        """ Update the pixmap for the current transition.

        This method first clears the output pixmap. It then draws the
        starting pixmap followed by the ending pixmap. Each pixmap is
        drawn with complementary alpha values.

        """
        out = self.outPixmap()
        painter = QPainter(out)
        painter.eraseRect(0, 0, out.width(), out.height())
        painter.setOpacity(1.0 - alpha)
        painter.drawPixmap(QPoint(0, 0), self.startPixmap())
        painter.setOpacity(alpha)
        painter.drawPixmap(QPoint(0, 0), self.endPixmap())
