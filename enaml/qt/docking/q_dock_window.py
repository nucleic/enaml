#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QEvent
from PyQt4.QtGui import QFrame, QLayout, QRegion, QPushButton

from atom.api import Atom, Typed, Int

from .dock_window_resizer import DockWindowResizer
from .q_dock_window_layout import QDockWindowLayout


class QDockWindow(QFrame):
    """ A custom QFrame which holds a QDockItem instance.

    The dock container provides a level of indirection when tearing
    dock items out of a dock area. The window flags for the container
    are controlled by the dock manager driving the dock area.

    """
    #: The size of the extra space for hit testing a resize corner.
    ResizeCornerExtra = 8

    class WindowState(Atom):
        """ A private class for managing container drag state.

        """
        press_pos = Typed(QPoint)

        #: The resize mode based on the mouse hover position.
        resize_mode = Int(DockWindowResizer.NoResize)

        #: The offset point of the cursor during a resize press.
        resize_offset = Typed(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockWindow.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the QDockWindow.

        """
        super(QDockWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_Hover, True)
        layout = QDockWindowLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.setContentsMargins(QMargins(5, 15, 5, 5))
        self.state = self.WindowState()
        self.handler = None  # set by the dock manager
        self._resize_margins = QMargins(5, 5, 5, 5)
        self.setDockArea(QPushButton())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockArea(self):
        """ Get the dock area installed on the container.

        Returns
        -------
        result : QDockArea or None
            The dock area installed in the container, or None.

        """
        return self.layout().dockWidget()

    def setDockArea(self, dock_area):
        """ Set the dock area for the container.

        Parameters
        ----------
        dock_area : QDockArea
            The dock area to use in the container.

        """
        self.layout().setDockWidget(dock_area)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock container.

        This handler dispatches hover events which are sent when the
        container is floating. It also notifies the dock manager when
        it is activated so that the manager can maintain a proper
        top-level Z-order.

        """
        # hover events are only generated if the WA_Hover attribute is
        # set, and that is only set when the container is floating.
        if event.type() == QEvent.HoverMove:
            self.hoverMoveEvent(event)
            return True
        if event.type() == QEvent.WindowActivate:
            if self.handler is not None:
                self.handler.window_activated()
        return super(QDockWindow, self).event(event)

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the container.

        This handler is invoked when the container is in floating mode.
        It updates the cursor if the mouse is hovered over one of the
        containers resize areas.

        """
        state = self.state
        dwr = DockWindowResizer
        # don't change the cursor until the resize is finished.
        if state.resize_mode != dwr.NoResize:
            return
        margins = self._resize_margins
        extra = self.ResizeCornerExtra
        mode, ignored = dwr.hit_test(self, event.pos(), margins, extra)
        cursor = dwr.cursor(mode)
        if cursor is None:
            self.unsetCursor()
        else:
            self.setCursor(cursor)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the container.

        This handler sets up the resize and drag operations when the
        container is in floating mode.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            state = self.state
            pos = event.pos()
            dwr = DockWindowResizer
            margins = self._resize_margins
            extra = self.ResizeCornerExtra
            mode, offset = dwr.hit_test(self, pos, margins, extra)
            if mode != dwr.NoResize:
                state.resize_mode = mode
                state.resize_offset = offset
                event.accept()
            elif pos.y() <= self.contentsMargins().top():
                state.press_pos = pos
                event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the container.

        This handler finalizes the mouse event when the container is
        in floating mode.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            state = self.state
            state.resize_mode = DockWindowResizer.NoResize
            state.resize_offset = None
            state.press_pos = None
            event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the container.

        This handler resizes and moves the container when it is in
        floating mode.

        """
        event.ignore()
        state = self.state
        dwr = DockWindowResizer
        if state.resize_mode != dwr.NoResize:
            mode = state.resize_mode
            offset = state.resize_offset
            dwr.resize(self, event.pos(), mode, offset)
            event.accept()
        elif state.press_pos is not None:
            self.move(event.globalPos() - state.press_pos)
            event.accept()


    def resizeEvent(self, event):
        """ Handle the resize event for the container.

        This handler updates the mask on the container if it is set
        to floating mode.

        """
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
