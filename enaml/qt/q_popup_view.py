#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, Float, Int, IntEnum

from .QtCore import (
    Qt, QPoint, QPointF, QSize, QRect,QMargins, QPropertyAnimation, QTimer,
    QEvent, Signal
)
from .QtGui import (
    QApplication, QWidget, QLayout, QPainter, QPainterPath, QRegion, QPen,
    QCursor
)

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
    #: The anchor location on the view. The default anchors
    #: the top center of the view to the center of the parent.
    anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.0))

    #: The anchor location on the parent. The default anchors
    #: the top center of the view to the center of the parent.
    parent_anchor = Typed(QPointF, factory=lambda: QPointF(0.5, 0.5))

    #: The offset of the popup view with respect to the anchor.
    offset = Typed(QPoint, factory=lambda: QPoint(0, 0))

    #: The mode to use when computing the anchored position.
    anchor_mode = Typed(AnchorMode, factory=lambda: AnchorMode.Parent)

    #: The edge location of the arrow for the view.
    arrow_edge = Typed(ArrowEdge, factory=lambda: ArrowEdge.Left)

    #: The size of the arrow for the view.
    arrow_size = Int(0)

    #: The position of the arrow for the view.
    arrow_position = Float(0.5)

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


class LayoutData(Atom):
    """ An object which holds the data for popup view layout.

    """
    #: The position of the popup view.
    pos = Typed(QPoint)

    #: The size of the popup view.
    size = Typed(QSize)

    #: The size of the arrow in pixels.
    arrow_size = Int(0)

    #: The edge location of the arrow.
    arrow_edge = Typed(ArrowEdge)

    #: The position of the arrow on the edge.
    arrow_position = Float(0.0)


def make_path(layout_data):
    """ Create the painter path for the arrow.

    Parameters
    ----------
    layout_data : LayoutData
        The layout data object describing the path to generate.

    Returns
    -------
    result : QPainterPath
        The painter path for the view.

    """
    def arrow_offset(length, height, pos):
        base = 2 * height
        pos = max(0.0, min(1.0, pos))
        base = min(length, base)
        return int(pos * (length - base)) + base / 2
    arrow_size = layout_data.arrow_size
    arrow_pos = layout_data.arrow_position
    edge = layout_data.arrow_edge
    w = layout_data.size.width()
    h = layout_data.size.height()
    path = QPainterPath()
    if arrow_size <= 0:
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.lineTo(0, 0)
    elif edge == ArrowEdge.Bottom:
        offset = arrow_offset(w, arrow_size, arrow_pos)
        ledge = h - arrow_size
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, ledge)
        path.lineTo(offset + arrow_size, ledge)
        path.lineTo(offset, h)
        path.lineTo(offset - arrow_size, ledge)
        path.lineTo(0, ledge)
        path.lineTo(0, 0)
    elif edge == ArrowEdge.Top:
        offset = arrow_offset(w, arrow_size, arrow_pos)
        path.moveTo(0, arrow_size)
        path.lineTo(offset - arrow_size, arrow_size)
        path.lineTo(offset, 0)
        path.lineTo(offset + arrow_size, arrow_size)
        path.lineTo(w, arrow_size)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.lineTo(0, arrow_size)
    elif edge == ArrowEdge.Left:
        offset = arrow_offset(h, arrow_size, arrow_pos)
        path.moveTo(arrow_size, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)
        path.lineTo(arrow_size, h)
        path.lineTo(arrow_size, offset + arrow_size)
        path.lineTo(0, offset)
        path.lineTo(arrow_size, offset - arrow_size)
        path.lineTo(arrow_size, 0)
    else:
        offset = arrow_offset(h, arrow_size, arrow_pos)
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


def edge_margins(size, edge):
    """ Get the contents margins for a given arrow size and edge.

    Parameters
    ----------
    size : int
        The size of the arrow in pixels.

    edge : ArrowEdge
        The edge location of the arrow.

    """
    margins = QMargins()
    if size > 0:
        if edge == ArrowEdge.Right:
            margins.setRight(size)
        elif edge == ArrowEdge.Bottom:
            margins.setBottom(size)
        elif edge == ArrowEdge.Left:
            margins.setLeft(size)
        else:
            margins.setTop(size)
    return margins


def target_global_pos(parent, mode, anchor):
    """ Get the global position of the parent anchor.

    Parameters
    ----------
    parent : QWidget or None
        The parent widget for the view.

    mode : AnchorMode
        The anchor mode for the view.

    anchor : QPoint
        The anchor location on the parent.

    Returns
    -------
    result : QPoint
        The global coordinates of the target parent anchor.

    """
    if mode == AnchorMode.Cursor:
        origin = QCursor.pos()
        size = QSize()
    else:
        if parent is None:
            desktop = QApplication.desktop()
            geo = desktop.availableGeometry()
            origin = geo.topLeft()
            size = geo.size()
        else:
            origin = parent.mapToGlobal(QPoint(0, 0))
            size = parent.size()
    px = int(anchor.x() * size.width())
    py = int(anchor.y() * size.height())
    return origin + QPoint(px, py)


def popup_offset(size, anchor, offset):
    """ Get the offset to apply to the target global pos.

    Parameters
    ----------
    size : QSize
        The size of the popup view.

    anchor : QPoint
        The anchor for the popup view.

    offset : QPoint
        The additional offset for the popup view.

    Returns
    -------
    result : QPoint
        The offset to apply to the global target position to
        move the popup to the correct location.

    """
    px = int(anchor.x() * size.width())
    py = int(anchor.y() * size.height())
    return QPoint(px, py) - offset


def arrow_tip_pos(layout_data):
    """ Compute the position of the arrow point.

    """
    pos = QPoint(layout_data.pos)
    size = layout_data.size
    width = size.width()
    height = size.height()
    arrow_edge = layout_data.arrow_edge
    arrow_pos = layout_data.arrow_position
    if arrow_edge == ArrowEdge.Top:
        pos += QPoint(width * arrow_pos, 0)
    elif arrow_edge == ArrowEdge.Right:
        pos += QPoint(width, height * arrow_pos)
    elif arrow_edge == ArrowEdge.Bottom:
        pos += QPoint(width * arrow_pos, height)
    else:
        pos += QPoint(0, height * arrow_pos)
    return pos


def ensure_on_screen(layout_data):
    """

    """
    return False
    # tip_pos = arrow_tip_pos(layout_data)
    # screen_geo = QApplication.desktop().availableGeometry(tip_pos)
    # view_geo = QRect(layout_data.pos, layout_data.size)
    # if screen_geo.contains(view_geo):
    #     return False
    # sides = []
    # size = layout_data.size
    # if _test_top(view_geo, )
    # if view_geo.width() > screen_geo.width():
    #     return False
    # if view_geo.height() > screen_geo.height():
    #     return False
    # if view_geo.x() < screen_geo.x():
    #     dx = screen_geo.x() - view_geo.x()




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
            self._refreshGeometry()

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
                #self._updatePosition()
                self._refreshGeometry()
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
        self._refreshGeometry()

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

        # Compute the margins as specified by the state.
        state = self._state
        arrow_edge = state.arrow_edge
        arrow_size = state.arrow_size
        margins = edge_margins(arrow_size, arrow_edge)

        # Compute the hypothetical view size.
        self.setContentsMargins(margins)
        size = self.size()

        # Compute the hypothetical view position.
        anchor_mode = state.anchor_mode
        parent_anchor = state.parent_anchor
        pos = target_global_pos(self.parent(), anchor_mode, parent_anchor)
        pos -= popup_offset(size, state.anchor, state.offset)

        # Create the layout data and ensure it the view is on screen.
        layout_data = LayoutData()
        layout_data.pos = pos
        layout_data.size = size
        layout_data.arrow_size = arrow_size
        layout_data.arrow_edge = arrow_edge
        layout_data.arrow_position = state.arrow_position
        changed = ensure_on_screen(layout_data)

        # If the layout has changed, apply the update.
        if changed:
            arrow_size = layout_data.arrow_size
            arrow_edge = layout_data.arrow_edge
            margins = edge_margins(arrow_size, arrow_edge)
            self.setContentsMargins(margins)
            layout_data.size = self.size()

        # Compute the painter path for the view and set the mask.
        path = make_path(layout_data)
        state.path = path
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        # Move the widget into position and update it. The update is
        # necessary in the case where only the mask has changed, which
        # does not automatically generate a paint event.
        self.move(layout_data.pos)
        self.update()
