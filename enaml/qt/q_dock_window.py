#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QMargins, QPoint, QEvent
from PyQt4.QtGui import QFrame, QLayout, QRegion, QWidgetItem, QPainter, QColor

from .q_dock_area import QDockArea


class QDockWindowLayout(QLayout):
    """ A QLayout subclass for laying out a dock window

    """
    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QDockWindowLayout, self).__init__(parent)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self._dock_area = None
        self._dock_area_item = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockArea(self):
        """ Get the dock area set for the layout.

        Returns
        -------
        result : QDockArea
            The primary dock area set in the window layout.

        """
        return self._dock_area

    def setDockArea(self, area):
        """ Set the dock area for the layout.

        The old area will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        area : QDockArea
            The area to use as the primary content in the layout.

        """
        old_area = self._dock_area
        if old_area is not None:
            old_area.hide()
            old_area.setParent(None)
        self._dock_area = area
        self._dock_area_item = None
        if area is not None:
            self._dock_area_item = QWidgetItem(area)
            area.setParent(self.parentWidget())
            area.show()
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockWindowLayout, self).setGeometry(rect)
        area = self._dock_area
        if area is not None:
            area.setGeometry(self.contentsRect())

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        area = self._dock_area
        if area is not None:
            hint = area.sizeHint()
        else:
            hint = QSize(256, 192)
        m = self.contentsMargins()
        hint.setWidth(hint.width() + m.left() + m.right())
        hint.setHeight(hint.height() + m.top() + m.bottom())
        return hint

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        area = self._dock_area
        if area is not None:
            size = area.minimumSizeHint()
        else:
            size = QSize(256, 192)
        m = self.contentsMargins()
        size.setWidth(size.width() + m.left() + m.right())
        size.setHeight(size.height() + m.top() + m.bottom())
        return size

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        area = self._dock_area
        if area is not None:
            return area.maximumSize()
        return QSize(16777215, 16777215)

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        msg = 'Use `setTitleBar | setDockWidget` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        return 1 if self._dock_area else 0

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        if idx == 0:
            return self._dock_area_item

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None


class QDockWindow(QFrame):
    """ A custom QFrame which provides a floating dock area.

    This class is used by the docking framework to manage floating dock
    windows. It should not normally be used directly by user code.

    """
    def __init__(self, parent):
        assert isinstance(parent, QDockArea)
        super(QDockWindow, self).__init__(parent)
        flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        layout = QDockWindowLayout()
        layout.setDockArea(QDockArea())
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

        self.setAttribute(Qt.WA_Hover)
        self._in_resize_box = False
        self._resizing = False
        self._press_pos = None
        self._dock_manager = None  # set by framework

    def dockArea(self):
        return self.layout().dockArea()

    def updateMargins(self):
        if self.dockArea().itemCount() > 1:
            m = QMargins(0, 10, 0, 0)
        else:
            m = QMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(m)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(QDockWindow, self).keyPressEvent(event)

    def event(self, event):
        if event.type() == QEvent.HoverMove:
            self.hoverMoveEvent(event)
            return True
        if event.type() == QEvent.WindowActivate:
            self._dock_manager.window_activated(self)
        return super(QDockWindow, self).event(event)

    def hoverMoveEvent(self, event):
        pos = event.pos()
        w = self.width()
        h = self.height()
        if pos.x() >= w - 10 and pos.y() >= h - 10:
            self._in_resize_box = True
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self._in_resize_box = False
            self.unsetCursor()

    def mousePressEvent(self, event):
        event.ignore()
        if event.button() == Qt.LeftButton:
            if self._in_resize_box:
                self._resizing = True
                event.accept()
                return
            elif event.pos().y() < self.layout().contentsMargins().top():
                self._press_pos = event.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        event.ignore()
        if self._resizing:
            d = event.pos()
            self.resize(QSize(d.x() + 2, d.y() + 2))
            event.accept()
            return
        if self._press_pos is not None:
            self.move(event.globalPos() - self._press_pos)

    def mouseReleaseEvent(self, event):
        event.ignore()
        if event.button() == Qt.LeftButton:
            if self._resizing or self._press_pos is not None:
                self._resizing = False
                self._press_pos = None
                event.accept()

    def paintEvent(self, event):
        super(QDockWindow, self).paintEvent(event)
        t = self.layout().contentsMargins().top()
        if t > 0:
            x1 = 7
            x2 = self.width() - 7
            color = self.palette().window().color()
            painter = QPainter(self)
            painter.setPen(QColor.darker(color))
            painter.drawLine(QPoint(x1, t - 2), QPoint(x2, t - 2))
            painter.setPen(QColor.lighter(color))
            painter.drawLine(QPoint(x1, t - 1), QPoint(x2, t - 1))

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        region = QRegion(0, 0, w, h)

        # top left
        region -= QRegion(0, 0, 3, 1)
        region -= QRegion(0, 0, 1, 3)

        # top right
        region -= QRegion(w - 3, 0, 3, 1)
        region -= QRegion(w - 1, 0, 1, 3)

        # bottom left
        region -= QRegion(0, h - 3, 1, 3)
        region -= QRegion(0, h - 1, 3, 1)

        # bottom right
        region -= QRegion(w - 1, h - 3, 1, 3)
        region -= QRegion(w - 3, h - 1, 3, 1)

        self.setMask(region)
