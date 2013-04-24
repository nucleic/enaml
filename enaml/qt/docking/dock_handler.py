#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QSize, QRect
from PyQt4.QtGui import QApplication

from atom.api import Atom, Bool, Typed, ForwardTyped

from .layout_handling import unplug_container
from .q_dock_area import QDockArea
from .q_dock_container import QDockContainer


def DockManager():
    from .dock_manager import DockManager
    return DockManager


class DockHandler(Atom):
    """ A base class for defining handler objects used by a dock manager.

    """
    #: The original title bar press position.
    press_pos = Typed(QPoint)

    #: Whether or not the dock item is floating.
    floating = Bool(False)

    #: Whether or not the dock item is being dragged.
    dragging = Bool(False)

    #: Whether the cursor has been grabbed at the application level.
    grabbed_cursor = Bool(False)

    #: The size of the dock item when it was last docked.
    docked_size = Typed(QSize)

    #: The geometry of the dock item when it was last floated.
    floated_geo = Typed(QRect)

    #: The dock container which owns the dock item.
    dock_container = Typed(QDockContainer)

    #: The dock manager which owns the handler.
    manager = ForwardTyped(DockManager)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _raise(self):
        """ Raise this handler in the sibling Z-order.

        """
        siblings = self.manager.handlers
        siblings.remove(self)
        siblings.append(self)

    def _unplug(self):
        """ Unplug the container from its dock area.

        This method assumes the provided container is in a state which
        is suitable for unplugging. If the operation is successful, the
        container will be hidden and its parent will be None.

        Returns
        -------
        result : bool
            True if unplugging was a success, False otherwise.

        """
        dock_area = None
        container = self.dock_container
        parent = container.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                dock_area = parent
                break
            parent = parent.parent()
        if dock_area is None:
            return False
        return unplug_container(dock_area, container)

    def _dock_drag(self, pos):
        """ Handle a floating dock container drag.

        This method will forward the drag notification to the dock
        manager so that it can display the guide overlays.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse.

        """
        self.manager.dock_drag(self, pos)

    def _end_dock_drag(self, pos):
        """ End the dock drag operation for the handler.

        This method will notify the dock manager of the drag end. The
        manager will replug the container if necessary.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse.

        """
        self.manager.end_dock_drag(self, pos)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def name(self):
        """ Get the object name of the managed dock container.

        """
        return self.dock_container.objectName()

    def reset(self):
        """ Reset the handler to the initial pre-docked state.

        """
        self.floating = False
        self.dragging = False
        self.press_pos = None
        container = self.dock_container
        container.hide()
        container.showTitleBar()
        container.setFloating(False)
        container.setParent(self.manager.dock_area, Qt.Widget)
        container.setAttribute(Qt.WA_WState_ExplicitShowHide, False)
        container.setAttribute(Qt.WA_WState_Hidden, False)

    def untab(self, pos):
        """ Unplug the container from a tab control.

        This method is invoked by the QDockTabBar when the container
        should be torn out. It synthesizes the appropriate internal
        state so that the item can continue to be dock dragged.

        Parameters
        ----------
        pos : QPoint
            The global mouse position.

        """
        if not self._unplug():
            return False
        self._raise()
        self.dragging = True
        self.floating = True
        container = self.dock_container
        container.setFloating(True)
        dock_item = container.dockItem()
        title_bar = dock_item.titleBarWidget()
        margins = container.contentsMargins()
        x = title_bar.width() / 2 + margins.left()
        y = title_bar.height() / 2 + margins.top()
        self.press_pos = QPoint(x, y)
        flags = Qt.Tool | Qt.FramelessWindowHint
        container.setParent(self.manager.dock_area, flags)
        container.move(pos - self.press_pos)
        container.show()
        dock_item.grabMouse()

        # Override the cursor as a workaround for the cursor flashing
        # between arrow and ibeam when undocking an item with a text
        # input area which is close to the title bar. This is restored
        # on the mouse release event.
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.grabbed_cursor = True

        return True

    def float(self, geometry):
        """ Make the handler a floating window.

        This method is invoked by the DockManager to make the container
        a floating window during layout. The handler should be 'reset()'
        before this method is called.

        Parameters
        ----------
        geometry : QRect
            Optional initial geometry to apply to the container before
            it is shown. An invalid QRect is an indication to use the
            default geometry.

        """
        self._raise()
        self.floating = True
        container= self.dock_container
        container.setFloating(True)
        container.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        if geometry.isValid():
            container.setGeometry(geometry)
        container.show()

    #--------------------------------------------------------------------------
    # QDockContainer Handler Methods
    #--------------------------------------------------------------------------
    def window_activated(self):
        """ Handle the window activated event for the dock container.

        This handler is invoked by the container when it receives a
        WindowActivate event while floating. It is used to maintain
        knowledge of the Z-order of floating windows.

        """
        self._raise()

    #--------------------------------------------------------------------------
    # QDockItem Handler Methods
    #--------------------------------------------------------------------------
    def mouse_press_event(self, event):
        """ Handle a mouse press event for the dock item.

        This handler initializes the drag state when the mouse press
        occurs on the title bar widget of the dock item.

        Returns
        -------
        result : bool
            True if the event was handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            if self.press_pos is None:
                container = self.dock_container
                dock_item = container.dockItem()
                title_bar = dock_item.titleBarWidget()
                if not title_bar.isHidden():
                    if title_bar.geometry().contains(event.pos()):
                        pos = dock_item.mapTo(container, event.pos())
                        self.press_pos = pos
                        return True
        return False

    def mouse_move_event(self, event):
        """ Handle a mouse move event for the dock item.

        This handler manages docking and undocking the item.

        """
        # Protect against being called with bad state. This can happen
        # when clicking and dragging a child of the item which doesn't
        # handle the move event.
        if self.press_pos is None:
            return False

        # If the title bar is dragged while the container is floating,
        # the container is moved to the proper location.
        global_pos = event.globalPos()
        container = self.dock_container
        if self.dragging:
            if self.floating:
                container.move(global_pos - self.press_pos)
                self._dock_drag(global_pos)
            return True

        dock_item = container.dockItem()
        pos = dock_item.mapTo(container, event.pos())
        dist = (pos - self.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return False

        # If the container is already floating, there is nothing to do.
        # The call to this event handler will move the container.
        self.dragging = True
        if self.floating:
            return True

        if not self._unplug():
            return False

        self._raise()
        self.floating = True
        container.setFloating(True)
        self.press_pos += QPoint(0, container.contentsMargins().top())
        flags = Qt.Tool | Qt.FramelessWindowHint
        container.setParent(self.manager.dock_area, flags)
        container.move(global_pos - self.press_pos)
        container.show()
        dock_item.grabMouse()

        # Override the cursor as a workaround for the cursor flashing
        # between arrow and ibeam when undocking an item with a text
        # input area which is close to the title bar. This is restored
        # on the mouse release event.
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.grabbed_cursor = True

        return True

    def mouse_release_event(self, event):
        """ Handle a mouse release event for the dock item.

        This handler ends the drag state for the dock item.

        Returns
        -------
        result : bool
            True if the event was handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            if self.press_pos is not None:
                if self.grabbed_cursor:
                    QApplication.restoreOverrideCursor()
                    self.grabbed_cursor = False
                self.dock_container.dockItem().releaseMouse()
                if self.floating:
                    self._end_dock_drag(event.globalPos())
                self.dragging = False
                self.press_pos = None
                return True
        return False
