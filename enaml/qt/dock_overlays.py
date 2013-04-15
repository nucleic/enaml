#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect, QTimer, QPropertyAnimation
from PyQt4.QtGui import QRubberBand, QSplitterHandle, QTabWidget

from atom.api import Atom, Int, Float, Typed

from .q_guide_rose import QGuideRose
from .q_dock_item import QDockItem


def band_geometry(area, widget, guide, border_size):
    """ Compute the geometry for an overlay rubber band.

    Parameters
    ----------
    area : QDockArea
        The dock area under the mouse.

    widget : QWidget
        The target widget in the dock area under the mouse.

    guide : QGuideRose.Guide
        The rose guide under the mouse.

    border_size : int
        The size to use for the rubber band when in border position.

    """
    Guide = QGuideRose.Guide
    if guide == Guide.NoGuide:
        return QRect()

    # border hits
    m = area.contentsMargins()
    if guide == Guide.BorderNorth:
        p = QPoint(m.left(), m.top())
        s = QSize(area.width() - m.left() - m.right(), border_size)
    elif guide == Guide.BorderEast:
        p = QPoint(area.width() - border_size - m.right(), m.top())
        s = QSize(border_size, area.height() - m.top() - m.bottom())
    elif guide == Guide.BorderSouth:
        p = QPoint(m.left(), area.height() - border_size - m.bottom())
        s = QSize(area.width() - m.left() - m.right(), border_size)
    elif guide == Guide.BorderWest:
        p = QPoint(m.left(), m.top())
        s = QSize(border_size, area.height() - m.top() - m.bottom())

    # compass hits
    elif guide == Guide.CompassNorth:
        p = widget.mapTo(widget, QPoint(0, 0))
        s = widget.size()
        s.setHeight(s.height() / 3)
    elif guide == Guide.CompassEast:
        p = widget.mapTo(widget, QPoint(0, 0))
        s = widget.size()
        d = s.width() / 3
        r = s.width() - d
        s.setWidth(d)
        p.setX(p.x() + r)
    elif guide == Guide.CompassSouth:
        p = widget.mapTo(widget, QPoint(0, 0))
        s = widget.size()
        d = s.height() / 3
        r = s.height() - d
        s.setHeight(d)
        p.setY(p.y() + r)
    elif guide == Guide.CompassWest:
        p = widget.mapTo(widget, QPoint(0, 0))
        s = widget.size()
        s.setWidth(s.width() / 3)
    elif guide == Guide.CompassCenter:
        p = widget.mapTo(widget, QPoint(0, 0))
        s = widget.size()

    # splitter handle hits
    elif guide == Guide.SplitHorizontal:
        p = widget.mapTo(widget, QPoint(0, 0))
        wo, r = divmod(border_size - widget.width(), 2)
        wo += r
        p.setX(p.x() - wo)
        s = QSize(2 * wo + widget.width(), widget.height())
    elif guide == Guide.SplitVertical:
        p = widget.mapTo(widget, QPoint(0, 0))
        ho, r = divmod(border_size - widget.height(), 2)
        ho += r
        p.setY(p.y() - ho)
        s = QSize(widget.width(), 2 * ho + widget.height())

    # default no-op
    else:
        s = QSize()
        p = QPoint()

    p = widget.mapToGlobal(p)
    return QRect(p, s)


class DockOverlays(Atom):
    """ An object which manages the overlays for a QDockArea.

    This manager handles the state transitions for the overlays. The
    transitions are performed on a slightly-delayed timer to provide
    a more fluid user interaction experience.

    """
    #: The size of the rubber band when docking on the border, in px.
    boder_size = Int(60)

    #: The delay to use when triggering the rose timer, in ms.
    rose_delay = Int(30)

    #: The delay to use when triggering the band timer, in ms.
    band_delay = Int(50)

    #: The target opacity to use when making the band visible.
    band_target_opacity = Float(0.6)

    #: The duration of the band visibilty animation, in ms.
    band_vis_duration = Int(100)

    #: the duration of the band geometry animation, in ms.
    band_geo_duration = Int(100)

    #: The overlayed guide rose.
    _rose = Typed(QGuideRose, ())

    #: The overlayed rubber band.
    _band = Typed(QRubberBand, (QRubberBand.Rectangle,))

    #: The property animator for the rubber band geometry.
    _geo_animator = Typed(QPropertyAnimation)

    #: The property animator for the rubber band visibility.
    _vis_animator = Typed(QPropertyAnimation)

    #: The target mode to apply to the rose on timeout.
    _target_rose_mode = Int(QGuideRose.Mode.NoMode)

    #: The target geometry to apply to rubber band on timeout.
    _target_band_geo = Typed(QRect, factory=lambda: QRect())

    #: The queued band geo.
    _queued_band_geo = Typed(QRect)

    #: The value of the last guide which was hit in the rose.
    _last_guide = Int(-1)

    #: The hover position of the mouse to use for state changes.
    _hover_pos = Typed(QPoint)

    #: The timer for changing the state of the rose.
    _rose_timer = Typed(QTimer)

    #: The timer for changing the state of the band.
    _band_timer = Typed(QTimer)

    #--------------------------------------------------------------------------
    # Default Value Methods
    #--------------------------------------------------------------------------
    def _default__rose_timer(self):
        """ Create the default timer for the rose state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_rose_timer)
        return timer

    def _default__band_timer(self):
        """ Create the default timer for the band state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_band_timer)
        return timer

    def _default__geo_animator(self):
        """ Create the default property animator for the rubber band.

        """
        p = QPropertyAnimation(self._band, 'geometry')
        p.setDuration(self.band_geo_duration)
        return p

    def _default__vis_animator(self):
        """ Create the default property animator for the rubber band.

        """
        p = QPropertyAnimation(self._band, 'windowOpacity')
        p.setDuration(self.band_vis_duration)
        p.finished.connect(self._on_vis_finished)
        return p

    #--------------------------------------------------------------------------
    # Timer Handlers
    #--------------------------------------------------------------------------
    def _on_rose_timer(self):
        """ Handle the timeout event for the internal rose timer.

        This handler transitions the rose to its new state and updates
        the position of the rubber band.

        """
        rose = self._rose
        rose.setMode(self._target_rose_mode)
        rose.hover(self._hover_pos)
        self._update_band_state()

    def _on_band_timer(self):
        """ Handle the timeout event for the internal band timer.

        This handler updates the position of the rubber band.

        """
        self._update_band_state()

    #--------------------------------------------------------------------------
    # Animation Handlers
    #--------------------------------------------------------------------------
    def _on_vis_finished(self):
        """ Handle the 'finished' signal from the visibility animator.

        This handle will hide the rubber band when its opacity is 0.

        """
        band = self._band
        if band.windowOpacity() == 0.0:
            band.hide()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_band_state(self):
        """ Refresh the geometry and visible state of the rubber band.

        The state will be updated using animated properties to provide
        a nice fluid user experience.

        """
        # A valid geometry indicates that the rubber should be shown on
        # the screen. An invalid geometry means it should be hidden. If
        # the validity is changed during animation, the animators are
        # restarted using the current state as their starting point.
        band = self._band
        geo = self._target_band_geo
        if geo.isValid():
            # If the band is already hidden, the geometry animation can
            # be bypassed since the band can be located anywhere. The
            # rose must be raised because QRubberBand raises itself
            # when it receives a showEvent.
            if band.isHidden():
                band.setGeometry(geo)
                self._start_vis_animator(self.band_target_opacity)
                self._rose.raise_()
                return
            self._start_vis_animator(self.band_target_opacity)
            self._start_geo_animator(geo)
        else:
            self._start_vis_animator(0.0)

    def _start_vis_animator(self, opacity):
        """ (Re)start the visibility animator.

        Parameters
        ----------
        opacity : float
            The target opacity of the target object.

        """
        animator = self._vis_animator
        if animator.state() == animator.Running:
            animator.stop()
        target = animator.targetObject()
        if target.isHidden() and opacity != 0.0:
            target.setWindowOpacity(0.0)
            target.show()
        animator.setStartValue(target.windowOpacity())
        animator.setEndValue(opacity)
        animator.start()

    def _start_geo_animator(self, geo):
        """ (Re)start the visibility animator.

        Parameters
        ----------
        geo : QRect
            The target geometry for the target object.

        """
        animator = self._geo_animator
        if animator.state() == animator.Running:
            animator.stop()
        target = animator.targetObject()
        animator.setStartValue(target.geometry())
        animator.setEndValue(geo)
        animator.start()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def hide(self):
        """ Hide the overlay widgets from the screen.

        """
        self._rose_timer.stop()
        self._band_timer.stop()
        self._rose.hide()
        self._band.hide()

    def hit_test_rose(self, pos):
        """ Hit test the guide rose for the given position.

        The hit test is performed using the current rose mode.

        Parameters
        ----------
        pos : QPoint
            The position to hit test, expressed in the coordinate
            system of the owner dock area.

        Returns
        -------
        result : QGuideRose.Guide
            The guide enum which lies under the given point.

        """
        rose = self._rose
        return rose.hitTest(pos, rose.mode())

    def hover(self, area, pos):
        """ Update the overlays based on the mouse hover position.

        Parameters
        ----------
        area : QDockArea
            The dock area that is being hovered.

        pos : QPoint
            The hover position, expressed in the coordinate system
            of the owner dock area.

        """
        rose = self._rose
        Mode = QGuideRose.Mode

        # Special case the hover when the dock area has no docked items.
        # No hit testing is necessary when using the single center mode.
        if not area.layout().hasItems():
            self._hover_pos = pos
            center = QPoint(area.width() / 2, area.height() / 2)
            rose.setMode(Mode.SingleCenter)
            rose.setCenter(center)
            rose.hover(pos)
            guide = rose.hitTest(pos, Mode.SingleCenter)
            origin = area.mapToGlobal(QPoint(0, 0))
            if guide != self._last_guide:
                self._last_guide = guide
                if guide == QGuideRose.Guide.SingleCenter:
                    m = area.contentsMargins()
                    g = QRect(origin, area.size())
                    g = g.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
                    self._target_band_geo = g
                else:
                    self._target_band_geo = QRect()
                self._band_timer.start(self.band_delay)
            if rose.isHidden():
                rose.setGeometry(QRect(origin, area.size()))
                rose.show()
            return

        # Compute the target mode for the guide rose based on the
        # area lying under the hover position.
        widget = area.layout().hitTest(pos)
        if isinstance(widget, (QDockItem, QTabWidget)):
            center = widget.mapTo(area, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
            target_mode = Mode.Compass
        elif isinstance(widget, QSplitterHandle):
            if widget.orientation() == Qt.Horizontal:
                target_mode = Mode.SplitHorizontal
            else:
                target_mode = Mode.SplitVertical
            center = widget.mapTo(area, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
        else:
            target_mode = Mode.NoMode
            center = QPoint()

        # Update the state of the rose. If it is to be hidden, it is
        # done so immediately. If the target mode is different from
        # the current mode, the rose is hidden and the state change
        # is collapsed on a timer.
        self._hover_pos = pos
        self._target_rose_mode = target_mode
        if target_mode == Mode.NoMode:
            self._rose_timer.stop()
            rose.setMode(target_mode)
        elif target_mode != rose.mode():
            rose.setMode(Mode.NoMode)
            self._rose_timer.start(self.rose_delay)
        rose.setCenter(center)

        # Hit test the rose and update the target geometry for the
        # rubber band if the target guide has changed.
        update_band = False
        guide = rose.hitTest(pos, target_mode)
        if guide != self._last_guide:
            self._last_guide = guide
            border = self.border_size
            self._target_band_geo = band_geometry(area, widget, guide, border)
            update_band = True

        # If the rose is currently visible, pass it the hover event so
        # that it can trigger a repaint of the guides if needed. Queue
        # an update for the band geometry which prevents the band from
        # flickering when rapidly cycling between guide pads.
        if rose.mode() != Mode.NoMode:
            rose.hover(pos)
            if update_band:
                self._band_timer.start(self.band_delay)

        # Ensure that the rose is shown on the screen.
        if rose.isHidden():
            origin = area.mapToGlobal(QPoint(0, 0))
            rose.setGeometry(QRect(origin, area.size()))
            rose.show()
