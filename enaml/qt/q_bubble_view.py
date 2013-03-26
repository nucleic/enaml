#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QMargins, QEvent, pyqtSignal
from PyQt4.QtGui import QWidget, QLayout, QPainter, QPainterPath

from .q_single_widget_layout import QSingleWidgetLayout


class QBubbleView(QWidget):
    """ A Bubble popup widget.

    This widget implements a popup style with rounded corners and an
    arrow anchoring it to an underlying widget. Useful for transient
    dialogs.

    """
    #: A signal emitted when the popup is closed
    closed = pyqtSignal()

    #: Enum to specify BubbleView orientation
    AnchorTop = 0
    AnchorBottom = 1
    AnchorLeft = 2
    AnchorRight = 3

    def __init__(self, parent=None):
        super(QBubbleView, self).__init__(parent)
        self._central_widget = None

        # Set up the window flags to get a non-bordered window
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)

        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QSingleWidgetLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

        # Default anchoring and configuration options
        self.setAnchor(QBubbleView.AnchorBottom)
        self.setRelativePos((0.5, 0.5))
        self.setArrowSize(20)
        self.setRadius(10)

        # track parent window movement
        parent.window().installEventFilter(self)
        parent.destroyed.connect(self.deleteLater)

    def centralWidget(self):
        """ Returns the central widget for the popup.

        Returns
        -------
        result : QWidget or None
            The central widget of the popup, or None if no widget
            was provided.

        """
        return self._central_widget

    def setCentralWidget(self, widget):
        """ Set the central widget for this popup.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the content of the popup.

        """
        self._central_widget = widget
        self.layout().setWidget(widget)

    def setAnchor(self, anchor):
        """ Set the positioning of the popup relative to the parent widget.

        Parameters
        ----------
        anchor : int
            Can be one of AnchorLeft, AnchorRight, AnchorTop, AnchorBottom

        """
        if anchor not in (QBubbleView.AnchorLeft, QBubbleView.AnchorRight,
                          QBubbleView.AnchorTop, QBubbleView.AnchorBottom):
            err = "Anchor must be one of AnchorLeft, AnchorRight, " \
                  "AnchorTop, AnchorBottom"
            raise ValueError(err)

        self._anchor_type = anchor
        if self.isVisible():
            self._rebuild()

    def anchor(self):
        """ Return the relative positioning.

        Returns
        -------
        result : int
            An enum specifying the position relative to the parent widget.
            One of AnchorLeft, AnchorRight, AnchorTop, AnchorBottom

        """
        return self._anchor_type

    def setArrowSize(self, arrow):
        """ Set size of the arrow.

        Parameters
        ----------
        arrow : int
            The size of the arrow (in pixels). A size of zero indicates
            that no arrow is desired

        """
        if arrow < 0:
            raise ValueError("Arrow size must be greater than or equal to 0")
        self._arrow = QSize(arrow / 1.5, arrow)
        if self.isVisible():
            self._rebuild()

    def arrowSize(self):
        """ Return the size of the arrow.

        Returns
        -------
        result : int
            The size of the arrow (in pixels)

        """
        return self._arrow.height()

    def setRadius(self, radius):
        """ Set the radius of the popup corners.

        Parameters
        ----------
        radius : int
            The radius of the popup corners (in pixels). Must be greater
            than or equal to 2.

        """
        if radius < 2:
            raise ValueError("Radius must be greater than or equal to 2")
        self._radius = radius
        if self.isVisible():
            self._rebuild()

    def radius(self):
        """ Return the radius of the corners.

        Returns
        -------
        result : Int
            The radius of the popup corners (in pixels)

        """
        return self._radius

    def setRelativePos(self, pos):
        """ Set the relative position of the popup.

        This method sets the relative position of the anchor point (the
        tip of the arrow) relative the bounds of the parent widget.

        Parameters
        ----------
        pos : tuple
            A 2-tuple of the form ((0,1), (0,1) specifying the position
            of the popup coordindates relative to the parent widget's
            bounds. Each member of the tuple should be between 0 and 1
            inclusive.

        """
        self._relative_pos = pos
        if self.isVisible():
            self._rebuild()

    def relativePos(self):
        """ Return the relative position of the popup.

        Returns
        -------
        result : Tuple
            The relative anchoring of the popup relative to the parent
            widget's bounds

        """
        return self._relative_pos

    def paintEvent(self, event):
        """ Reimplement the paint event

        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = self.palette()
        painter.setPen(palette.dark().color())
        painter.setBrush(palette.window())
        painter.drawPath(self._path)

    def resizeEvent(self, event):
        """ Reimplement the resize event

        Rebuild the popup path used to paint the widget when the size of
        the popup changes.

        """
        self._rebuild()
        super(QBubbleView, self).resizeEvent(event)

    def closeEvent(self, event):
        """ Handle the QCloseEvent from the window system.

        By default, this handler calls the superclass' method to close
        the window and then emits the 'closed' signal.

        """
        super(QBubbleView, self).closeEvent(event)
        self.closed.emit()

    def eventFilter(self, obj, event):
        """ Track parent window move events.

        """
        if event.type() == QEvent.Move:
            self.move(self.pos() + event.pos() - event.oldPos())
        return False

    def _rebuild(self):
        """ Rebuild the path used to draw the outline of the popup.

        """
        # anchor to center of parent
        anchor = self.parent()
        anchor_size = anchor.size()
        pt = QPoint(anchor_size.width() * self._relative_pos[0],
                    anchor_size.height() * self._relative_pos[1])
        anchor_pt = anchor.mapToGlobal(pt)

        h = self._arrow.height()
        rect = self.rect()
        margins = QMargins()
        anchor_type = self._anchor_type
        if anchor_type == QBubbleView.AnchorRight:
            adj = QPoint(0, rect.height() / 2)
            margins.setLeft(h)
        elif anchor_type == QBubbleView.AnchorBottom:
            adj = QPoint(rect.width() / 2, 0)
            margins.setTop(h)
        elif anchor_type == QBubbleView.AnchorLeft:
            adj = QPoint(rect.width(), rect.height() / 2)
            margins.setRight(h)
        else:
            adj = QPoint(rect.width() / 2, rect.height())
            margins.setBottom(h)
        self.move(anchor_pt - adj)
        self.setContentsMargins(margins)

        self._path = _generate_popup_path(
            rect, self._radius, self._radius, self._arrow, anchor_type
        )
        self.update()


def _generate_popup_path(rect, xRadius, yRadius, arrowSize, anchor):
    """ Generate the QPainterPath used to draw the outline of the popup.

    Parameters
    ----------
    rect : QRect
        Bounding rect for the popup.

    xRadius, yRadius : int
        x and y radius of the popup.

    arrowSize : QSize
        Width and height of the popup anchor arrow.

    anchor : int
        Positioning of the popup relative to the parent. Determines the
        position of the arrow.

    Returns
    -------
    result : QPainterPath
        Path that can be passed to QPainter.drawPath to render popup.

    """
    awidth, aheight = arrowSize.width(), arrowSize.height()
    draw_arrow = (awidth > 0 and aheight > 0)

    if anchor == QBubbleView.AnchorRight:
        rect.adjust(aheight, 0, 0, 0)
    elif anchor == QBubbleView.AnchorLeft:
        rect.adjust(0, 0, -aheight, 0)
    elif anchor == QBubbleView.AnchorBottom:
        rect.adjust(0, aheight, 0, 0)
    else:
        rect.adjust(0, 0, 0, -aheight)

    r = rect.normalized()

    if r.isNull():
        return

    hw = r.width() / 2
    hh = r.height() / 2

    xRadius = 100 * min(xRadius, hw) / hw
    yRadius = 100 * min(yRadius, hh) / hh

    # The starting point of the path is the top left corner
    x = r.x()
    y = r.y()
    w = r.width()
    h = r.height()
    rxx2 = w * xRadius / 100
    ryy2 = h * yRadius / 100

    center = r.center()

    path = QPainterPath()
    path.arcMoveTo(x, y, rxx2, ryy2, 180)
    path.arcTo(x, y, rxx2, ryy2, 180, -90)

    if anchor == QBubbleView.AnchorBottom and draw_arrow:
        path.lineTo(center.x() - awidth, y)
        path.lineTo(center.x(), y - aheight)
        path.lineTo(center.x() + awidth, y)

    path.arcTo(x + w - rxx2, y, rxx2, ryy2, 90, -90)

    if anchor == QBubbleView.AnchorLeft and draw_arrow:
        path.lineTo(x + w, center.y() - awidth)
        path.lineTo(x + w + aheight, center.y())
        path.lineTo(x + w, center.y() + awidth)

    path.arcTo(x + w - rxx2, y + h - ryy2, rxx2, ryy2, 0, -90)

    if anchor == QBubbleView.AnchorTop and draw_arrow:
        path.lineTo(center.x() + awidth, y + h)
        path.lineTo(center.x(), y + h + aheight)
        path.lineTo(center.x() - awidth, y + h)

    path.arcTo(x, y + h - ryy2, rxx2, ryy2, 270, -90)

    if anchor == QBubbleView.AnchorRight and draw_arrow:
        path.lineTo(x, center.y() + awidth)
        path.lineTo(x - aheight, center.y())
        path.lineTo(x,  center.y() - awidth)

    path.closeSubpath()
    return path
