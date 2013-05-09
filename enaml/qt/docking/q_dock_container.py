#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QRect
from PyQt4.QtGui import QApplication, QLayout, QIcon

from atom.api import Typed, Bool

from .q_dock_area import QDockArea
from .q_dock_frame import QDockFrame
from .q_dock_frame_layout import QDockFrameLayout


class QDockContainerLayout(QDockFrameLayout):
    """ A QDockFrameLayout subclass which works with a QDockContainer.

    """
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockContainerLayout, self).invalidate()
        widget = self.getWidget()
        if widget is not None:
            self.parentWidget().setSizePolicy(widget.sizePolicy())


class QDockContainer(QDockFrame):
    """ A QDockFrame which holds a QDockItem instance.

    """
    class FrameState(QDockFrame.FrameState):
        """ A private class for managing container drag state.

        """
        #: The original title bar press position.
        press_pos = Typed(QPoint)

        #: Whether or not the dock item is being dragged.
        dragging = Bool(False)

        #: Whether the container is being destroyed.
        destroying = Bool(False)

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
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def showMaximized(self):
        """ Handle a show maximized request for the window.

        """
        if self.isWindow():
            super(QDockContainer, self).showMaximized()
            bar = self.dockItem().titleBarWidget()
            buttons = bar.buttons()
            buttons |= bar.RestoreButton
            buttons &= ~bar.MaximizeButton
            bar.setButtons(buttons)

    def showNormal(self):
        """ Handle a show normal request for the window.

        """
        if self.isWindow():
            super(QDockContainer, self).showNormal()
            bar = self.dockItem().titleBarWidget()
            buttons = bar.buttons()
            buttons |= bar.MaximizeButton
            buttons &= ~bar.RestoreButton
            bar.setButtons(buttons)

    def destroy(self):
        """ Destroy the dock container and release its references.

        """
        state = self.frame_state
        if state.destroying:
            return
        state.destroying = True
        if self.isWindow():
            self.close()
        else:
            self.unplug()
        manager = self.manager()
        if manager is not None:
            manager.dock_items.discard(self.dockItem())
        self.setDockItem(None)
        super(QDockContainer, self).destroy()
        self.deleteLater()
        state.destroying = False

    def titleBarGeometry(self):
        """ Get the geometry rect for the title bar.

        Returns
        -------
        result : QRect
            The geometry rect for the title bar, expressed in frame
            coordinates. An invalid rect is returned if title bar
            should not be active.

        """
        title_bar = self.dockItem().titleBarWidget()
        if title_bar.isHidden():
            return QRect()
        pt = title_bar.mapTo(self, QPoint(0, 0))
        return QRect(pt, title_bar.size())

    def resizeMargins(self):
        """ Get the margins to use for resizing the container.

        Returns
        -------
        result : QMargins
            The margins to use for container resizing when the container
            is a top-level window.

        """
        return self.contentsMargins()

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
        return self.layout().getWidget()

    def setDockItem(self, dock_item):
        """ Set the dock item for the container.

        Parameters
        ----------
        dock_item : QDockItem
            The dock item to use in the container.

        """
        layout = self.layout()
        old = layout.getWidget()
        if old is not None:
            old.maximizeButtonClicked.disconnect(self.showMaximized)
            old.restoreButtonClicked.disconnect(self.showNormal)
            old.closeButtonClicked.disconnect(self.close)
        if dock_item is not None:
            dock_item.maximizeButtonClicked.connect(self.showMaximized)
            dock_item.restoreButtonClicked.connect(self.showNormal)
            dock_item.closeButtonClicked.connect(self.close)
        layout.setWidget(dock_item)
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

    def showControlButtons(self):
        """ Show the maximize button in the title bar.

        """
        # FIXME this is needed during shutdown with a floating window
        item = self.dockItem()
        if item is None:
            return
        title_bar = item.titleBarWidget()
        buttons = title_bar.buttons()
        buttons |= title_bar.MaximizeButton
        buttons &= ~title_bar.RestoreButton
        title_bar.setButtons(buttons)

    def hideControlButtons(self):
        """ Hide the maximize button in the title bar.

        """
        # FIXME this is needed during shutdown with a floating window
        item = self.dockItem()
        if item is None:
            return
        title_bar = item.titleBarWidget()
        buttons = title_bar.buttons()
        buttons &= ~title_bar.MaximizeButton
        buttons &= ~title_bar.RestoreButton
        title_bar.setButtons(buttons)

    def reset(self):
        """ Reset the container to the initial pre-docked state.

        """
        state = self.frame_state
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
        self.showControlButtons()
        self.setAttribute(Qt.WA_Hover, True)
        flags = Qt.Tool | Qt.FramelessWindowHint
        self.setParent(self.manager().dock_area, flags)
        self.setContentsMargins(QMargins(5, 5, 5, 5))

    def unfloat(self):
        """ Set the window state to be non-floating window.

        """
        self.hide()
        self.hideControlButtons()
        self.setAttribute(Qt.WA_Hover, False)
        flags = Qt.Widget
        self.setParent(self.manager().dock_area, flags)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.unsetCursor()

    def unplug(self):
        """ Unplug the container from its containing dock area.

        This method is invoked by the framework when appropriate. It
        should not need to be called by user code.

        Returns
        -------
        result : bool
            True if the container was unplugged, False otherwise.

        """
        dock_area = None
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                dock_area = parent
                break
            parent = parent.parent()
        if dock_area is None:
            return False
        # avoid a circular import
        from .layout_handling import unplug_container
        return unplug_container(dock_area, self)

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
            return
        state = self.frame_state
        state.mouse_title = True
        state.dragging = True
        self.float()
        self.raiseFrame()
        title_bar = self.dockItem().titleBarWidget()
        pos = QPoint(title_bar.width() / 2, title_bar.height() / 2)
        margins = self.contentsMargins()
        offset = QPoint(margins.left(), margins.top())
        state.press_pos = title_bar.mapTo(self, pos) + offset
        self.move(pos - state.press_pos)
        self.show()
        self.grabMouse()
        self.activateWindow()
        self.raise_()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def closeEvent(self, event):
        """ Handle the close event for the dock container.

        """
        item = self.dockItem()
        if item is None or item.close():
            self.destroy()
        else:
            event.ignore()

    def titleBarMousePressEvent(self, event):
        """ Handle a mouse press event on the title bar.

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
        """ Handle a mouse move event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.frame_state
        if state.press_pos is None:
            return False

        # If dragging and floating, move the container's position and
        # notify the manager of that the container was mouse moved.
        global_pos = event.globalPos()
        if state.dragging:
            if self.isWindow():
                if self.isMaximized():
                    coeff = state.press_pos.x() / float(self.width())
                    self.showNormal()
                    margins = self.contentsMargins()
                    button_width = 50  # general approximation
                    max_x = self.width() - margins.right() - button_width
                    test_x = int(coeff * self.width())
                    new_x = max(margins.left() + 5, min(test_x, max_x))
                    title_bar = self.dockItem().titleBarWidget()
                    title_height = title_bar.height() / 2
                    mid_title = title_bar.mapTo(self, QPoint(0, title_height))
                    state.press_pos.setX(new_x)
                    state.press_pos.setY(mid_title.y())
                self.move(global_pos - state.press_pos)
                self.manager().frame_moved(self, global_pos)
            return True

        # Ensure the drag has crossed the app drag threshold.
        dist = (event.pos() - state.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return True

        # If the container is already floating, nothing left to do.
        state.dragging = True
        if self.isWindow():
            return True

        # Unplug the container from the layout before floating so
        # that layout widgets can clean themselves up when empty.
        if not self.unplug():
            return False

        # Make the container a toplevel frame, update it's Z-order,
        # and grab the mouse to continue processing drag events.
        self.float()
        self.raiseFrame()
        state.press_pos += QPoint(0, self.contentsMargins().top())
        self.move(global_pos - state.press_pos)
        self.show()
        self.grabMouse()
        self.activateWindow()
        self.raise_()
        return True

    def titleBarMouseReleaseEvent(self, event):
        """ Handle a mouse release event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is not None:
                self.releaseMouse()
                self.manager().frame_released(self, event.globalPos())
                state.dragging = False
                state.press_pos = None
                return True
        return False
