#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Bool, Typed, Float, Int, IntEnum

from .QtCore import (
    Qt, QPoint, QPointF, QSize, QRect,QMargins, QPropertyAnimation, QTimer,
    QEvent, Signal
)
from .QtGui import (
    QPainter, QPainterPath, QRegion, QPen, QCursor, QTransform
)
from .QtWidgets import QApplication, QWidget, QLayout

from .q_single_widget_layout import QSingleWidgetLayout


class AnchorMode(IntEnum):
    """ An IntEnum defining the various popup anchor modes.

    """
    #: Anchor to the parent widget.
    Parent = 0

    #: Anchor to current snapped mouse position.
    Cursor = 1


class ArrowEdge(IntEnum):
    """ An IntEnum defining the edge location of the popup arrow.

    """
    #: The left edge of the popup view.
    Left = 0

    #: The right edge of the popup view.
    Right = 1

    #: The top edge of the popup view.
    Top = 2

    #: The bottom edge of the popup view.
    Bottom = 3


class PopupState(Atom):
    """ A class which maintains the public state for a popup view.

    """
    #: The mode to use when computing the anchored position.
    anchor_mode = Typed(AnchorMode, factory=lambda: AnchorMode.Parent)

    #: The anchor location on the parent. The default anchors
    #: the top center of the view to the center of the parent.
    parent_anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.5))

    #: The anchor location on the view. The default anchors
    #: the top center of the view to the center of the parent.
    anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.0))

    #: The offset of the popup view with respect to the anchor.
    offset = Typed(QPoint, factory=lambda: QPoint(0, 0))

    #: The edge location of the arrow for the view.
    arrow_edge = Typed(ArrowEdge, factory=lambda: ArrowEdge.Left)

    #: The size of the arrow for the view.
    arrow_size = Int(0)

    #: The timeout value to use when closing the view, in seconds.
    timeout = Float(0.0)

    #: The duration for the fade in.
    fade_in_duration = Int(100)

    #: The duration for the fade out.
    fade_out_duration = Int(100)

    #: The computed path to use when drawing the view.
    path = Typed(QPainterPath, factory=lambda: QPainterPath())

    #: The animator to use when showing the view.
    fade_in_animator = Typed(QPropertyAnimation, ())

    #: The animator to use when hiding the view.
    fade_out_animator = Typed(QPropertyAnimation, ())

    #: The timeout timer to use for closing the view.
    close_timer = Typed(QTimer, ())

    #: Whether or not the view closes on click.
    close_on_click = Bool(True)

    #: Whether or not the view is currently in a resize event.
    in_resize_event = Bool(False)

    def init(self, widget):
        """ Initialize the state for the owner widget.

        """
        fade_in = self.fade_in_animator
        fade_in.setTargetObject(widget)
        fade_in.setPropertyName(b'windowOpacity')
        fade_out = self.fade_out_animator
        fade_out.setTargetObject(widget)
        fade_out.setPropertyName(b'windowOpacity')
        fade_out.finished.connect(widget.close)
        close_timer = self.close_timer
        close_timer.setSingleShot(True)
        close_timer.timeout.connect(widget.close)


def make_path(size, arrow_size, arrow_edge, offset):
    """ Create the painter path for the view with an edge arrow.

    Parameters
    ----------
    size : QSize
        The size of the view.

    arrow_size : int
        The size of the arrow.

    arrow_edge : ArrowEdge
        The edge location of the arrow.

    offset : int
        The offset along the arrow edge to the arrow center.

    Returns
    -------
    result : QPainterPath
        The painter path for the view.

    """
    w = size.width()
    h = size.height()
    path = QPainterPath()
    if arrow_size <= 0:
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.lineTo(0, 0)
    elif arrow_edge == ArrowEdge.Bottom:
        ledge = h - arrow_size
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, ledge)
        path.lineTo(offset + arrow_size, ledge)
        path.lineTo(offset, h)
        path.lineTo(offset - arrow_size, ledge)
        path.lineTo(0, ledge)
        path.lineTo(0, 0)
    elif arrow_edge == ArrowEdge.Top:
        path.moveTo(0, arrow_size)
        path.lineTo(offset - arrow_size, arrow_size)
        path.lineTo(offset, 0)
        path.lineTo(offset + arrow_size, arrow_size)
        path.lineTo(w, arrow_size)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.lineTo(0, arrow_size)
    elif arrow_edge == ArrowEdge.Left:
        path.moveTo(arrow_size, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)
        path.lineTo(arrow_size, h)
        path.lineTo(arrow_size, offset + arrow_size)
        path.lineTo(0, offset)
        path.lineTo(arrow_size, offset - arrow_size)
        path.lineTo(arrow_size, 0)
    else:
        ledge = w - arrow_size
        path.moveTo(0, 0)
        path.lineTo(ledge, 0)
        path.lineTo(ledge, offset - arrow_size)
        path.lineTo(w, offset)
        path.lineTo(ledge, offset + arrow_size)
        path.lineTo(ledge, h)
        path.lineTo(0, h)
        path.lineTo(0, 0)
    return path


def edge_margins(arrow_size, arrow_edge):
    """ Get the contents margins for a given arrow size and edge.

    Parameters
    ----------
    arrow_size : int
        The size of the arrow in pixels.

    arrow_edge : ArrowEdge
        The edge location of the arrow.

    Returns
    -------
    result : QMargins
        The contents margins for the given arrow spec.

    """
    margins = QMargins()
    if arrow_size > 0:
        if arrow_edge == ArrowEdge.Right:
            margins.setRight(arrow_size)
        elif arrow_edge == ArrowEdge.Bottom:
            margins.setBottom(arrow_size)
        elif arrow_edge == ArrowEdge.Left:
            margins.setLeft(arrow_size)
        else:
            margins.setTop(arrow_size)
    return margins


def is_fully_on_screen(rect):
    """ Get whether or not a rect is fully contained on the screen.

    Parameters
    ----------
    rect : QRect
        The rect of interest.

    Returns
    -------
    result : bool
        True if the rect is fully contained on the screen, False
        otherwise.

    """
    desktop = QApplication.desktop()
    desk_geo = desktop.availableGeometry(rect.topLeft())
    if not desk_geo.contains(rect.topLeft()):
        return False
    desk_geo = desktop.availableGeometry(rect.topRight())
    if not desk_geo.contains(rect.topRight()):
        return False
    desk_geo = desktop.availableGeometry(rect.bottomLeft())
    if not desk_geo.contains(rect.bottomLeft()):
        return False
    desk_geo = desktop.availableGeometry(rect.bottomRight())
    if not desk_geo.contains(rect.bottomRight()):
        return False
    return True


def left_screen_edge(desktop, rect):
    """ Get the x-coordinate of the effective left screen edge.

    Parameters
    ----------
    desktop : QDesktopWidget
        The desktop widget for the application.

    rect : QRect
        The rect of interest.

    Returns
    -------
    result : int
        the x-coordinate of the effective left screen edge.

    """
    p1 = rect.topLeft()
    p2 = rect.bottomLeft()
    g1 = desktop.availableGeometry(p1)
    g2 = desktop.availableGeometry(p2)
    return max(p1.x(), g1.left(), g2.left())


def right_screen_edge(desktop, rect):
    """ Get the x-coordinate of the effective right screen edge.

    Parameters
    ----------
    desktop : QDesktopWidget
        The desktop widget for the application.

    rect : QRect
        The rect of interest.

    Returns
    -------
    result : int
        the x-coordinate of the effective right screen edge.

    """
    p1 = rect.topRight()
    p2 = rect.bottomRight()
    g1 = desktop.availableGeometry(p1)
    g2 = desktop.availableGeometry(p2)
    return min(p1.x(), g1.right(), g2.right())


def top_screen_edge(desktop, rect):
    """ Get the y-coordinate of the effective top screen edge.

    Parameters
    ----------
    desktop : QDesktopWidget
        The desktop widget for the application.

    rect : QRect
        The rect of interest.

    Returns
    -------
    result : int
        the y-coordinate of the effective top screen edge.

    """
    p1 = rect.topLeft()
    p2 = rect.topRight()
    g1 = desktop.availableGeometry(p1)
    g2 = desktop.availableGeometry(p2)
    return max(p1.y(), g1.top(), g2.top())


def bottom_screen_edge(desktop, rect):
    """ Get the y-coordinate of the effective bottom screen edge.

    Parameters
    ----------
    desktop : QDesktopWidget
        The desktop widget for the application.

    rect : QRect
        The rect of interest.

    Returns
    -------
    result : int
        the y-coordinate of the effective bottom screen edge.

    """
    p1 = rect.bottomLeft()
    p2 = rect.bottomRight()
    g1 = desktop.availableGeometry(p1)
    g2 = desktop.availableGeometry(p2)
    return min(p1.y(), g1.bottom(), g2.bottom())


def ensure_on_screen(rect):
    """ Ensure that the given rectangle is fully on-screen.

    If the given rectangle does fit on the screen its position will be
    adjusted so that it fits on screen as close as possible to its
    original position. Rects which are bigger than the screen size
    will necessarily still incur clipping.

    Parameters
    ----------
    rect : QRect
        The global geometry rectangle of interest.

    Returns
    -------
    result : QRect
        A potentially adjust rect which best fits on the screen.

    """
    rect = QRect(rect)
    desktop = QApplication.desktop()
    desk_geo = desktop.availableGeometry(rect.topLeft())
    if desk_geo.contains(rect):
        return rect
    bottom_edge = bottom_screen_edge(desktop, rect)
    if rect.bottom() > bottom_edge:
        rect.moveBottom(bottom_edge)
    right_edge = right_screen_edge(desktop, rect)
    if rect.right() > right_edge:
        rect.moveRight(right_edge)
    top_edge = top_screen_edge(desktop, rect)
    if rect.top() < top_edge:
        rect.moveTop(top_edge)
    left_edge = left_screen_edge(desktop, rect)
    if rect.left() < left_edge:
        rect.moveLeft(left_edge)
    return rect


def adjust_arrow_rect(rect, arrow_edge, target_pos, offset):
    """ Adjust an arrow rectangle to fit on the screen.

    Parameters
    ----------
    rect : QRect
        The rect of interest.

    arrow_edge : ArrowEdge
        The edge on which the arrow will be rendered.

    target_pos : QPoint
        The global target position of the parent anchor.

    offset : QPoint
        The offset to apply to the parent anchor.

    Returns
    -------
    result : tuple
        A 4-tuple of (QRect, ArrowEdge, int, int) which represent the
        adjusted rect, the new arrow edge, and x and y deltas to apply
        to the arrow position.

    """
    ax = ay = 0
    rect = QRect(rect)
    desktop = QApplication.desktop()

    if arrow_edge == ArrowEdge.Left:
        bottom_edge = bottom_screen_edge(desktop, rect)
        if rect.bottom() > bottom_edge:
            ay += rect.bottom() - bottom_edge
            rect.moveBottom(bottom_edge)
        top_edge = top_screen_edge(desktop, rect)
        if rect.top() < top_edge:
            ay -= top_edge - rect.top()
            rect.moveTop(top_edge)
        left_edge = left_screen_edge(desktop, rect)
        if rect.left() < left_edge:
            rect.moveLeft(left_edge)
        right_edge = right_screen_edge(desktop, rect)
        if rect.right() > right_edge:
            arrow_edge = ArrowEdge.Right
            right = target_pos.x() - offset.x()
            rect.moveRight(min(right, right_edge))

    elif arrow_edge == ArrowEdge.Top:
        right_edge = right_screen_edge(desktop, rect)
        if rect.right() > right_edge:
            ax += rect.right() - right_edge
            rect.moveRight(right_edge)
        left_edge = left_screen_edge(desktop, rect)
        if rect.left() < left_edge:
            ax -= left_edge - rect.left()
            rect.moveLeft(left_edge)
        top_edge = top_screen_edge(desktop, rect)
        if rect.top() < top_edge:
            rect.moveTop(top_edge)
        bottom_edge = bottom_screen_edge(desktop, rect)
        if rect.bottom() > bottom_edge:
            arrow_edge = ArrowEdge.Bottom
            bottom = target_pos.y() - offset.y()
            rect.moveBottom(min(bottom, bottom_edge))

    elif arrow_edge == ArrowEdge.Right:
        bottom_edge = bottom_screen_edge(desktop, rect)
        if rect.bottom() > bottom_edge:
            ay += rect.bottom() - bottom_edge
            rect.moveBottom(bottom_edge)
        top_edge = top_screen_edge(desktop, rect)
        if rect.top() < top_edge:
            ay -= top_edge - rect.top()
            rect.moveTop(top_edge)
        right_edge = right_screen_edge(desktop, rect)
        if rect.right() > right_edge:
            rect.moveRight(right_edge)
        left_edge = left_screen_edge(desktop, rect)
        if rect.left() < left_edge:
            arrow_edge = ArrowEdge.Left
            left = target_pos.x() - offset.x()
            rect.moveLeft(max(left, left_edge))

    else:  # ArrowEdge.Bottom
        right_edge = right_screen_edge(desktop, rect)
        if rect.right() > right_edge:
            ax += rect.right() - right_edge
            rect.moveRight(right_edge)
        left_edge = left_screen_edge(desktop, rect)
        if rect.left() < left_edge:
            ax -= left_edge - rect.left()
            rect.moveLeft(left_edge)
        bottom_edge = bottom_screen_edge(desktop, rect)
        if rect.bottom() > bottom_edge:
            rect.moveBottom(bottom_edge)
        top_edge = top_screen_edge(desktop, rect)
        if rect.top() < top_edge:
            arrow_edge = ArrowEdge.Top
            top = target_pos.y() - offset.y()
            rect.moveTop(max(top, top_edge))

    return rect, arrow_edge, ax, ay


class QPopupView(QWidget):
    """ A custom QWidget which implements a framless popup widget.

    It is useful for showing transient configuration dialogs as well
    as temporary notification windows.

    """
    #: A signal emitted when the popup is fully closed.
    closed = Signal()

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
        self._state = PopupState()
        self._state.init(self)
        if parent is not None:
            parent.installEventFilter(self)
            if not parent.isWindow():
                parent.window().installEventFilter(self)

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
            self._refreshGeometry()

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
            self._refreshGeometry()

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
            self._refreshGeometry()

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
            self._refreshGeometry()

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
            self._refreshGeometry()

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
            self._refreshGeometry()

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

    def closeOnClick(self):
        """ Get whether or not close on click is enabled.

        Returns
        -------
        result : bool
            True if close on click is enabled, False otherwise. The
            default value is True.

        """
        return self._state.close_on_click

    def setCloseOnClick(self, enable):
        """ Set whether or not close on click is enabled.

        Parameters
        ----------
        enable : bool
            True if close on click should be enabled, False otherwise.

        """
        self._state.close_on_click = enable

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
            self._refreshGeometry()
        return False

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the popup view.

        This handler ensures that the window is closed in the proper
        cases, when the superclass method doesn't handle it.

        """
        event.ignore()
        state = self._state
        if state.close_on_click:
            path = state.path
            pos = event.pos()
            rect = self.rect()
            win_type = self.windowType()
            if win_type == Qt.Popup:
                if not rect.contains(pos):
                    super(QPopupView, self).mousePressEvent(event)
                else:
                    path = state.path
                    if not path.isEmpty() and not path.contains(pos):
                        event.accept()
                        self.close()
            elif win_type == Qt.ToolTip or win_type == Qt.Window:
                if path.isEmpty() or path.contains(pos):
                    event.accept()
                    self.close()

    def showEvent(self, event):
        """ Handle the show event for the popup view.

        This handler starts the fade in animation and the timer which
        manages the timeout for the popup.

        """
        self._refreshGeometry(force=True)
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
        if self._state.in_resize_event:
            return
        self._state.in_resize_event = True
        try:
            self._refreshGeometry()
        finally:
            self._state.in_resize_event = False

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
    def _refreshGeometry(self, force=False):
        """ Refresh the geometry for the popup using the current state.

        Parameters
        ----------
        force : bool, optional
            Wether or not to force the computation even if the view is
            not visible. The default is False.

        """
        if not force and not self.isVisible():
            return
        if self._state.arrow_size <= 0:
            self._layoutPlainRect()
        else:
            self._layoutArrowRect()

    def _layoutPlainRect(self):
        """ Layout the widget with no edge arrow.

        """
        self.setContentsMargins(QMargins())
        self.clearMask()
        target_pos = self._targetPos()
        anchor_pos = self._anchorPos()
        offset = self._state.offset
        trial_pos = target_pos + offset - anchor_pos
        trial_geo = QRect(trial_pos, self.size())
        geo = ensure_on_screen(trial_geo)
        self.setGeometry(geo)

    def _layoutArrowRect(self):
        """ Layout the widget with the edge arrow.

        """
        # Setup the initial contents margins.
        state = self._state
        arrow_size = state.arrow_size
        arrow_edge = state.arrow_edge
        margins = edge_margins(arrow_size, arrow_edge)
        self.setContentsMargins(margins)

        # Use the current size to compute the arrow position.
        ax = ay = 0
        size = self.size()
        anchor = state.anchor
        if arrow_edge == ArrowEdge.Left or arrow_edge == ArrowEdge.Right:
            ay = int(anchor.y() * size.height())
            ay = max(arrow_size, min(size.height() - arrow_size, ay))
            if arrow_edge == ArrowEdge.Right:
                ax = size.width()
        else:
            ax = int(anchor.x() * size.width())
            ax = max(arrow_size, min(size.width() - arrow_size, ax))
            if arrow_edge == ArrowEdge.Bottom:
                ay = size.height()

        # Compute the view rect and adjust it if it falls off screen.
        target_pos = self._targetPos()
        pos = target_pos + state.offset - QPoint(ax, ay)
        rect = QRect(pos, size)
        if not is_fully_on_screen(rect):
            rect, new_edge, d_ax, d_ay = adjust_arrow_rect(
                rect, arrow_edge, target_pos, state.offset
            )
            ax = max(arrow_size, min(size.width() - arrow_size, ax + d_ax))
            ay = max(arrow_size, min(size.height() - arrow_size, ay + d_ay))
            if new_edge != arrow_edge:
                arrow_edge = new_edge
                margins = edge_margins(arrow_size, new_edge)
                self.setContentsMargins(margins)

        # Use the final geometry to get the path for the arrow.
        if arrow_edge == ArrowEdge.Left or arrow_edge == ArrowEdge.Right:
            path = make_path(rect.size(), arrow_size, arrow_edge, ay)
        else:
            path = make_path(rect.size(), arrow_size, arrow_edge, ax)

        # Store the path for painting and update the widget mask.
        state.path = path
        mask = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(mask)

        # Set the geometry of the view and update. The update is needed
        # for the case where the only change was the widget mask, which
        # will not generate a paint event. Qt collapses paint events,
        # so the cost of this is minimal.
        self.setGeometry(rect)
        self.update()

    def _targetPos(self):
        """ Get the global position of the parent anchor.

        Returns
        -------
        result : QPoint
            The global coordinates of the target parent anchor.

        """
        state = self._state
        if state.anchor_mode == AnchorMode.Cursor:
            origin = QCursor.pos()
            size = QSize()
        else:
            parent = self.parent()
            if parent is None:
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

    def _anchorPos(self):
        """ Get the position of the anchor in local coordinates.

        Returns
        -------
        result : QPoint
            The anchor position on the view in local coordinates.

        """
        size = self.size()
        anchor = self._state.anchor
        px = int(anchor.x() * size.width())
        py = int(anchor.y() * size.height())
        return QPoint(px, py)
