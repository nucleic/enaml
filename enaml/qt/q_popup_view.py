#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, Float, Int

from .QtCore import (
    Qt, QPoint, QPointF, QSize, QMargins, QPropertyAnimation, QTimer, QEvent,
    Signal
)
from .QtGui import (
    QApplication, QWidget, QLayout, QPainter, QPainterPath, QRegion, QPen,
    QCursor
)

from .q_single_widget_layout import QSingleWidgetLayout


class QPopupView(QWidget):
    """ A custom QWidget which implements a framless popup widget.

    It is useful for showing transient configuration dialogs as well
    as temporary notification windows.

    """
    #: A signal emitted when the popup is fully closed.
    closed = Signal()

    #: The left edge of the popup view.
    LeftEdge = 0

    #: The right edge of the popup view.
    RightEdge = 1

    #: The top edge of the popup view.
    TopEdge = 2

    #: The bottom edge of the popup view.
    BottomEdge = 3

    #: Anchor to parent (which can be None)
    AnchorParent = 0

    #: Anchor to mouse
    AnchorCursor = 1

    class ViewState(Atom):
        """ A private class used to manage the state of a popup view.

        """
        #: The anchor location on the view. The default anchors
        #: the top center of the view to the center of the parent.
        anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.0))

        #: The anchor location on the parent. The default anchors
        #: the top center of the view to the center of the parent.
        parent_anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.5))

        #: Anchor to parent or cursor
        anchor_mode = Int(0)  # AnchorParent

        #: The size of the arrow for the view.
        arrow_size = Int(0)

        #: The edge location of the arrow for the view.
        arrow_edge = Int(0)  # LeftEdge

        #: The position of the arrow for the view.
        arrow_position = Float(0.5)

        #: The offset of the view wrt to the anchor.
        offset = Typed(QPoint, factory=lambda: QPoint(0, 0))

        #: The timeout value to use when closing the view, in seconds.
        timeout = Float(0.0)

        #: The path to use when drawing the view.
        path = Typed(QPainterPath, factory=QPainterPath)

        #: The animator to use when showing the view.
        fade_in_animator = Typed(QPropertyAnimation, ())

        #: The animator to use when hiding the view.
        fade_out_animator = Typed(QPropertyAnimation, ())

        #: The duration for the fade in.
        fade_in_duration = Int(100)

        #: The duration for the fade out.
        fade_out_duration = Int(100)

        #: The timeout timer to use for closing the view.
        close_timer = Typed(QTimer, ())

        def init(self, widget):
            """ Initialize the state for the owner widget.

            """
            fade_in = self.fade_in_animator
            fade_in.setTargetObject(widget)
            fade_in.setPropertyName('windowOpacity')
            fade_out = self.fade_out_animator
            fade_out.setTargetObject(widget)
            fade_out.setPropertyName('windowOpacity')
            fade_out.finished.connect(widget.close)
            close_timer = self.close_timer
            close_timer.setSingleShot(True)
            close_timer.timeout.connect(widget.close)

    def __init__(self, parent=None, flags=Qt.Popup):
        """ Initialize a QPopupView.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the popup view.

        flags : Qt.WindowFlags, optional
            Additional window flags to use when creating the view.
            The default is Qt.Popup.

        """
        super(QPopupView, self).__init__(parent)
        self.setWindowFlags(flags | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QSingleWidgetLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self._state = self.ViewState()
        self._state.init(self)
        if parent is not None:
            parent.installEventFilter(self)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def centralWidget(self):
        """ Get the central widget for the popup view.

        Returns
        -------
        result : QWidget or None
            The central widget of the popup, or None if no widget
            was provided.

        """
        return self.layout().getWidget()

    def setCentralWidget(self, widget):
        """ Set the central widget for the popup view.

        Parameters
        ----------
        widget : QWidget or None.
            The widget to use as the content of the popup.

        """
        self.layout().setWidget(widget)

    def anchor(self):
        """ Get the anchor position for the popup view.

        Returns
        -------
        result : QPointF
            The anchor point for the view.

        """
        return self._state.anchor

    def setAnchor(self, anchor):
        """ Set the anchor position for the popup view.

        Parameters
        ----------
        anchor : QPointF
            The anchor point for the view.

        """
        state = self._state
        if anchor != state.anchor:
            state.anchor = anchor
            self._updatePosition()

    def anchorMode(self):
        """ Get the anchor mode for the popup view

        Returns
        -------
        result : int
            An enum value describing the anchor mode of the popup.

        """
        return self._state.anchor_mode

    def setAnchorMode(self, mode):
        """ Set the anchor mode for the popup view

        Parameters
        ----------
        mode : int
            The anchor mode (can be AnchorParent or AnchorCursor)

        """
        state = self._state
        if mode != state.anchor_mode:
            state.anchor_mode = mode
            self._updatePosition()

    def parentAnchor(self):
        """ Get the parent anchor position for the popup view.

        Returns
        -------
        result : QPointF
            The parent anchor point for the view.

        """
        return self._state.parent_anchor

    def setParentAnchor(self, anchor):
        """ Set the parent anchor position for the popup view.

        Parameters
        ----------
        anchor : QPointF
            The parent anchor point for the view.

        """
        state = self._state
        if anchor != state.parent_anchor:
            state.parent_anchor = anchor
            self._updatePosition()

    def arrowSize(self):
        """ Get the size of the popup arrow.

        Returns
        -------
        result : int
            The size of the arrow in pixels.

        """
        return self._arrow_size.height()

    def setArrowSize(self, size):
        """ Set size of the popup arrow.

        Parameters
        ----------
        size : int
            The size of the popup arrow, in pixels. A size of zero
            indicates that no arrow is to be used.

        """
        state = self._state
        if size != state.arrow_size:
            state.arrow_size = size
            self._updateMargins()
            self._updateMask()
            self._updatePosition()

    def arrowEdge(self):
        """ Get edge for the popup arrow.

        Returns
        -------
        result : int
            An enum value describing the edge location of the arrow.

        """
        return self._state.arrow_edge

    def setArrowEdge(self, edge):
        """ Set the edge for the popup arrow.

        Parameters
        ----------
        edge : int
            The enum describing the edge location of the arrow.

        """
        state = self._state
        if edge != state.arrow_edge:
            state.arrow_edge = edge
            self._updateMargins()
            self._updateMask()

    def arrowPosition(self):
        """ Get the position of the popup arrow.

        Returns
        -------
        result : float
            The position of the arrow along its edge.

        """
        return self._state.arrow_position

    def setArrowPosition(self, pos):
        """ Set the position of the popup arrow.

        Parameters
        ----------
        pos : float
            The position of the popup arrow along its edge.

        """
        state = self._state
        if pos != state.arrow_position:
            state.arrow_position = pos
            self._updateMask()  # This does not generate a paint event.
            if self.isVisible():
               self.update()

    def offset(self):
        """ Get the offset of the view from the anchors.

        Returns
        -------
        result : QPoint
            The offset of the view from the anchors.

        """
        return self._state.offset

    def setOffset(self, offset):
        """ Set the offset of the view from the anchors.

        Parameters
        ----------
        offset : QPoint
            The offset of the view from the anchors.

        """
        state = self._state
        if offset != state.offset:
            state.offset = offset
            self._updatePosition()

    def timeout(self):
        """ Get the timeout for the view.

        Returns
        -------
        result : float
            The timeout of the view, in seconds.

        """
        return self._state.timeout

    def setTimeout(self, timeout):
        """ Set the timeout for the view.

        Parameters
        ----------
        timeout : float
            The timeout for the view, in seconds.

        """
        self._state.timeout = timeout

    def fadeInDuration(self):
        """ Get the duration of the fade in for the view.

        Returns
        -------
        result : int
            The duration of the fade in, in milliseconds.

        """
        return self._state.fade_in_duration

    def setFadeInDuration(self, duration):
        """ Set the duration of the fade in for the view.

        Parameters
        ----------
        duration : int
            The duration of the fade in, in milliseconds.

        """
        self._state.fade_in_duration = duration

    def fadeOutDuration(self):
        """ Get the duration of the fade out for the view.

        Returns
        -------
        result : int
            The duration of the fade out, in milliseconds.

        """
        return self._state.fade_out_duration

    def setFadeOutDuration(self, duration):
        """ Set the duration of the fade out for the view.

        Parameters
        ----------
        duration : int
            The duration of the fade out, in milliseconds.

        """
        self._state.fade_out_duration = duration

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        """ Filter the events from the parent object.

        This handler ensures the position of the popup is updated
        when the parent is resized or moved.

        """
        evt_type = event.type()
        if evt_type == QEvent.Move or evt_type == QEvent.Resize:
            if obj is self.parent():
                self._updatePosition()
        return False

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the popup view.

        This handler ensures that the window is closed in the proper
        cases, when the superclass method doesn't handle it.

        """
        super(QPopupView, self).mousePressEvent(event)
        if self.isVisible():
            pos = event.pos()
            rect = self.rect()
            if rect.contains(pos):
                pt = QPointF(pos.x(), pos.y())
                win_type = self.windowType()
                if win_type == Qt.ToolTip:
                    if self._state.path.contains(pt):
                        event.accept()
                        self.close()
                elif win_type == Qt.Popup:
                    if not self._state.path.contains(pt):
                        event.accept()
                        self.close()

    def showEvent(self, event):
        """ Handle the show event for the popup view.

        This handler starts the fade in animation and the timer which
        manages the timeout for the popup.

        """
        state = self._state
        if state.timeout > 0.0:
            state.close_timer.start(int(state.timeout * 1000))
        duration = state.fade_in_duration
        if duration <= 0:
            return
        animator = state.fade_in_animator
        if animator.state() == QPropertyAnimation.Stopped:
            animator.setStartValue(0.0)
            animator.setEndValue(1.0)
            animator.setDuration(duration)
            animator.start()

    def closeEvent(self, event):
        """ Handle the close event for the popup view.

        This handler stops the timeout timer and the fade in animation
        and starts the fade out animation. Once the popup view is fully
        transparent, the close event is accepted.

        """
        event.ignore()
        state = self._state
        state.close_timer.stop()
        state.fade_in_animator.stop()
        duration = state.fade_out_duration
        if duration <= 0:
            event.accept()
            self.closed.emit()
            return
        animator = state.fade_out_animator
        if animator.state() == QPropertyAnimation.Stopped:
            opacity = self.windowOpacity()
            if opacity == 0.0:
                event.accept()
                self.closed.emit()
            else:
                animator.setStartValue(opacity)
                animator.setEndValue(0.0)
                animator.setDuration(duration)
                animator.start()

    def resizeEvent(self, event):
        """ Handle the resize event for the popup view.

        """
        super(QPopupView, self).resizeEvent(event)
        self._updateMask()
        self._updatePosition()

    def paintEvent(self, event):
        """ Handle the paint event for the popup view.

        """
        palette = self.palette()
        fill_color = palette.window().color()
        stroke_color = palette.windowText().color()
        painter = QPainter(self)
        painter.setBrush(fill_color)
        painter.setPen(QPen(stroke_color, 2))
        painter.setRenderHint(QPainter.Antialiasing)
        path = self._state.path
        if path.isEmpty():
            painter.drawRect(self.rect())
        else:
            painter.drawPath(path)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @staticmethod
    def _arrowOffset(length, height, pos):
        """ Compute the offset for an arrow from parameters.

        Parameters
        ----------
        length : int
            The length of the edge on which the arrow is being drawn.

        height : int
            The height of the arrow.

        pos : float
            The position of the arrow along the edge.

        Returns
        -------
        result : int
            The offset from the start of the edge to the center of
            the base of the arrow.

        """
        base = 2 * height
        pos = max(0.0, min(1.0, pos))
        base = min(length, base)
        return int(pos * (length - base)) + base / 2

    def _updateMargins(self):
        """ Update the contents margins for the popup view.

        """
        state = self._state
        margins = QMargins()
        if state.arrow_size > 0:
            size = state.arrow_size
            edge = state.arrow_edge
            if edge == QPopupView.RightEdge:
                margins.setRight(size)
            elif edge == QPopupView.BottomEdge:
                margins.setBottom(size)
            elif edge == QPopupView.LeftEdge:
                margins.setLeft(size)
            else:
                margins.setTop(size)
        self.setContentsMargins(margins)

    def _updateMask(self):
        """ Update the mask and painter path for the popup view.

        """
        size = self.size()
        state = self._state
        asize = state.arrow_size
        apos = state.arrow_position
        edge = state.arrow_edge
        path = QPainterPath()
        w = size.width()
        h = size.height()
        path = QPainterPath()
        if asize <= 0:
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.lineTo(0, 0)
        elif edge == QPopupView.BottomEdge:
            offset = self._arrowOffset(w, asize, apos)
            ledge = h - asize
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, ledge)
            path.lineTo(offset + asize, ledge)
            path.lineTo(offset, h)
            path.lineTo(offset - asize, ledge)
            path.lineTo(0, ledge)
            path.lineTo(0, 0)
        elif edge == QPopupView.TopEdge:
            offset = self._arrowOffset(w, asize, apos)
            path.moveTo(0, asize)
            path.lineTo(offset - asize, asize)
            path.lineTo(offset, 0)
            path.lineTo(offset + asize, asize)
            path.lineTo(w, asize)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.lineTo(0, asize)
        elif edge == QPopupView.LeftEdge:
            offset = self._arrowOffset(h, asize, apos)
            path.moveTo(asize, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(asize, h)
            path.lineTo(asize, offset + asize)
            path.lineTo(0, offset)
            path.lineTo(asize, offset - asize)
            path.lineTo(asize, 0)
        else:
            offset = self._arrowOffset(h, asize, apos)
            ledge = w - asize
            path.moveTo(0, 0)
            path.lineTo(ledge, 0)
            path.lineTo(ledge, offset - asize)
            path.lineTo(w, offset)
            path.lineTo(ledge, offset + asize)
            path.lineTo(ledge, h)
            path.lineTo(0, h)
            path.lineTo(0, 0)
        state.path = path
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def _targetGlobalPos(self):
        """ Get the global position of the parent anchor.

        Returns
        -------
        result : QPoint
            The global coordinates of the target parent anchor.

        """
        state = self._state
        if state.anchor_mode == QPopupView.AnchorCursor:
            origin = QCursor.pos()
            size = QSize()
        else:
            parent = self.parent()
            if parent is None:
                # FIXME expose something other than the primary screen.
                desktop = QApplication.desktop()
                geo = desktop.availableGeometry()
                origin = geo.topLeft()
                size = geo.size()
            else:
                origin = parent.mapToGlobal(QPoint(0, 0))
                size = parent.size()
        anchor = state.parent_anchor
        px = int(anchor.x() * size.width())
        py = int(anchor.y() * size.height())
        return origin + QPoint(px, py)

    def _popupOffset(self):
        """ Get the offset to apply to the target global pos.

        Returns
        -------
        result : QPoint
            The offset to apply to the global target position to
            move the popup to the correct location.

        """
        state = self._state
        size = self.size()
        anchor = state.anchor
        px = int(anchor.x() * size.width())
        py = int(anchor.y() * size.height())
        return QPoint(px, py) - state.offset

    def _updatePosition(self):
        """ Update the position of the popup view.

        """
        target = self._targetGlobalPos()
        offset = self._popupOffset()
        self.move(target - offset)
