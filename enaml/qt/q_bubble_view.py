#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QPointF, QMargins, pyqtSignal
from PyQt4.QtGui import QFrame, QLayout, QPainter, QPainterPath, QRegion, QPen

from .q_single_widget_layout import QSingleWidgetLayout


class QBubbleView(QFrame):
    """ A Bubble popup widget.

    This widget implements a popup style with rounded corners and an
    arrow anchoring it to an underlying widget. Useful for transient
    dialogs.

    """
    #: A signal emitted when the popup is closed.
    closed = pyqtSignal()

    #: The top anchor location.
    AnchorTop = 0

    #: The bottom anchor location.
    AnchorBottom = 1

    #: The left anchor location.
    AnchorLeft = 2

    #: The right anchor location.
    AnchorRight = 3

    def __init__(self, parent):
        """ Initialize a QBubbleView.

        Parameters
        ----------
        parent : QWidget
            The parent widget of the popup view, or None.

        """
        super(QBubbleView, self).__init__(parent)
        flags = Qt.Popup | Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QSingleWidgetLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self._anchor = QBubbleView.AnchorBottom
        self._arrow_size = QSize(20, 20)
        self._relative_pos = QPointF(0.5, 0.5)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def centralWidget(self):
        """ Returns the central widget for the popup.

        Returns
        -------
        result : QWidget or None
            The central widget of the popup, or None if no widget
            was provided.

        """
        return self.layout().getWidget()

    def setCentralWidget(self, widget):
        """ Set the central widget for this popup.

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
        result : int
            An enum specifying the anchor position relative to the
            parent widget. This will be one of AnchorLeft, AnchorRight,
            AnchorTop, or AnchorBottom.

        """
        return self._anchor

    def setAnchor(self, anchor):
        """ Set the anchor position for the popup view.

        Parameters
        ----------
        anchor : int
            An enum specifying the anchor position relative to the
            parent widget. This should be one of AnchorLeft,
            AnchorRight, AnchorTop, or AnchorBottom.

        """
        self._anchor = anchor
        self._rebuild()
        self.update()

    def arrowSize(self):
        """ Return the size of the arrow.

        Returns
        -------
        result : int
            The size of the arrow in pixels.

        """
        return self._arrow_size.height()

    def setArrowSize(self, arrow):
        """ Set size of the arrow.

        Parameters
        ----------
        arrow : int
            The size of the arrow (in pixels). A size of zero indicates
            that no arrow is desired

        """
        self._arrow_size = QSize(arrow, arrow)
        self._rebuild()
        self.update()

    def relativePos(self):
        """ Return the relative position of the popup.

        Returns
        -------
        result : QPointF
            The relative anchoring of the popup relative to the parent
            widget's bounds.

        """
        return self._relative_pos

    def setRelativePos(self, pos):
        """ Set the relative position of the popup.

        This method sets the position of the anchor point relative the
        bounds of the parent widget.

        Parameters
        ----------
        pos : QPointF
            A point in the range 0.0 to 1.0 specifying the relative
            position of the anchor on the parent widget.

        """
        self._relative_pos = pos
        self._rebuild()
        self.update()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def closeEvent(self, event):
        """ Handle the close event for the popup view.

        By default, this handler calls the superclass' method to close
        the window and then emits the 'closed' signal.

        """
        super(QBubbleView, self).closeEvent(event)
        self.closed.emit()

    def resizeEvent(self, event):
        """ Handle the resize event for the popup view.

        This handler rebuilds the popup path when the size changes.

        """
        super(QBubbleView, self).resizeEvent(event)
        self._rebuild()

    def paintEvent(self, event):
        """ Reimplement the paint event

        """
        super(QBubbleView, self).paintEvent(event)
        path = self._path
        if path is not None:
            painter = QPainter(self)
            palette = self.palette()
            fill = palette.window()
            stroke = palette.windowText()
            painter.setBrush(fill.color())
            painter.setPen(QPen(stroke.color(), 2))
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPath(self._path)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @staticmethod
    def _generatePath(size, arrowSize, anchor):
        """ Generate the QPainterPath to draw the outline of the popup.

        Parameters
        ----------
        size : QSize
            Bounding size for the popup.

        arrowSize : QSize
            Width and height of the popup anchor arrow.

        anchor : int
            The enum position of the popup relative to the parent.

        Returns
        -------
        result : QPainterPath or None
            A painter path that can be used to render popup or None
            if a path could not be generated.

        """
        awidth, aheight = arrowSize.width(), arrowSize.height()
        draw_arrow = (awidth > 0 and aheight > 0)
        path = QPainterPath()
        w = size.width()
        h = size.height()
        path = QPainterPath()
        if not draw_arrow:
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.lineTo(0, 0)
        elif anchor == QBubbleView.AnchorTop:
            ledge = h - aheight
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, ledge)
            path.lineTo(w / 2 + awidth / 2, ledge)
            path.lineTo(w / 2, h)
            path.lineTo(w / 2 - awidth / 2, ledge)
            path.lineTo(0, ledge)
            path.lineTo(0, 0)
        elif anchor == QBubbleView.AnchorBottom:
            path.moveTo(0, aheight)
            path.lineTo(w / 2 - awidth / 2, aheight)
            path.lineTo(w / 2, 0)
            path.lineTo(w / 2 + awidth / 2, aheight)
            path.lineTo(w, aheight)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.lineTo(0, aheight)
        elif anchor == QBubbleView.AnchorRight:
            awidth, aheight = aheight, awidth
            path.moveTo(awidth, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(awidth, h)
            path.lineTo(awidth, h / 2 + aheight / 2)
            path.lineTo(0, h / 2)
            path.lineTo(awidth, h / 2 - aheight / 2)
            path.lineTo(awidth, 0)
        else:
            awidth, aheight = aheight, awidth
            ledge = w - awidth
            path.moveTo(0, 0)
            path.lineTo(ledge, 0)
            path.lineTo(ledge, h / 2 - aheight / 2)
            path.lineTo(w, h / 2)
            path.lineTo(ledge, h / 2 + aheight / 2)
            path.lineTo(ledge, h)
            path.lineTo(0, h)
            path.lineTo(0, 0)
        return path

    def _rebuild(self):
        """ Rebuild the path used to draw the outline of the popup.

        """
        pos = self._relative_pos
        parent = self.parent()
        pt = QPoint(parent.width() * pos.x(), parent.height() * pos.y())
        anchor_pt = parent.mapToGlobal(pt)
        size = self.size()
        margins = QMargins()
        anchor = self._anchor
        arrow_size = self._arrow_size
        if anchor == QBubbleView.AnchorRight:
            adj = QPoint(0, size.height() / 2)
            margins.setLeft(arrow_size.height())
        elif anchor == QBubbleView.AnchorBottom:
            adj = QPoint(size.width() / 2, 0)
            margins.setTop(arrow_size.height())
        elif anchor == QBubbleView.AnchorLeft:
            adj = QPoint(size.width(), size.height() / 2)
            margins.setRight(arrow_size.height())
        else:
            adj = QPoint(size.width() / 2, size.height())
            margins.setBottom(arrow_size.height())
        self.move(anchor_pt - adj)
        self.setContentsMargins(margins)
        path = self._generatePath(self.size(), arrow_size, anchor)
        if path is not None:
            mask = QRegion(path.toFillPolygon().toPolygon())
            self.setMask(mask)
        self._path = path
