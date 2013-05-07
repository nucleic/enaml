#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QRect
from PyQt4.QtGui import QLayout

from atom.api import Bool, Typed

from .q_dock_area import QDockArea
from .q_dock_frame import QDockFrame
from .q_dock_frame_layout import QDockFrameLayout
from .q_dock_window_buttons import QDockWindowButtons


class QDockWindow(QDockFrame):
    """ A QDockFrame which holds a toplevel dock area.

    """
    #: The static resize margins for the dock window.
    ResizeMargins = QMargins(5, 5, 5, 5)

    #: The static normal contents margins for the dock window.
    NormalMargins = QMargins(5, 20, 5, 5)

    #: The static maximized margins for the dock window.
    MaximizedMargins = QMargins(0, 20, 0, 0)

    #: The minimum offset for the window buttons from the right edge.
    MinButtonOffset = 5

    class FrameState(QDockFrame.FrameState):
        """ A private class for managing window drag state.

        """
        #: The press position in the window title bar.
        press_pos = Typed(QPoint)

        #: Whether or not the window is being dragged by the user.
        dragging = Bool(False)

    def __init__(self, manager, parent=None):
        """ Initialize a QDockWindow.

        Parameters
        ----------
        manager : DockManager
            The dock manager which owns the dock window.

        parent : QWidget or None
            The parent of the dock window, or None.

        """
        super(QDockWindow, self).__init__(manager, parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        layout = QDockFrameLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.setContentsMargins(self.NormalMargins)
        self.setDockArea(QDockArea())
        btns = self._buttons = QDockWindowButtons(self)
        btns.maximizeButtonClicked.connect(self.showMaximized)
        btns.restoreButtonClicked.connect(self.showNormal)
        btns.closeButtonClicked.connect(self.close)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def showMaximized(self):
        """ Handle a show maximized request for the window.

        """
        self.setContentsMargins(self.MaximizedMargins)
        super(QDockWindow, self).showMaximized()
        self.clearMask()
        self._buttons.setMaximized(True)

    def showNormal(self):
        """ Handle a show normal request for the window.

        """
        super(QDockWindow, self).showNormal()
        self.setContentsMargins(self.NormalMargins)
        self._buttons.setMaximized(False)

    def closeEvent(self, event):
        """ Handle a close event for the window.

        """
        event.ignore()
        area = self.dockArea()
        if area is not None:
            # avoid a circular import
            from .layout_handling import iter_containers
            for container in list(iter_containers(area)):
                container.dockItem().close()

    def destroy(self):
        """ Destroy the dock container and release its references.

        """
        self.setDockArea(None)
        super(QDockWindow, self).destroy()

    def titleBarGeometry(self):
        """ Get the geometry rect for the title bar.

        Returns
        -------
        result : QRect
            The geometry rect for the title bar, expressed in frame
            coordinates. An invalid rect is returned if title bar
            should not be active.

        """
        cmargins = self.contentsMargins()
        if self.isMaximized():
            return QRect(0, 0, self.width(), cmargins.top())
        rmargins = self.ResizeMargins
        width = self.width() - (cmargins.left() + cmargins.right())
        height = cmargins.top() - rmargins.top()
        return QRect(cmargins.left(), rmargins.top(), width, height)

    def resizeMargins(self):
        """ Get the margins to use for resizing the container.

        Returns
        -------
        result : QMargins
            The margins to use for container resizing when the container
            is a top-level window.

        """
        return self.ResizeMargins

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def dockArea(self):
        """ Get the dock area installed on the container.

        Returns
        -------
        result : QDockArea or None
            The dock area installed in the container, or None.

        """
        return self.layout().getWidget()

    def setDockArea(self, dock_area):
        """ Set the dock area for the container.

        Parameters
        ----------
        dock_area : QDockArea
            The dock area to use in the container.

        """
        self.layout().setWidget(dock_area)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def resizeEvent(self, event):
        """ Handle the resize event for the dock window.

        """
        super(QDockWindow, self).resizeEvent(event)
        buttons = self._buttons
        size = buttons.minimumSizeHint()
        offset = max(self.MinButtonOffset, self.contentsMargins().right())
        x = self.width() - size.width() - offset
        rect = QRect(x, 0, size.width(), size.height())
        buttons.setGeometry(rect)

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the dock window.

        This reimplementation unsets the cursor when the mouse hovers
        over the dock window buttons.

        """
        if self._buttons.geometry().contains(event.pos()):
            self.unsetCursor()
        else:
            super(QDockWindow, self).hoverMoveEvent(event)

    def titleBarMousePressEvent(self, event):
        """ Handle the mouse press event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is None:
                state.press_pos = event.pos()
                return True
        return False

    def titleBarMouseMoveEvent(self, event):
        """ Handle the mouse move event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.frame_state
        if state.press_pos is not None:
            global_pos = event.globalPos()
            if self.isMaximized():
                coeff = state.press_pos.x() / float(self.width())
                self.showNormal()
                btn_width = self._buttons.width()
                margins = self.contentsMargins()
                max_x = self.width() - margins.right() - btn_width - 5
                test_x = int(coeff * self.width())
                new_x = max(5, min(test_x, max_x))
                state.press_pos.setX(new_x)
                state.press_pos.setY(margins.top() / 2)
            self.move(global_pos - state.press_pos)
            self.manager().frame_moved(self, global_pos)
            return True
        return False

    def titleBarMouseReleaseEvent(self, event):
        """ Handle the mouse release event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is not None:
                self.manager().frame_released(self, event.globalPos())
                state.dragging = False
                state.press_pos = None
                return True
        return False
