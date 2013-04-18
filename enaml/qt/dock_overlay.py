#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QRect, QTimer, QPropertyAnimation
from PyQt4.QtGui import QRubberBand, QSplitterHandle, QTabWidget

from atom.api import Atom, Int, Float, Typed

from .q_guide_rose import QGuideRose
from .q_dock_container import QDockContainer


class DockOverlay(Atom):
    """ An object which manages the overlays for dock widgets.

    This manager handles the state transitions for the overlays. The
    transitions are performed on a slightly-delayed timer to provide
    a more fluid user interaction experience.

    """
    #: The size of the rubber band when docking on the border, in px.
    border_size = Int(60)

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
        rose.mouseOver(self._hover_pos)
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
            else:
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

    def _band_geometry(self, widget, guide):
        """ Compute the geometry for an overlay rubber band.

        Parameters
        ----------
        widget : QWidget
            The widget to which the band geometry should be fit.

        guide : QGuideRose.Guide
            The rose guide under the mouse. This determines how the
            geometry of the band will be fit to the widget.

        """
        Guide = QGuideRose.Guide
        if guide == Guide.NoGuide:
            return QRect()

        # border hits
        border_size = self.border_size
        rect = widget.contentsRect()
        if guide == Guide.BorderNorth:
            rect.setHeight(border_size)
        elif guide == Guide.BorderEast:
            rect.setLeft(rect.right() + 1 - border_size)
        elif guide == Guide.BorderSouth:
            rect.setTop(rect.bottom() + 1 - border_size)
        elif guide == Guide.BorderWest:
            rect.setWidth(border_size)

        # compass hits
        elif guide == Guide.CompassNorth:
            rect.setHeight(rect.height() / 3)
        elif guide == Guide.CompassEast:
            rect.setLeft(2 * rect.width() / 3)
        elif guide == Guide.CompassSouth:
            rect.setTop(2 * rect.height() / 3)
        elif guide == Guide.CompassWest:
            rect.setWidth(rect.width() / 3)
        elif guide == Guide.CompassCenter:
            pass  # nothing to do

        # splitter handle hits
        elif guide == Guide.SplitHorizontal:
            wo, r = divmod(border_size - rect.width(), 2)
            rect.setWidth(2 * (wo + r) + rect.width())
            rect.moveLeft(rect.x() - (wo + r))
        elif guide == Guide.SplitVertical:
            ho, r = divmod(border_size - widget.height(), 2)
            rect.setHeight(2 * (ho + r) + rect.height())
            rect.moveTop(rect.y() - (ho + r))

        # single center
        elif guide == Guide.SingleCenter:
            pass  # nothing to do

        # default no-op
        else:
            return QRect()

        pt = widget.mapToGlobal(rect.topLeft())
        return QRect(pt, rect.size())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def guide_at(self, pos):
        """ Get the dock guide for a given position.

        Parameters
        ----------
        pos : QPoint
            The position of interest, expressed in the coordinates of
            the overlay.

        Returns
        -------
        result : QGuideRose.Guide
            The guide enum which lies under the given point.

        """
        rose = self._rose
        return rose.guideAt(pos, rose.mode())

    def hide(self):
        """ Hide the overlay.

        This method will stop the timers and set the visibility of the
        guide rose and the rubber band to False.

        """
        self._rose_timer.stop()
        self._band_timer.stop()
        self._rose.hide()
        self._band.hide()

    def mouse_over_widget(self, widget, pos, empty=False):
        """ Update the overlays based on the mouse position.

        This handler should be invoked when the mouse hovers over a
        single widget (such as a floating dock container) as opposed to
        an area of docked widgets. The guide rose will be displayed in
        the center of the widget with no border guides.

        Parameters
        ----------
        widget : QWidget
            The widget under the mouse.

        pos : QPoint
            The hover position, expressed in the local coordinates of
            the widget.

        empty : bool, optional
            Whether the widget represents an empty widget. If this is
            True, a single center guide will be shown instead of the
            guide rose.

        """
        rose = self._rose
        Mode = QGuideRose.Mode
        target_mode = Mode.SingleCenter if empty else Mode.CompassOnly
        self._target_rose_mode = target_mode
        if rose.mode() != target_mode:
            rose.setMode(Mode.NoMode)
            self._rose_timer.start(self.rose_delay)
        origin = widget.mapToGlobal(QPoint(0, 0))
        geo = QRect(origin, widget.size())
        dirty = rose.geometry() != geo
        if dirty:
            rose.hide()
            rose.setMode(Mode.NoMode)
            rose.setGeometry(geo)
        guide = rose.guideAt(pos, target_mode)
        if dirty or guide != self._last_guide:
            self._last_guide = guide
            self._target_band_geo = self._band_geometry(widget, guide)
            self._band_timer.start(self.band_delay)
        rose.setCenter(QPoint(geo.width() / 2, geo.height() / 2))
        rose.mouseOver(pos)
        rose.show()

    def mouse_over(self, area, widget, pos):
        """ Update the overlays based on the mouse position.

        Parameters
        ----------
        area : QDockArea
            The dock area being overlayed.

        widget : QWidget
            The dock widget in the area which is under the mouse, or
            None if there is no such relevant widget.

        pos : QPoint
            The hover position, expressed in the local coordinates of
            the overlayed dock area.

        """
        rose = self._rose
        Mode = QGuideRose.Mode
        Guide = QGuideRose.Guide
        origin = area.mapToGlobal(QPoint(0, 0))
        rose.setGeometry(QRect(origin, area.size()))

        # Compute the target mode for the guide rose based on the dock
        # widget which lies under the mouse position.
        if isinstance(widget, (QDockContainer, QTabWidget)):
            center = widget.mapTo(area, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
            target_mode = Mode.Compass
            if area is widget:
                target_mode = Mode.CompassOnly
        elif isinstance(widget, QSplitterHandle):
            if widget.orientation() == Qt.Horizontal:
                target_mode = Mode.SplitHorizontal
            else:
                target_mode = Mode.SplitVertical
            center = widget.mapTo(area, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
        else:
            target_mode = Mode.BorderOnly
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
            rose.setMode(Mode.BorderOnly)
            self._rose_timer.start(self.rose_delay)
        rose.setCenter(center)

        # Hit test the rose and update the target geometry for the
        # rubber band if the target guide has changed.
        update_band = False
        guide = rose.guideAt(pos, target_mode)
        if guide != self._last_guide:
            self._last_guide = guide
            if guide >= Guide.BorderNorth and guide <= Guide.BorderWest:
                bgeo = self._band_geometry(area, guide)
            else:
                bgeo = self._band_geometry(widget, guide)
            self._target_band_geo = bgeo
            update_band = True

        # If the rose is currently visible, pass it the hover event so
        # that it can trigger a repaint of the guides if needed. Queue
        # an update for the band geometry which prevents the band from
        # flickering when rapidly cycling between guide pads.
        if rose.mode() != Mode.NoMode:
            rose.mouseOver(pos)
            if update_band:
                self._band_timer.start(self.band_delay)

        # Ensure that the rose and band are shown if hidden.
        if rose.isHidden():
            rose.show()
            self._band_timer.start(self.band_delay)
