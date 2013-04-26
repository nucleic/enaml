#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QEvent
from PyQt4.QtGui import QFrame, QLayout, QRegion, QIcon

from atom.api import Atom, Typed, Int, Bool

from .dock_window_resizer import DockWindowResizer
from .q_dock_window_layout import QDockWindowLayout


class QDockContainerLayout(QDockWindowLayout):
    """ A QDockWindowLayout subclass which works with a QDockContainer.

    """
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockContainerLayout, self).invalidate()
        dock_widget = self.dockWidget()
        if dock_widget is not None:
            self.parentWidget().setSizePolicy(dock_widget.sizePolicy())


class QDockContainer(QFrame):
    """ A custom QFrame which holds a QDockItem instance.

    The dock container provides a level of indirection when tearing
    dock items out of a dock area. The window flags for the container
    are controlled by the dock manager driving the dock area.

    """
    #: The size of the extra space for hit testing a resize corner.
    ResizeCornerExtra = 8

    class ContainerState(Atom):
        """ A private class for managing container drag state.

        """
        #: Whether the container is floating as a toplevel window.
        is_floating = Bool(False)

        #: The resize mode based on the mouse hover position.
        resize_mode = Int(DockWindowResizer.NoResize)

        #: The offset point of the cursor during a resize press.
        resize_offset = Typed(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockContainer.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the QDockContainer.

        """
        super(QDockContainer, self).__init__(parent)
        layout = QDockContainerLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.state = self.ContainerState()
        self.handler = None  # set by the dock manager

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockItem(self):
        """ Get the dock item installed on the container.

        Returns
        -------
        result : QDockItem or None
            The dock item installed in the container, or None.

        """
        return self.layout().dockWidget()

    def setDockItem(self, dock_item):
        """ Set the dock item for the container.

        Parameters
        ----------
        dock_item : QDockItem
            The dock item to use in the container.

        """
        self.layout().setDockWidget(dock_item)

    def isFloating(self):
        """ Get whether the container is floating.

        Returns
        -------
        result : bool
            True if the container is floating, False otherwise.

        """
        return self.state.is_floating

    def setFloating(self, floating):
        """ Set whether the container is floating.

        This flag only affects how the container draws itself. It does
        not change the window flags; that responsibility lies with the
        dock manager which controls the container.

        Parameters
        ----------
        floating : bool
            True if the container is floating, False otherwise.

        """
        state = self.state
        state.is_floating = floating
        self.setAttribute(Qt.WA_Hover, floating)
        if floating:
            self.setContentsMargins(QMargins(5, 5, 5, 5))
        else:
            self.setContentsMargins(QMargins(0, 0, 0, 0))
            self.unsetCursor()
            self.clearMask()

    #--------------------------------------------------------------------------
    # Proxy Methods
    #--------------------------------------------------------------------------
    def title(self):
        """ Get the title for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.title()
        return u''

    def icon(self):
        """ Get the icon for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.icon()
        return QIcon()

    def showTitleBar(self):
        """ Show the title bar for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            item.titleBarWidget().show()

    def hideTitleBar(self):
        """ Hide the title bar for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            item.titleBarWidget().hide()

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
            if self.state.is_floating and self.handler is not None:
                self.handler.window_activated()
        return super(QDockContainer, self).event(event)

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the container.

        This handler is invoked when the container is in floating mode.
        It updates the cursor if the mouse is hovered over one of the
        containers resize areas.

        """
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            # don't change the cursor until the resize is finished.
            if state.resize_mode != dwr.NoResize:
                return
            margins = self.contentsMargins()
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
        state = self.state
        if state.is_floating and event.button() == Qt.LeftButton:
            dwr = DockWindowResizer
            margins = self.contentsMargins()
            extra = self.ResizeCornerExtra
            mode, offset = dwr.hit_test(self, event.pos(), margins, extra)
            if mode != dwr.NoResize:
                state.resize_mode = mode
                state.resize_offset = offset
                event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the container.

        This handler finalizes the mouse event when the container is
        in floating mode.

        """
        event.ignore()
        state = self.state
        if state.is_floating and event.button() == Qt.LeftButton:
            state.resize_mode = DockWindowResizer.NoResize
            state.resize_offset = None
            event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the container.

        This handler resizes and moves the container when it is in
        floating mode.

        """
        event.ignore()
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            if state.resize_mode != dwr.NoResize:
                mode = state.resize_mode
                offset = state.resize_offset
                dwr.resize(self, event.pos(), mode, offset)
                event.accept()

    def resizeEvent(self, event):
        """ Handle the resize event for the container.

        This handler updates the mask on the container if it is set
        to floating mode.

        """
        state = self.state
        if state.is_floating:
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
