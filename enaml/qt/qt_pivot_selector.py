#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QSize, QPoint, QEvent, pyqtSignal
from PyQt4.QtGui import (
    QWidget, QSizePolicy, QCursor, QPainter, QPen, QStyle, QColor, QBrush,
)

from atom.api import Int, Typed

from enaml.widgets.pivot_selector import ProxyPivotSelector

from .qt_control import QtControl


class QPivotSelector(QWidget):
    """ A Qt implementation of a pivot selector.

    This widget enables the user to select the pivot level from a list
    of pivots.

    """

    #: A signal emitted when the selector changes.
    currentIndexChanged = pyqtSignal(int)

    #: A signal emitted when the user rearranges the order of items
    #: TODO - fix this so dragging works correctly
    itemOrderingChanged = pyqtSignal(list)

    #: A signal emitted when one of the pivots is clicked
    indexClicked = pyqtSignal(int)

    #: Private list of items
    _items = []

    #: Which item is currently selected
    _selected = -1

    #: Which item is the offset
    _offset = 0

    #: Is an item being dragged
    _dragging_item = False

    #: Which item is being dragged
    _dragging_name = -1

    #: internal styling
    _item_height = 4

    def __init__(self, parent=None):
        """ Initialize a QPivotSelector.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of this selector widget, or None if the widget has
            no parent

        """
        super(QPivotSelector, self).__init__(parent)
        self.setAttribute(Qt.WA_Hover)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        style = self.style()
        frame_width = style.pixelMetric(QStyle.PM_DefaultFrameWidth)
        self._border = 2 * (frame_width + 2) + 3
        self._margin = style.pixelMetric(QStyle.PM_ButtonMargin)

        #self._hand_cursor = QCursor(Qt.OpenHandCursor)
        self._drag_cursor = QCursor(Qt.SizeHorCursor)
        self._hover_item = False
        self._widths = []

    def items(self):
        """ Get the current items.

        The items are returned in the current visual order.

        Returns
        -------
        result : list
            The current selector strings.

        """
        return self._items

    def setItems(self, items):
        """ Set the list of current items.

        Parameters
        ----------
        items : list
            The pivot items to show. List items must be strings.

        """
        self._items = items
        if items:
            self._selected = len(items) - 1 - self._offset
            self.currentIndexChanged.emit(self._selected)

        # Compute and cache the font widths
        fm = self.fontMetrics()
        widths = []
        for sel in self._items:
            widths.append(fm.width(sel) + self._border + self._margin)
        self._widths = widths

        self.update()

    def count(self):
        """ Return the number of items in the selector

        Returns
        -------
        result : int
            The number of items in this selector

        """
        return len(self._items)

    def setCurrentIndex(self, idx):
        """ Set the current selector index

        Parameters
        ----------
        idx : int
            The index to set

        """
        self._selected = idx

    def currentIndex(self):
        """ Return the current index

        Returns
        ----------
        result: int
            The current selected index

        """
        return self._selected

    def setOffset(self, offset):
        """ Set the active offset

        Parameters
        ----------
        offset : int
            The offset to set

        """
        self._offset = offset

    def offset(self):
        """ Return the current offset

        Returns
        ----------
        result: int
            The current offset

        """
        return self._offset

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A reimplemented virtual method.

        """
        painter = QPainter(self)

        # Paint all the items side by side
        fm = self.fontMetrics()

        border, margin = self._border, self._margin

        rect = QRect()
        rect.setHeight(fm.height() + border)
        rect.setTopLeft(QPoint(margin / 2, self._item_height))

        col = QColor("#ADD8E6")
        hover_pen_outline = QPen(Qt.black, 2, join=Qt.MiterJoin)
        hover_pen_fill = QPen(col, 2)
        pen = QPen(Qt.gray, 2, join=Qt.MiterJoin)

        col.setAlphaF(0.4)
        highlight_brush = QBrush(col)

        col = QColor("#FCE883")
        col = QColor("#CCCCCC")
        col.setAlphaF(0.4)
        fixed_brush = QBrush(col)

        for i, sel in enumerate(self._items):
            rect.setWidth(self._widths[i] - margin)
            if i < self._offset:
                painter.setBrush(fixed_brush)
            #elif i <= (self._selected + self._offset):
            #    painter.setBrush(highlight_brush)
            else:
                painter.setBrush(QBrush())
            painter.setPen(Qt.lightGray)
            painter.drawRoundedRect(rect, 5, 5)
            if i <= (self._selected + self._offset):
                painter.setPen(Qt.black)
            else:
                painter.setPen(Qt.lightGray)
            painter.drawText(rect, Qt.AlignCenter, str(sel))

            # Now draw the selector
            if i == (self._selected + self._offset):
                if self._hover_item:
                    painter.setPen(hover_pen_outline)
                else:
                    painter.setPen(pen)
                sh = self._item_height
                tr = rect.topRight() + QPoint((margin / 2) + 1, -sh / 2)
                br = rect.bottomRight() + QPoint((margin / 2) + 1, (sh / 2) + 2)
                offset = QPoint(8, 0)
                painter.drawPolyline(*[tr - offset, tr, br, br - offset])
                if self._hover_item:
                    offset = QPoint(4, 0)
                    painter.drawLine(tr - offset, br - offset)
                    painter.setPen(hover_pen_fill)
                    painter.drawLine(tr - QPoint(2, -2), br - QPoint(2, 2))

            rect.moveLeft(rect.left() + self._widths[i])

    def sizeHint(self):
        """ A reimplemented virtual method.

        Returns
        -------
        result : QSize
            The default size for this widget

        """
        fm = self.fontMetrics()
        border, margin = self._border, self._margin
        height = fm.height() + border + self._item_height
        return QSize(sum(self._widths) + border, height)

    def event(self, event):
        """ A reimplemented virtual method

        Handles cursor changes on hover events

        """
        if (event.type() == QEvent.HoverMove and not self._dragging_item and
            self._dragging_name == -1):
            if (self.selectorRect().contains(event.pos()) and not
                    self.cursor() == self._drag_cursor):
                self.setCursor(self._drag_cursor)
                self._hover_item = True
            else:
                #self.setCursor(self._hand_cursor)
                self.setCursor(Qt.ArrowCursor)
                self._hover_item = False
            self.update()
        elif (event.type() == QEvent.HoverLeave):
            self._hover_item = False
        return super(QPivotSelector, self).event(event)

    def mousePressEvent(self, event):
        """ A reimplemented virtual method.

        """
        if self.selectorRect().contains(event.pos()):
            self._dragging_item = True
        else:  # TODO fix pivot label dragging
            # Check which box we clicked on
            x, r, l = event.pos().x(), 0, 0
            for i, width in enumerate(self._widths):
                r += width
                if l <= x <= r:
                    self.indexClicked.emit(i)
                    #self._dragging_name = i
                    break
                l += width
        return super(QPivotSelector, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ A reimplemented virtual method.

        """
        if self._dragging_item:
            x, edge = event.pos().x(), 0
            for i, width in enumerate(self._widths):
                edge += width
                if self._offset < (i+1) and abs(x - edge) < width/2:
                    self._selected = i - self._offset
                    self.currentIndexChanged.emit(self._selected)
                    self.update()
                    break
        elif self._dragging_name != -1:
            # Animate dragging
            sel, items = self._dragging_name, self._items[:]
            x, l = event.pos().x(), 0,
            for i, width in enumerate(self._widths):
                if abs(x - l) < 4:
                    items[i], items[sel] = items[sel], items[i]
                    self.setItems(items)
                    break
                l += width
        return super(QPivotSelector, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """ A reimplemented virtual method.

        """
        if self._dragging_item:
            self._dragging_item = False
        elif self._dragging_name != -1:
            self._dragging_name = -1
            self.itemOrderingChanged.emit(self._items)
        return super(QPivotSelector, self).mouseReleaseEvent(event)

    def selectorRect(self):
        """ Calculate the rect of the selector.
        """
        fm = self.fontMetrics()
        border, margin = self._border, self._margin
        height = fm.height() + border + self._item_height
        return QRect(sum(self._widths[:self._selected + self._offset + 1]) - 4, 0, 8, height)


# cyclic notification guard flags
INDEX_GUARD = 0x1


class QtPivotSelector(QtControl, ProxyPivotSelector):
    """ A Qt implementation of an Enaml QtPivotSelector

    """
    #: A reference to the widget created by the proxy
    widget = Typed(QPivotSelector)

    #: Cyclic notification guard. This is a bitfield of multiple guards
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QPivotSelector widget.

        """
        self.widget = QPivotSelector(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtPivotSelector, self).init_widget()
        d = self.declaration
        self.set_items(d.items)
        self.set_index(d.index)
        self.set_offset(d.offset)
        self.widget.currentIndexChanged.connect(self.on_index_changed)
        self.widget.indexClicked.connect(self.on_clicked)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self):
        """ The signal handler for the index changed signal.

        """
        if not self._guard & INDEX_GUARD:
            self.declaration.index = self.widget.currentIndex()

    def on_clicked(self, idx):
        """ The signal handler for the index clicked signal.

        """
        self.declaration.clicked(idx)

    #--------------------------------------------------------------------------
    # ProxyComboBox API
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the PivotSelector.

        """
        self.widget.setItems(items)
        self.request_relayout()

    def set_index(self, index):
        """ Set the current index of the PivotSelector.

        """
        self._guard |= INDEX_GUARD
        try:
            self.widget.setCurrentIndex(index)
        finally:
            self._guard &= ~INDEX_GUARD

    def set_offset(self, offset):
        """ Set the current offset of the PivotSelector.

        """
        self.widget.setOffset(offset)
