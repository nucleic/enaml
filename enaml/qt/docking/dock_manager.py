#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Int, Typed, List, atomref

from enaml.layout.dock_layout import DockLayout, DockLayoutValidator

from enaml.qt.QtCore import Qt, QPoint, QRect, QObject
from enaml.qt.QtWidgets import QApplication

from .dock_overlay import DockOverlay
from .layout_handling import layout_hit_test, plug_frame, iter_containers
from .layout_builder import LayoutBuilder
from .layout_saver import LayoutSaver
from .proximity_handler import ProximityHandler
from .q_dock_area import QDockArea
from .q_dock_container import QDockContainer
from .q_dock_window import QDockWindow
from .q_guide_rose import QGuideRose


class DockContainerMonitor(QObject):
    """ A QObject class which monitors dock container toplevel changes.

    """
    def __init__(self, manager):
        """ Initialize a DockContainerMonitor.

        Parameters
        ----------
        mananger : DockManager
            The manager which owns this monitor. Only an atomref will
            be maintained to the manager.

        """
        super(DockContainerMonitor, self).__init__()
        self._manager = atomref(manager)

    def onTopLevelChanged(self, toplevel):
        """ Handle the 'topLevelChanged' signal from a dock container.

        """
        if self._manager:
            handler = self._manager()._proximity_handler
            container = self.sender()
            if toplevel:
                handler.addFrame(container)
            else:
                handler.removeFrame(container)


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    """
    #: The handler which holds the primary dock area.
    _dock_area = Typed(QDockArea)

    #: The overlay used when hovering over a dock area.
    _overlay = Typed(DockOverlay, ())

    #: The list of QDockFrame instances maintained by the manager. The
    #: QDockFrame class maintains this list in proper Z-order.
    _dock_frames = List()

    #: The set of QDockItem instances added to the manager.
    _dock_items = Typed(set, ())

    #: The distance to use for snapping floating dock frames.
    _snap_dist = Int(factory=lambda: QApplication.startDragDistance() * 2)

    #: A proximity handler which manages proximal floating frames.
    _proximity_handler = Typed(ProximityHandler, ())

    #: A container monitor which tracks toplevel container changes.
    _container_monitor = Typed(DockContainerMonitor)

    def _default__container_monitor(self):
        return DockContainerMonitor(self)

    def __init__(self, dock_area):
        """ Initialize a DockingManager.

        Parameters
        ----------
        dock_area : QDockArea
            The primary dock area to be managed. Docking will be
            restricted to this area and to windows spawned by the
            area.

        """
        assert dock_area is not None
        self._dock_area = dock_area
        self._overlay = DockOverlay(dock_area)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dock_area(self):
        """ Get the dock area to which the manager is attached.

        Returns
        -------
        result : QDockArea
            The dock area to which the manager is attached.

        """
        return self._dock_area

    def add_item(self, item):
        """ Add a dock item to the dock manager.

        If the item has already been added, this is a no-op.

        Parameters
        ----------
        items : QDockItem
            The item to be managed by this dock manager. It will be
            reparented to a dock container and made available to the
            the layout system.

        """
        if item in self._dock_items:
            return
        self._dock_items.add(item)
        item._manager = self
        container = QDockContainer(self, self._dock_area)
        container.setDockItem(item)
        container.setObjectName(item.objectName())
        monitor = self._container_monitor
        container.topLevelChanged.connect(monitor.onTopLevelChanged)
        self._dock_frames.append(container)

    def remove_item(self, item):
        """ Remove a dock item from the dock manager.

        If the item has not been added to the manager, this is a no-op.

        Parameters
        ----------
        items : QDockItem
            The item to remove from the dock manager. It will be hidden
            and unparented, but not destroyed.

        """
        if item not in self._dock_items:
            return
        item._manager = None
        for container in self.dock_containers():
            if container.dockItem() is item:
                if not container.isWindow():
                    container.unplug()
                container.hide()
                self._free_container(container)
                break

    def save_layout(self):
        """ Get the current layout of the dock area.

        Returns
        -------
        result : docklayout
            A docklayout instance which represents the current layout
            state.

        """
        items = [self._dock_area] + self.floating_frames()
        return DockLayout(*map(LayoutSaver(), items))

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        Parameters
        ----------
        layout : DockLayout
            The dock layout to apply to the managed area.

        """
        available = (i.objectName() for i in self._dock_items)
        DockLayoutValidator(available)(layout)
        LayoutBuilder(self)(layout)

    def update_layout(self, ops):
        """ Update the layout for a list of layout operations.

        Parameters
        ----------
        ops : list
            A list of LayoutOp objects to use for updating the layout.

        """
        builder = LayoutBuilder(self)
        for op in ops:
            builder(op)

    def destroy(self):
        """ Destroy the dock manager.

        This method will free all of the resources held by the dock
        manager. The primary dock area and dock items will not be
        destroyed. After the method is called, the dock manager is
        invalid and should no longer be used.

        """
        for frame in self._dock_frames:
            if isinstance(frame, QDockContainer):
                frame.setDockItem(None)
                frame.setParent(None, Qt.Widget)
                frame.hide()
        for frame in self._dock_frames:
            if isinstance(frame, QDockWindow):
                frame.setParent(None, Qt.Widget)
                frame.hide()
        for item in self._dock_items:
            item._manager = None
        self._dock_area.setCentralWidget(None)
        self._dock_area.setMaximizedWidget(None)
        del self._dock_area
        del self._dock_frames
        del self._dock_items
        del self._proximity_handler
        del self._container_monitor
        del self._overlay

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def dock_containers(self):
        """ Get an iterable of QDockContainer instances.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Returns
        -------
        result : list
            A list of QDockContainer instances owned by this dock
            manager.

        """
        return [f for f in self._dock_frames if isinstance(f, QDockContainer)]

    def dock_windows(self):
        """ Get an iterable of QDockWindow instances.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Returns
        -------
        result : list
            A list of QDockWindow instances owned by this dock manager.

        """
        return [f for f in self._dock_frames if isinstance(f, QDockWindow)]

    def floating_frames(self):
        """ Get an iterable of floating dock frames.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Returns
        -------
        result : list
            A list toplevel QDockFrame instances.

        """
        return [f for f in self._dock_frames if f.isWindow()]

    def add_window(self, window):
        """ Add a floating QDockWindow to the dock manager.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        window : QDockWindow
            A newly created dock window which should be tracked by
            the dock manager.

        """
        self._dock_frames.append(window)
        self._proximity_handler.addFrame(window)

    def close_container(self, container, event):
        """ Handle a close request for a QDockContainer.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        window : QDockContainer
            The dock container to close.

        event : QCloseEvent
            The close event passed to the event handler.

        """
        item = container.dockItem()
        if item is None or item.close():
            if not container.isWindow():
                container.unplug()
            self._free_container(container)
        else:
            event.ignore()

    def close_window(self, window, event):
        """ Handle a close request for a QDockWindow.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        window : QDockWindow
            The dock window to close.

        event : QCloseEvent
            The close event passed to the event handler.

        """
        area = window.dockArea()
        if area is not None:
            containers = list(iter_containers(area))
            geometries = {}
            for container in containers:
                pos = container.mapToGlobal(QPoint(0, 0))
                size = container.size()
                geometries[container] = QRect(pos, size)
            for container, ignored in area.dockBarContainers():
                containers.append(container)
                size = container.sizeHint()
                geometries[container] = QRect(window.pos(), size)
            for container in containers:
                if not container.close():
                    container.unplug()
                    container.float()
                    container.setGeometry(geometries[container])
                    container.show()
        self._free_window(window)

    def raise_frame(self, frame):
        """ Raise a frame to the top of the Z-order.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        frame : QDockFrame
            The frame to raise to the top of the Z-order.

        """
        frames = self._dock_frames
        handler = self._proximity_handler
        if handler.hasLinkedFrames(frame):
            linked = set(handler.linkedFrames(frame))
            ordered = [f for f in frames if f in linked]
            for other in ordered:
                frames.remove(other)
                frames.append(other)
                other.raise_()
            frame.raise_()
        frames.remove(frame)
        frames.append(frame)

    def frame_resized(self, frame):
        """ Handle the post-processing for a resized floating frame.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        frame : QDockFrame
            The frame which has been resized.

        """
        # If the frame is linked, the resize may have changed the frame
        # geometry such that the existing links are no longer valid.
        # The links are refreshed and the link button state is updated.
        if frame.isLinked():
            handler = self._proximity_handler
            handler.updateLinks(frame)
            if not handler.hasLinkedFrames(frame):
                frame.setLinked(False)

    def drag_move_frame(self, frame, target_pos, mouse_pos):
        """ Move the floating frame to the target position.

        This method is called by a floating frame in response to a user
        moving it by dragging on it's title bar. It takes into account
        neighboring windows and will snap the frame edge to another
        window if it comes close to the boundary. It also ensures that
        the guide overlays are shown at the proper position. This method
        should not be called by user code.

        Parameters
        ----------
        frame : QDockFrame
            The floating QDockFrame which should be moved.

        target_pos : QPoint
            The global position which is the target of the move.

        mouse_pos : QPoint
            The global mouse position.

        """
        # If the frame is linked, it and any of its linked frames are
        # moved the same amount with no snapping. An unlinked window
        # is free to move and will snap to any other floating window
        # that has an opposite edge lying within the snap distance.
        # The overlay is hidden when the frame has proximal frames
        # since such a frame is not allowed to be docked.
        show_drag_overlay = True
        handler = self._proximity_handler
        if frame.isLinked():
            delta = target_pos - frame.pos()
            frame.move(target_pos)
            if handler.hasLinkedFrames(frame):
                show_drag_overlay = False
                for other in handler.linkedFrames(frame):
                    other.move(other.pos() + delta)
        else:
            f_size = frame.frameGeometry().size()
            f_rect = QRect(target_pos, f_size)
            f_x = target_pos.x()
            f_y = target_pos.y()
            f_w = f_size.width()
            f_h = f_size.height()
            dist = self._snap_dist
            filt = lambda n: -dist < n < dist
            for other in handler.proximalFrames(f_rect, dist):
                if other is not frame:
                    o_geo = other.frameGeometry()
                    o_x = o_geo.left()
                    o_y = o_geo.top()
                    o_right = o_x + o_geo.width()
                    o_bottom = o_y + o_geo.height()
                    dx = [c for c in (o_x - f_x,
                                      o_x - (f_x + f_w),
                                      o_right - f_x,
                                      o_right - (f_x + f_w))
                          if filt(c)]
                    if dx:
                        f_x += min(dx)
                    dy = [c for c in (o_y - f_y,
                                      o_y - (f_y + f_h),
                                      o_bottom - f_y,
                                      o_bottom - (f_y + f_h))
                          if filt(c)]
                    if dy:
                        f_y += min(dy)
            frame.move(f_x, f_y)
        if show_drag_overlay:
            self._update_drag_overlay(frame, mouse_pos)
        else:
            self._overlay.hide()

    def drag_release_frame(self, frame, pos):
        """ Handle the dock frame being released by the user.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code. It will redock
        a floating dock item if it is released over a dock guide.

        Parameters
        ----------
        frame : QDockFrame
            The dock frame being dragged by the user.

        pos : QPoint
            The global coordinates of the mouse position.

        """
        # Docking is disallowed for frames which have linked proximal
        # frames, or if the target dock area has a maximized widget.
        # This prevents a situation where the docking logic would be
        # non-sensical and maintains a consistent user experience.
        overlay = self._overlay
        overlay.hide()
        guide = overlay.guide_at(pos)
        if guide == QGuideRose.Guide.NoGuide:
            return
        if self._proximity_handler.hasLinkedFrames(frame):
            return
        builder = LayoutBuilder(self)
        target = self._dock_target(frame, pos)
        if isinstance(target, QDockArea):
            if target.maximizedWidget() is not None:
                return
            with builder.drop_frame(frame):
                local = target.mapFromGlobal(pos)
                widget = layout_hit_test(target, local)
                plug_frame(target, widget, frame, guide)
        elif isinstance(target, QDockContainer):
            with builder.dock_context(target):
                with builder.drop_frame(frame):
                    area = target.parentDockArea()
                    if area is not None:
                        plug_frame(area, target, frame, guide)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _free_container(self, container):
        """ Free the resources attached to the container.

        Parameters
        ----------
        container : QDockContainer
            The container which should be cleaned up. It should be
            unplugged from any layout before being passed to this
            method.

        """
        item = container.dockItem()
        container.setParent(None)
        container.setDockItem(None)
        container._manager = None
        self._dock_items.discard(item)
        self._dock_frames.remove(container)
        self._proximity_handler.removeFrame(container)

    def _free_window(self, window):
        """ Free the resources attached to the window.

        Parameters
        ----------
        window : QDockWindow
            The Window which should be cleaned up.

        """
        window.setParent(None)
        window.setDockArea(None)
        window._manager = None
        self._dock_frames.remove(window)
        self._proximity_handler.removeFrame(window)

    def _iter_dock_targets(self, frame):
        """ Get an iterable of potential dock targets.

        Parameters
        ----------
        frame : QDockFrame
            The frame which is being docked, and therefore excluded
            from the target search.

        Returns
        -------
        result : generator
            A generator which yields the dock container and dock area
            instances which are potential dock targets.

        """
        for target in reversed(self._dock_frames):
            if target is not frame and target.isWindow():
                if isinstance(target, QDockContainer):
                    yield target
                elif isinstance(target, QDockWindow):
                    yield target.dockArea()
        yield self._dock_area

    def _dock_target(self, frame, pos):
        """ Get the dock target for the given frame and position.

        Parameters
        ----------
        frame : QDockFrame
            The dock frame which should be docked.

        pos : QPoint
            The global mouse position.

        Returns
        -------
        result : QDockArea, QDockContainer, or None
            The potential dock target for the frame and position.

        """
        for target in self._iter_dock_targets(frame):
            # Hit test the central pane instead of the entire dock area
            # so that mouse movement over the dock bars is ignored.
            if isinstance(target, QDockArea):
                pane = target.centralPane()
                local = pane.mapFromGlobal(pos)
                if pane.rect().contains(local):
                    return target
            else:
                local = target.mapFromGlobal(pos)
                if target.rect().contains(local):
                    return target

    def _update_drag_overlay(self, frame, pos):
        """ Update the overlay for a dragged frame.

        Parameters
        ----------
        frame : QDockFrame
            The dock frame being dragged by the user.

        pos : QPoint
            The global coordinates of the mouse position.

        """
        overlay = self._overlay
        target = self._dock_target(frame, pos)
        if isinstance(target, QDockContainer):
            local = target.mapFromGlobal(pos)
            overlay.mouse_over_widget(target, local)
        elif isinstance(target, QDockArea):
            # Disallow docking onto an area with a maximized widget.
            # This prevents a non-intuitive user experience.
            if target.maximizedWidget() is not None:
                overlay.hide()
                return
            local = target.mapFromGlobal(pos)
            widget = layout_hit_test(target, local)
            overlay.mouse_over_area(target, widget, local)
        else:
            overlay.hide()
