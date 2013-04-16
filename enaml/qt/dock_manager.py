#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QRect, QSize, QMargins
from PyQt4.QtGui import QApplication

from atom.api import Atom, Bool, Typed, List, Dict

from .q_dock_area import QDockArea
from .q_dock_item import QDockItem


class DockItemState(Atom):
    """ A framework class for storing a dock item's state.

    This class should not be used directly by user code.

    """
    #: The original title bar press position.
    press_pos = Typed(QPoint)

    #: Whether or not the dock item is floating.
    floating = Bool(False)

    #: Whether or not the dock item is being dragged.
    dragging = Bool(False)

    #: The size of the dock item when it was last docked.
    docked_size = Typed(QSize)

    #: The geometry of the dock item when it was last floated.
    floated_geo = Typed(QRect)

    #: The area being hovered by the item.
    hover_area = Typed(QDockArea)


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    """
    #: The primary dock area being managed.
    _primary = Typed(QDockArea)

    #: The set of floating dock windows created during undocking. They
    #: are maintained in z-order top-most last.
    _windows = List()

    #: A mapping of dock items to item state structures.
    _states = Dict()

    _foo = Typed(object)

    def __init__(self, dock_area):
        """ Initialize a DockingManager.

        Parameters
        ----------
        dock_area : QDockArea
            The primary dock area to be managed. Docking will be
            restricted to this area and to windows spawned by the
            area.

        """
        self._primary = dock_area

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _find_dock_area(self, item):
        """ Find the dock area which contains the given dock item.

        Parameters
        ----------
        item : QDockItem
            The dock item of interest.

        Returns
        -------
        result : QDockArea or None
            The dock area in which the item currently lives, or None if
            the item is not held within a dock area.

        """
        parent = item.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                return parent
            parent = parent.parent()

    def _iter_areas(self):
        # iterate in top-most z-order
        for win in reversed(self._windows):
            yield win.dockArea()
        yield self._primary

    def _hover_item(self, item, event):
        state = self._states[item]
        skip_area = state.dock_window.dockArea()
        global_pos = event.globalPos()
        for area in self._iter_areas():
            if area is skip_area:
                continue
            geo = QRect(area.mapToGlobal(QPoint(0, 0)), area.size())
            if geo.contains(global_pos):
                if state.hover_area and state.hover_area is not area:
                    state.hover_area.endHover(item, global_pos)
                area.hover(item, global_pos)
                state.hover_area = area
                break
        else:
            if state.hover_area is not None:
                state.hover_area.endHover(item, global_pos)
                state.hover_area = None

    def _move_item(self, item, event):
        state = self._states[item]
        delta = event.pos() - state.press_pos
        target_win = state.dock_window
        target_win.move(target_win.pos() + delta)
        self._hover_item(item, event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def release_items(self):
        for item in self._states:
            item.dock_manager = None
        del self._states

    def add_item(self, item):
        assert isinstance(item, QDockItem)
        if item not in self._states:
            self._states[item] = DockItemState()
            item.dock_manager = self

    def remove_item(self, item):
        assert isinstance(item, QDockItem)
        state = self._states.pop(item, None)
        if state is not None:
            state.dock_manager = None

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def window_activated(self, window):
        # FIXME a linked list may be faster. But this list will be
        # so small it probably won't make an effective difference.
        if window in self._windows:
            self._windows.remove(window)
            self._windows.append(window)

    def mouse_press_event(self, item, event):
        state = self._states.get(item)
        if state is None:
            return False
        if event.button() == Qt.LeftButton:
            if state.press_pos is None:
                title_bar = item.titleBarWidget()
                if title_bar.geometry().contains(event.pos()):
                    pos = item.mapToParent(event.pos())
                    pos.setY(pos.y() + 5)
                    state.press_pos = pos
                    return True
        return False

    def mouse_release_event(self, item, event):
        state = self._states.get(item)
        if state is None:
            return False
        if event.button() == Qt.LeftButton:
            if state.press_pos is not None:
                item.releaseMouse()
                state.dragging = False
                state.press_pos = None
                if state.hover_area is not None:
                    state.hover_area.endHover(item, event.globalPos())
                    state.hover_area = None
                return True

    def mouse_move_event(self, item, event):
        state = self._states.get(item)
        if state is None:
            return False

        # Protect against being called with invalid state.
        if state.press_pos is None:
            return False

        container = item.parent()
        if container is None:
            return False

        # Dragging the title bar when the item is the only item in a
        # dock window causes the dock window to be moved and hovered.
        # If there is more than one item in the dock window, then the
        # item is free to be undocked as normal.
        if state.dragging:
            if state.floating:
                container.move(event.globalPos() - state.press_pos)
            return True

        # Start dragging if distances exceeds app drag threshold.
        pos = item.mapToParent(event.pos())
        dist = (pos - state.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return
        state.dragging = True

        # If item is already in a floating window, nothing more needs
        # to be done; the next call to this method will move the window
        # if it only contains a single dock item.
        if state.floating:
            return True

        dock_area = self._find_dock_area(item)
        if dock_area is None:
            return False

        print container.size()
        container = item.parent()
        dock_area.layout().unplug(container)
        container.setFloating(True)
        flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        container.setParent(dock_area, flags)
        container.move(event.globalPos())
        container.show()
        print container.size()

        state.floating = True

        # Grab the mouse so that move events continue to be sent to
        # the item even though it got reparented.
        item.grabMouse()

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    # def hover(self, item, pos):
    #     """ Execute a hover operation for a dock item.

    #     This method is called by the docking framework as needed. It
    #     should not be called by user code.

    #     Parameters
    #     ----------
    #     item : QDockItem
    #         The dock item which is being hovered.

    #     pos : QPoint
    #         The global coordinates of the hover position.

    #     """
    #     local = self.mapFromGlobal(pos)
    #     if self.rect().contains(local):
    #         self._overlays.hover(local)
    #         return True
    #     else:
    #         self._overlays.hide()
    #         return False

    # def endHover(self, item, pos):
    #     """ End a hover operation for a dock item.

    #     This method is called by the docking framework as needed. It
    #     should not be called by user code.

    #     Parameters
    #     ----------
    #     item : QDockItem
    #         The dock item which is being hovered.

    #     pos : QPoint
    #         The global coordinates of the hover position.

    #     Returns
    #     -------
    #     result : bool
    #         True if the pos is over a dock guide, False otherwise.

    #     """
    #     self._overlays.hide()
    #     local = self.mapFromGlobal(pos)
    #     if self.rect().contains(local):
    #         guide = self._overlays.hit_test_rose(local)
    #         return guide != QGuideRose.Guide.NoGuide
    #     return False
