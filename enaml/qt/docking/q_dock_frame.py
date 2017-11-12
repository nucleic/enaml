#------------------------------------------------------------------------------
# Copyright (c) 2013-2017 Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Bool, Int, Typed

from enaml.qt.QtCore import Qt, QEvent, QRect, QSize, QPoint, QMargins, Signal
from enaml.qt.QtWidgets import QApplication, QFrame


class QDockFrame(QFrame):
    """ A QFrame base class for creating dock frames.

    """
    #: No resize border.
    NoBorder = 0

    #: Resize the window vertically from the north edge.
    NorthBorder = 1

    #: Resize the window horizontally from the east edge.
    EastBorder = 2

    #: Resize the window vertically from the south edge.
    SouthBorder = 3

    #: Resize the window horizontally from the west edge.
    WestBorder = 4

    #: Resize the window diagonally from the northeast edge.
    NorthEastBorder = 5

    #: Resize the window diagonally from the northwest edge.
    NorthWestBorder = 6

    #: Resize the window diagonally from the southeast edge.
    SouthEastBorder = 7

    #: Resize the window diagonally from the southwest edge.
    SouthWestBorder = 8

    #: The cursors to use for a given resize border.
    ResizeCursors = {
        NorthBorder: Qt.SizeVerCursor,
        SouthBorder: Qt.SizeVerCursor,
        EastBorder: Qt.SizeHorCursor,
        WestBorder: Qt.SizeHorCursor,
        NorthEastBorder: Qt.SizeBDiagCursor,
        SouthWestBorder: Qt.SizeBDiagCursor,
        NorthWestBorder: Qt.SizeFDiagCursor,
        SouthEastBorder: Qt.SizeFDiagCursor,
    }

    #: The handlers to use for resizing the frame.
    ResizeHandlers = {
        NorthBorder: '_resizeNorth',
        SouthBorder: '_resizeSouth',
        EastBorder: '_resizeEast',
        WestBorder: '_resizeWest',
        NorthEastBorder: '_resizeNortheast',
        SouthWestBorder: '_resizeSouthwest',
        NorthWestBorder: '_resizeNorthwest',
        SouthEastBorder: '_resizeSoutheast',
    }

    #: The size of the extra space for hit testing a resize corner.
    ResizeCornerExtra = 8

    #: A signal emitted when the linked button is toggled. This should
    #: be emitted at the appropriate times by a subclass.
    linkButtonToggled = Signal(bool)

    class FrameState(Atom):
        """ A private class for tracking dock frame state.

        """
        #: Whether the title bar is consuming the mouse events.
        mouse_title = Bool(False)

        #: The resize border based on the mouse hover position.
        resize_border = Int(0)

        #: The last size of the frame before a resize.
        last_size = Typed(QSize)

        #: The offset point of the cursor during a resize press.
        resize_offset = Typed(QPoint)

    def __init__(self, manager, parent=None):
        """ Initialize a QDockFrame.

        Parameters
        ----------
        manager : DockManager
            The manager which owns the frame.

        parent : QWidget or None
            The parent of the QDockFrame.

        """
        super(QDockFrame, self).__init__(parent)
        self.frame_state = self.FrameState()
        self._manager = manager

    def manager(self):
        """ Get a reference to the manager which owns the frame.

        Returns
        -------
        result : DockManager
            The dock manager which owns this dock frame.

        """
        return self._manager

    def raiseFrame(self):
        """ Raise this frame to the top of the dock manager Z-order.

        """
        manager = self._manager
        if manager is not None:
            manager.raise_frame(self)

    def titleBarGeometry(self):
        """ Get the geometry rect for the title bar.

        Returns
        -------
        result : QRect
            The geometry rect for the title bar, expressed in frame
            coordinates. An invalid rect should be returned if title
            bar should not be active.

        """
        return QRect()

    def resizeMargins(self):
        """ Get the margins to use for resizing the frame.

        Returns
        -------
        result : QMargins
            The margins to use for frame resizing when the frame is
            a top-level window.

        """
        return QMargins()

    def isLinked(self):
        """ Get whether or not the frame is linked.

        This method should be reimplemented by a subclass.

        Returns
        -------
        result : bool
            True if the frame is considered linked, False otherwise.

        """
        return False

    def setLinked(self, linked):
        """ Set whether or not the frame is linked.

        This method should be reimplemented by a subclass.

        Parameters
        ----------
        linked : bool
            True if the frame is considered linked, False otherwise.

        """
        pass

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def event(self, event):
        """ Handle the generic events for the frame.

        This handler maintains proper Z-order of the frames within the
        manager's frame list and exposes some custom event handlers
        appropriate for dock frames.

        """
        if event.type() == QEvent.HoverMove:
            self.hoverMoveEvent(event)
            return event.isAccepted()
        if event.type() == QEvent.WindowActivate and self.isWindow():
            self.raiseFrame()
        return super(QDockFrame, self).event(event)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the dock frame.

        """
        event.ignore()
        state = self.frame_state
        geo = self.titleBarGeometry()
        if geo.isValid() and geo.contains(event.pos()):
            if self.titleBarMousePressEvent(event):
                if self.isWindow():
                    self.activateWindow()
                    self.raise_()
                event.accept()
                state.mouse_title = True
                return
        if self.isWindow() and event.button() == Qt.LeftButton:
            border, offset = self._resizeBorderTest(event.pos())
            if border != self.NoBorder:
                state.resize_border = border
                state.resize_offset = offset
                state.last_size = self.size()
                event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the dock frame.

        """
        event.ignore()
        state = self.frame_state
        if state.mouse_title:
            if self.titleBarMouseMoveEvent(event):
                event.accept()
                return
        if self.isWindow() and state.resize_border != self.NoBorder:
            border = state.resize_border
            handler = getattr(self, self.ResizeHandlers[border])
            handler(event.pos(), state.resize_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the dock frame.

        """
        event.ignore()
        state = self.frame_state
        self._refreshCursor(event.pos())
        if state.mouse_title:
            if self.titleBarMouseReleaseEvent(event):
                event.accept()
                state.mouse_title = False
                return
        if self.isWindow() and event.button() == Qt.LeftButton:
            state.resize_border = self.NoBorder
            state.resize_offset = None
            if state.last_size is not None:
                if state.last_size != self.size():
                    self.manager().frame_resized(self)
                del state.last_size
            event.accept()

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the frame.

        """
        event.ignore()
        if not self.isWindow() or self.isMaximized():
            return
        if QApplication.mouseButtons() != Qt.NoButton:
            return
        state = self.frame_state
        if state.mouse_title:
            return
        if state.resize_border != self.NoBorder:
            return
        self._refreshCursor(event.pos())
        event.accept()

    def titleBarMousePressEvent(self, event):
        """ Handle a mouse press event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        return False

    def titleBarMouseMoveEvent(self, event):
        """ Handle a mouse move event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        return False

    def titleBarMouseReleaseEvent(self, event):
        """ Handle a mouse release event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        return False

    #--------------------------------------------------------------------------
    # Resize Handling
    #--------------------------------------------------------------------------
    def _refreshCursor(self, pos):
        """ Refresh the resize cursor for the given position.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in local coordinates.

        """
        border, ignored = self._resizeBorderTest(pos)
        cursor = self.ResizeCursors.get(border)
        if cursor is None:
            self.unsetCursor()
        else:
            self.setCursor(cursor)

    def _resizeBorderTest(self, pos):
        """ Hit test the frame for resizing.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in local coordinates.

        Returns
        -------
        result : tuple
            A 2-tuple of (int, QPoint) representing the resize border
            and offset for the border.

        """
        rect = self.rect()
        if not rect.contains(pos):
            return (self.NoBorder, QPoint())
        x = pos.x()
        y = pos.y()
        width = rect.width()
        height = rect.height()
        margins = self.resizeMargins()
        extra = self.ResizeCornerExtra
        if x < margins.left():
            if y < margins.top() + extra:
                mode = self.NorthWestBorder
                offset = QPoint(x, y)
            elif y > height - (margins.bottom() + extra):
                mode = self.SouthWestBorder
                offset = QPoint(x, height - y)
            else:
                mode = self.WestBorder
                offset = QPoint(x, 0)
        elif y < margins.top():
            if x < margins.left() + extra:
                mode = self.NorthWestBorder
                offset = QPoint(x, y)
            elif x > width - (margins.right() + extra):
                mode = self.NorthEastBorder
                offset = QPoint(width - x, y)
            else:
                mode = self.NorthBorder
                offset = QPoint(0, y)
        elif x > width - margins.right():
            if y < margins.top() + extra:
                mode = self.NorthEastBorder
                offset = QPoint(width - x, y)
            elif y > height - (margins.bottom() + extra):
                mode = self.SouthEastBorder
                offset = QPoint(width - x, height - y)
            else:
                mode = self.EastBorder
                offset = QPoint(width - x, 0)
        elif y > height - margins.bottom():
            if x < margins.left() + extra:
                mode = self.SouthWestBorder
                offset = QPoint(x, height - y)
            elif x > width - (margins.right() + extra):
                mode = self.SouthEastBorder
                offset = QPoint(width - x, height - y)
            else:
                mode = self.SouthBorder
                offset = QPoint(0, height - y)
        else:
            mode = self.NoBorder
            offset = QPoint()
        return mode, offset

    def _resizeNorth(self, pos, offset):
        """ A resize handler for north resizing.

        """
        dh = pos.y() - offset.y()
        height = self.height()
        min_height = self.minimumSizeHint().height()
        if height - dh < min_height:
            dh = height - min_height
        rect = self.geometry()
        rect.setY(rect.y() + dh)
        self.setGeometry(rect)

    def _resizeSouth(self, pos, offset):
        """ A resize handler for south resizing.

        """
        dh = pos.y() - self.height() + offset.y()
        size = self.size()
        size.setHeight(size.height() + dh)
        self.resize(size)

    def _resizeEast(self, pos, offset):
        """ A resize handler for east resizing.

        """
        dw = pos.x() - self.width() + offset.x()
        size = self.size()
        size.setWidth(size.width() + dw)
        self.resize(size)

    def _resizeWest(self, pos, offset):
        """ A resize handler for west resizing.

        """
        dw = pos.x() - offset.x()
        width = self.width()
        min_width = self.minimumSizeHint().width()
        if width - dw < min_width:
            dw = width - min_width
        rect = self.geometry()
        rect.setX(rect.x() + dw)
        self.setGeometry(rect)

    def _resizeNortheast(self, pos, offset):
        """ A resize handler for northeast resizing.

        """
        dw = pos.x() - self.width() + offset.x()
        dh = pos.y() - offset.y()
        size = self.size()
        min_size = self.minimumSizeHint()
        if size.height() - dh < min_size.height():
            dh = size.height() - min_size.height()
        rect = self.geometry()
        rect.setWidth(rect.width() + dw)
        rect.setY(rect.y() + dh)
        self.setGeometry(rect)

    def _resizeNorthwest(self, pos, offset):
        """ A resize handler for northwest resizing.

        """
        dw = pos.x() - offset.x()
        dh = pos.y() - offset.y()
        size = self.size()
        min_size = self.minimumSizeHint()
        if size.width() - dw < min_size.width():
            dw = size.width() - min_size.width()
        if size.height() - dh < min_size.height():
            dh = size.height() - min_size.height()
        rect = self.geometry()
        rect.setX(rect.x() + dw)
        rect.setY(rect.y() + dh)
        self.setGeometry(rect)

    def _resizeSouthwest(self, pos, offset):
        """ A resize handler for southwest resizing.

        """
        dw = pos.x() - offset.x()
        dh = pos.y() - self.height() + offset.y()
        size = self.size()
        min_size = self.minimumSizeHint()
        if size.width() - dw < min_size.width():
            dw = size.width() - min_size.width()
        rect = self.geometry()
        rect.setX(rect.x() + dw)
        rect.setHeight(rect.height() + dh)
        self.setGeometry(rect)

    def _resizeSoutheast(self, pos, offset):
        """ A resize handler for southeast resizing.

        """
        dw = pos.x() - self.width() + offset.x()
        dh = pos.y() - self.height() + offset.y()
        size = self.size()
        size.setWidth(size.width() + dw)
        size.setHeight(size.height() + dh)
        self.resize(size)
