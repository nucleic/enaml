#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QEvent
from PyQt4.QtGui import QApplication, QLayout, QRegion, QIcon

from atom.api import Atom, Typed, Int, Bool

from .dock_window_resizer import DockWindowResizer
from .q_dock_frame import QDockFrame
from .q_dock_frame_layout import QDockFrameLayout


class QDockContainerLayout(QDockFrameLayout):
    """ A QDockFrameLayout subclass which works with a QDockContainer.

    """
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockContainerLayout, self).invalidate()
        dock_widget = self.dockWidget()
        if dock_widget is not None:
            self.parentWidget().setSizePolicy(dock_widget.sizePolicy())


class QDockContainer(QDockFrame):
    """ A QDockFrame which holds a QDockItem instance.

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

        #: The original title bar press position.
        press_pos = Typed(QPoint)

        #: Whether or not the dock item is being dragged.
        dragging = Bool(False)

    def __init__(self, manager, parent=None):
        """ Initialize a QDockContainer.

        Parameters
        ----------
        manager : DockManager
            The manager which owns the container.

        parent : QWidget or None
            The parent of the QDockContainer.

        """
        super(QDockContainer, self).__init__(manager, parent)
        layout = QDockContainerLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.state = self.ContainerState()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroy the dock container and release its references.

        """
        self.setDockItem(None)
        super(QDockContainer, self).destroy()

    #--------------------------------------------------------------------------
    # Framework API
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
        name = dock_item.objectName() if dock_item is not None else u''
        self.setObjectName(name)

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

    def reset(self):
        """ Reset the container to the initial pre-docked state.

        """
        state = self.state
        state.dragging = False
        state.press_pos = None
        self.unfloat()
        self.showTitleBar()
        self.setAttribute(Qt.WA_WState_ExplicitShowHide, False)
        self.setAttribute(Qt.WA_WState_Hidden, False)

    def float(self):
        """ Set the window state to be a toplevel floating window.

        """
        self.hide()
        self.state.is_floating = True
        self.setAttribute(Qt.WA_Hover, True)
        flags = Qt.Tool | Qt.FramelessWindowHint
        self.setParent(self.manager().dock_area, flags)
        self.setContentsMargins(QMargins(5, 5, 5, 5))

    def unfloat(self):
        """ Set the window state to be non-floating window.

        """
        self.hide()
        self.state.is_floating = False
        self.setAttribute(Qt.WA_Hover, False)
        flags = Qt.Widget
        self.setParent(self.manager().dock_area, flags)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.unsetCursor()
        self.clearMask()

    def unplug(self):
        """ A convenience method for unplugging the container.

        This method dispatches to the owner manager.

        Returns
        -------
        result : bool
            True if the container was unplugged, False otherwise.

        """
        return self.manager().unplug_container(self)

    def untab(self, pos):
        """ Unplug the container from a tab control.

        This method is invoked by the QDockTabBar when the container
        should be torn out. It synthesizes the appropriate internal
        state so that the item can continue to be dock dragged. This
        method should not be called by user code.

        Parameters
        ----------
        pos : QPoint
            The global mouse position.

        Returns
        -------
        result : bool
            True on success, False otherwise.

        """
        if not self.unplug():
            return False
        state = self.state
        state.dragging = True
        self.float()
        self.manager().raise_frame(self)
        title_bar = self.dockItem().titleBarWidget()
        pos = QPoint(title_bar.width() / 2, title_bar.height() / 2)
        margins = self.contentsMargins()
        offset = QPoint(margins.left(), margins.top())
        state.press_pos = title_bar.mapTo(self, pos) + offset
        self.move(pos - state.press_pos)
        self.show()
        self.grabMouse()
        return True

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock container.

        """
        if event.type() == QEvent.HoverMove:
            return self.hoverMoveEvent(event)
        return super(QDockContainer, self).event(event)

    def resizeEvent(self, event):
        """ Handle the resize event for the container.

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

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the container.

        """
        if self.titleBarMousePressEvent(event):
            event.accept()
            return
        if self.resizeBorderMousePressEvent(event):
            event.accept()
            return
        event.ignore()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the container.

        """
        if self.titleBarMouseMoveEvent(event):
            event.accept()
            return
        if self.resizeBorderMouseMoveEvent(event):
            event.accept()
            return
        event.ignore()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the container.

        """
        if self.titleBarMouseReleaseEvent(event):
            event.accept()
            return
        if self.resizeBorderMouseReleaseEvent(event):
            event.accept()
            return

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the container.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            if state.dragging or state.resize_mode != dwr.NoResize:
                return False
            margins = self.contentsMargins()
            extra = self.ResizeCornerExtra
            mode, ignored = dwr.hit_test(self, event.pos(), margins, extra)
            cursor = dwr.cursor(mode)
            if cursor is None:
                self.unsetCursor()
            else:
                self.setCursor(cursor)
            return True
        return False

    def titleBarMousePressEvent(self, event):
        """ Handle a mouse press event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if event.button() == Qt.LeftButton and state.press_pos is None:
            title_bar = self.dockItem().titleBarWidget()
            if not title_bar.isHidden():
                mapped = title_bar.mapFrom(self, event.pos())
                if title_bar.rect().contains(mapped):
                    state.press_pos = event.pos()
                    return True
        return False

    def titleBarMouseMoveEvent(self, event):
        """ Handle a mouse move event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if state.press_pos is None:
            return False

        # If dragging and floating, move the container's position and
        # notify the manager of that the container was mouse moved.
        global_pos = event.globalPos()
        if state.dragging:
            if state.is_floating:
                self.move(global_pos - state.press_pos)
                self.manager().container_moved(self, global_pos)
            return True

        # Ensure the drag has crossed the app drag threshold.
        dist = (event.pos() - state.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return True

        # If the container is already floating, nothing left to do.
        state.dragging = True
        if state.is_floating:
            return True

        # Unplug the container from the layout before floating so
        # that layout widgets can clean themselves up when empty.
        if not self.unplug():
            return False

        # Make the container a toplevel frame, update it's Z-order,
        # and grab the mouse to continue processing drag events.
        self.float()
        self.manager().raise_frame(self)
        state.press_pos += QPoint(0, self.contentsMargins().top())
        self.move(global_pos - state.press_pos)
        self.show()
        self.grabMouse()
        return True

    def titleBarMouseReleaseEvent(self, event):
        """ Handle a mouse release event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if event.button() == Qt.LeftButton and state.press_pos is not None:
            self.releaseMouse()
            self.manager().container_released(self, event.globalPos())
            state.dragging = False
            state.press_pos = None
            return True
        return False

    def resizeBorderMousePressEvent(self, event):
        """ Handle a mouse press event on the resize border.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if event.button() == Qt.LeftButton and state.is_floating:
            dwr = DockWindowResizer
            margins = self.contentsMargins()
            extra = self.ResizeCornerExtra
            mode, offset = dwr.hit_test(self, event.pos(), margins, extra)
            if mode != dwr.NoResize:
                state.resize_mode = mode
                state.resize_offset = offset
                return True
        return False

    def resizeBorderMouseMoveEvent(self, event):
        """ Handle a mouse move event on the resize border.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            if state.resize_mode != dwr.NoResize:
                mode = state.resize_mode
                offset = state.resize_offset
                dwr.resize(self, event.pos(), mode, offset)
                return True
        return False

    def resizeBorderMouseReleaseEvent(self, event):
        """ Handle a mouse release event on the resize border.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.state
        if state.is_floating:
            state.resize_mode = DockWindowResizer.NoResize
            state.resize_offset = None
            return True
        return False
