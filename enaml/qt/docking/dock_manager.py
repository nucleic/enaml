#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
from contextlib import contextmanager
import warnings

from atom.api import Atom, Int, Typed, List, atomref

from enaml.layout.dock_layout import (
    DockLayout, AreaLayout, DockBarLayout, ItemLayout
)
from enaml.nodevisitor import NodeVisitor

from enaml.qt.QtCore import Qt, QPoint, QRect, QObject
from enaml.qt.QtGui import QApplication

from .dock_overlay import DockOverlay
from .layout_handling import (
    LayoutWidgetBuilder, LayoutWidgetSaver, layout_hit_test, plug_frame,
    iter_containers
)
from .proximity_handler import ProximityHandler
from .q_dock_area import QDockArea
from .q_dock_bar import QDockBar
from .q_dock_container import QDockContainer
from .q_dock_window import QDockWindow
from .q_guide_rose import QGuideRose


def ensure_on_screen(rect):
    """ Ensure that the given rect is contained on screen.

    If the origin of the rect is not contained within the closest
    desktop screen, the rect will be moved so that it is fully on the
    closest screen. If the rect is larger than the closest screen, the
    origin will never be less than the screen origin.

    Parameters
    ----------
    rect : QRect
        The geometry rect of interest.

    """
    d = QApplication.desktop()
    pos = rect.topLeft()
    drect = d.screenGeometry(pos)
    if not drect.contains(pos):
        x = pos.x()
        if x < drect.x() or x > drect.right():
            dw = drect.width() - rect.width()
            x = max(drect.x(), drect.x() + dw)
        y = pos.y()
        if x < drect.top() or y > drect.bottom():
            dh = drect.height() - rect.height()
            y = max(drect.y(), drect.y() + dh)
        rect = QRect(x, y, rect.width(), rect.height())
    return rect


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


class LayoutHandler(NodeVisitor):

    BAR_POSITIONS = {
        'top': QDockBar.North,
        'right': QDockBar.East,
        'bottom': QDockBar.South,
        'left': QDockBar.West,
    }

    BORDER_GUIDES = {
        'top': QGuideRose.Guide.BorderNorth,
        'right': QGuideRose.Guide.BorderEast,
        'bottom': QGuideRose.Guide.BorderSouth,
        'left': QGuideRose.Guide.BorderWest,
    }

    ITEM_GUIDES = {
        'top': QGuideRose.Guide.CompassNorth,
        'right': QGuideRose.Guide.CompassEast,
        'bottom': QGuideRose.Guide.CompassSouth,
        'left': QGuideRose.Guide.CompassWest,
    }

    TAB_GUIDES = {
        'default': QGuideRose.Guide.CompassCenter,
        'top': QGuideRose.Guide.CompassExNorth,
        'right': QGuideRose.Guide.CompassExEast,
        'bottom': QGuideRose.Guide.CompassExSouth,
        'left': QGuideRose.Guide.CompassExWest,
    }

    def __init__(self, manager):
        containers = manager._dock_containers()
        available = dict((c.objectName(), c) for c in containers)
        self._manager = manager
        self._available = available
        self._widget_builder = LayoutWidgetBuilder(available)

    #--------------------------------------------------------------------------
    # DockLayoutOp Handlers
    #--------------------------------------------------------------------------
    def visit_InsertItem(self, op):
        """ Handle the InsertItem dock layout operation.

        """
        item = self._available.get(op.item)
        if item is None:
            return
        target = self._available.get(op.target)
        if target is None:
            self.visit_InsertBorderItem(op)  # duck typing
            return

        if not item.isWindow():
            item.unplug()

        area = target.parentDockArea()
        bar_position = area.dockBarPosition(target)
        if bar_position is not None:
            if item.isWindow():
                item.unfloat()
            item.showTitleBar()
            area.addToDockBar(item, bar_position)
            return

        with self._manager._dock_context(target):
            area = target.parentDockArea()
            widget = target.parentDockTabWidget() or target
            plug_frame(area, widget, item, self.ITEM_GUIDES[op.position])

    def visit_InsertBorderItem(self, op):
        """ Handle the InsertBorderItem dock layout operation.

        """
        item = self._available.get(op.item)
        if item is None:
            return

        if not item.isWindow():
            item.unplug()

        guide = self.BORDER_GUIDES[op.position]
        target = self._available.get(op.target)
        if target is None:
            area = self._manager.dock_area
            if area.centralWidget() is None:
                guide = QGuideRose.Guide.AreaCenter
            plug_frame(area, None, item, guide)
        else:
            with self._manager._dock_context(target):
                area = target.parentDockArea()
                if area.centralWidget() is None:
                    guide = QGuideRose.Guide.AreaCenter
                plug_frame(area, None, item, guide)

    def visit_InsertDockBarItem(self, op):
        """ Handle the InsertDockBarItem dock layout operation.

        """
        item = self._available.get(op.item)
        if item is None:
            return

        if item.isWindow():
            item.unfloat()
        else:
            item.unplug()
        item.showTitleBar()

        position = self.BAR_POSITIONS[op.position]
        target = self._available.get(op.target)
        if target is None:
            area = self._manager.dock_area
            area.addToDockBar(item, position, op.index)
        else:
            with self._manager._dock_context(target):
                area = target.parentDockArea()
                area.addToDockBar(item, position, op.index)

    def visit_InsertTab(self, op):
        """ Handle the InsertTab dock layout operation.

        """
        item = self._available.get(op.item)
        if item is None:
            return

        if not item.isWindow():
            item.unplug()

        target = self._available.get(op.target)
        if target is None:
            area = self._manager.dock_area
            if area.centralWidget() is None:
                guide = QGuideRose.Guide.AreaCenter
            else:
                guide = QGuideRose.Guide.BorderWest
            plug_frame(area, None, item, guide)
            return

        area = target.parentDockArea()
        bar_position = area.dockBarPosition(target)
        if bar_position is not None:
            if item.isWindow():
                item.unfloat()
            item.showTitleBar()
            area.addToDockBar(item, bar_position)
            return

        with self._manager._dock_context(target):
            area = target.parentDockArea()
            widget = target.parentDockTabWidget()
            if widget is None:
                widget = target
                guide = self.TAB_GUIDES[op.tab_position]
            else:
                guide = QGuideRose.Guide.CompassCenter
            plug_frame(area, widget, item, guide)
            tabs = target.parentDockTabWidget()
            index = tabs.indexOf(item)
            tabs.tabBar().moveTab(index, op.index)

    def visit_CreateFloatingItem(self, op):
        """ Handle the CreateFloatingItem dock layout op.

        """
        layout = op.item
        container = self._available.get(layout.name)
        if container is None:
            return
        if not container.isWindow():
            container.unplug()
            container.float()
        self.init_floating_frame(container, layout)

    def visit_CreateFloatingArea(self, op):
        manager = self._manager
        frame = QDockWindow.create(manager, manager._dock_area)
        self.init_dock_area(frame.dockArea(), op.area)
        manager._dock_frames.append(frame)
        manager._proximity_handler.addFrame(frame)
        self.init_floating_frame(frame, op.area)

    def visit_RemoveItem(self, op):
        container = self._available.get(op.item)
        if container is None:
            return
        if container.isWindow():
            container.unfloat()
        else:
            container.unplug()
        container.hide()

    def default_visit(self, node):
        pass

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def init_dock_area(self, area, layout):
        available = self._available
        if layout.item is not None:
            area.setCentralWidget(self._widget_builder(layout.item))
        for bar_layout in layout.dock_bars:
            position = self.BAR_POSITIONS[bar_layout.position]
            for item in bar_layout.items:
                container = available.get(item.name)
                if container is not None:
                    area.addToDockBar(container, position)
        for item in layout.find_all(ItemLayout):
            if item.maximized:
                container = available.get(item.name)
                if container is not None:
                    container.showMaximized()
                    break

    def init_floating_frame(self, frame, layout):
        rect = QRect(*layout.geometry)
        if rect.isValid():
            rect = ensure_on_screen(rect)
            frame.setGeometry(rect)
        frame.show()
        if layout.linked:
            frame.setLinked(True)
        if layout.maximized:
            frame.showMaximized()


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
        container = self._find_container(item.objectName())
        if container is not None:
            if container.isWindow():
                container.unplug()
            container.hide()
            self._free_container(container)

    def destroy(self):
        """ Destroy the dock manager.

        This method will free all of the resources held by the dock
        manager. The primary dock area and dock items will not be
        destroyed.

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
        self._dock_area.setCentralWidget(None)
        self._dock_area.setMaximizedWidget(None)
        del self._dock_area
        del self._dock_frames
        del self._dock_items
        del self._proximity_handler
        del self._container_monitor
        del self._overlay

    def save_layout(self):
        """ Get the current layout of the dock area.

        Returns
        -------
        result : docklayout
            A docklayout instance which represents the current layout
            state.

        """
        layout_saver = LayoutWidgetSaver()
        bar_positions = {
            QDockBar.North: 'top',
            QDockBar.East: 'right',
            QDockBar.South: 'bottom',
            QDockBar.West: 'left',
        }

        def make_area_node(area):
            widget = area.centralWidget()
            if widget is None:
                node = AreaLayout()
            else:
                node = AreaLayout(layout_saver(widget))
            bar_data = defaultdict(list)
            for container, position in area.dockBarContainers():
                bar_data[position].append(container.objectName())
            for bar_pos, names in bar_data.iteritems():
                bar = DockBarLayout(*names, position=bar_positions[bar_pos])
                node.dock_bars.append(bar)
            maxed = area.maximizedWidget()
            if maxed is not None:
                name = maxed.objectName()
                for item in node.find_all(ItemLayout):
                    if item.name == name:
                        item.maximized = True
                        break
            return node

        def make_frame_node(frame):
            if isinstance(frame, QDockWindow):
                node = make_area_node(frame.dockArea())
            else:
                node = layout_saver(frame)
            node.linked = frame.isLinked()
            node.maximized = frame.isMaximized()
            if frame.isMaximized():
                geo = frame.normalGeometry()
            else:
                geo = frame.geometry()
            node.geometry = (geo.x(), geo.y(), geo.width(), geo.height())
            return node

        primary = make_area_node(self._dock_area)
        secondary = map(make_frame_node, self._floating_frames())
        items = [primary] + secondary
        return DockLayout(*items)

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        Parameters
        ----------
        layout : DockLayout
            The DockLayout to apply to the managed area.

        """
        assert isinstance(layout, DockLayout)
        # Remove the layout widget before resetting the handlers. This
        # prevents a re-used container from being hidden by the call to
        # setCentralWidget after it has already been reset. The reference
        # is held to the old widget so the containers are not destroyed
        # before they are reset.
        ignored = self._dock_area.centralWidget()
        self._dock_area.setCentralWidget(None)
        containers = list(self._dock_containers())
        for container in containers:
            container.reset()
        for window in list(self._dock_windows()):
            window.close()
        self._dock_area.clearDockBars()
        available = dict((c.objectName(), c) for c in containers)

        layout_builder = LayoutWidgetBuilder(available)
        bar_positions = {
            'top': QDockBar.North,
            'right': QDockBar.East,
            'bottom': QDockBar.South,
            'left': QDockBar.West,
        }

        def populate_area(area, layout):
            if layout.item is not None:
                area.setCentralWidget(layout_builder(layout.item))
            for bar_layout in layout.dock_bars:
                position = bar_positions[bar_layout.position]
                for item in bar_layout.items:
                    container = available.get(item.name)
                    if container is not None:
                        area.addToDockBar(container, position)
            for item in layout.find_all(ItemLayout):
                if item.maximized:
                    container = available.get(item.name)
                    if container is not None:
                        container.showMaximized()
                        break

        primary_area = None
        floating_frames = []
        for item in layout.items:
            if isinstance(item, AreaLayout):
                if not item.floating and primary_area is None:
                    primary_area = item
                else:
                    frame = QDockWindow.create(self, self._dock_area)
                    populate_area(frame.dockArea(), item)
                    self._dock_frames.append(frame)
                    self._proximity_handler.addFrame(frame)
                    floating_frames.append((frame, item))
            else:
                frame = available.get(item.name)
                if frame is not None:
                    frame.float()
                    floating_frames.append((frame, item))

        if primary_area is not None:
            populate_area(self._dock_area, primary_area)

        for frame, item in floating_frames:
            rect = QRect(*item.geometry)
            if rect.isValid():
                rect = ensure_on_screen(rect)
                frame.setGeometry(rect)
            frame.show()
            if item.linked:
                frame.setLinked(True)
            if item.maximized:
                frame.showMaximized()

    def update_layout(self, ops):
        handler = LayoutHandler(self)
        for op in ops:
            handler(op)

    def apply_layout_op(self, op, direction, *item_names):
        """ This method is deprecated.

        """
        handler_name = '_apply_op_' + op
        getattr(self, handler_name)(direction, *item_names)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def frame_resized(self, frame):
        """ Handle the post-process for a resized floating frame.

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
            ordered = []
            for index, other in enumerate(frames):
                if other in linked:
                    ordered.append((index, other))
            ordered.sort()
            for ignored, other in ordered:
                frames.remove(other)
                frames.append(other)
                other.raise_()
            frame.raise_()
        frames.remove(frame)
        frames.append(frame)

    def stack_under_top(self, frame):
        """ Stack the given frame under the top frame in the Z-order.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code.

        Parameters
        ----------
        frame : QDockFrame
            The frame to stack under the top frame in the Z-order.

        """
        frames = self._dock_frames
        frames.remove(frame)
        frames.insert(-1, frame)

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
                    dx = filter(filt, (
                        o_x - f_x,
                        o_x - (f_x + f_w),
                        o_right - f_x,
                        o_right - (f_x + f_w),
                    ))
                    if dx:
                        f_x += min(dx)
                    dy = filter(filt, (
                        o_y - f_y,
                        o_y - (f_y + f_h),
                        o_bottom - f_y,
                        o_bottom - (f_y + f_h),
                    ))
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
        target = self._dock_target(frame, pos)
        if isinstance(target, QDockArea):
            if target.maximizedWidget() is not None:
                return
            with self._drop_window_context(frame) as ctxt:
                local = target.mapFromGlobal(pos)
                widget = layout_hit_test(target, local)
                success = plug_frame(target, widget, frame, guide)
                ctxt['success'] = success
        elif isinstance(target, QDockContainer):
            with self._dock_context(target):
                with self._drop_window_context(frame) as ctxt:
                    area = target.parentDockArea()
                    if area is not None:
                        success = plug_frame(area, target, frame, guide)
                        ctxt['success'] = success

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
        QDockWindow.free(window)

    def _dock_containers(self):
        """ Get an iterable of QDockContainer instances.

        Returns
        -------
        result : generator
            A generator which yields the QDockContainer instances owned
            by this dock manager.

        """
        for frame in self._dock_frames:
            if isinstance(frame, QDockContainer):
                yield frame

    def _dock_windows(self):
        """ Get an iterable of QDockWindow instances.

        Returns
        -------
        result : generator
            A generator which yields the QDockWindow instances owned
            by this dock manager.

        """
        for frame in self._dock_frames:
            if isinstance(frame, QDockWindow):
                yield frame

    def _floating_frames(self):
        """ Get an iterable of floating dock frames.

        Returns
        -------
        result : generator
            A generator which yield toplevel QDockFrame instances.

        """
        for frame in self._dock_frames:
            if frame.isWindow():
                yield frame

    def _find_container(self, name):
        """ Find the dock container with the given object name.

        Parameters
        ----------
        name : basestring
            The object name of the dock container to locate.

        Returns
        -------
        result : QDockContainer or None
            The dock container for the given object name or None.

        """
        for container in self._dock_containers():
            if container.objectName() == name:
                return container

    def _find_containers(self, names, missing=None):
        """ Find the dock containers with the given names.

        Parameters
        ----------
        names : iterable
            An iterable of names of the containers to find.

        missing : callable, optional
            A callable which will be invoked with the name of any
            container which is not found.

        Returns
        -------
        result : list
            The list of QDockContainers which were found.

        """
        cs = dict((c.objectName(), c) for c in self._dock_containers())
        res = []
        for name in names:
            if name in cs:
                res.append(cs[name])
            elif missing is not None:
                missing(name)
        return res

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

    @contextmanager
    def _dock_context(self, container):
        """ Setup a dock context for a dock container.

        This context manager ensures handled setting up the QDockWindow
        for a floating dock container. It ensures that the container
        will have a proper dock area for adding new items.

        Parameters
        ----------
        container : QDockContainer
            The dock container onto which another container is to
            be docked.

        """
        window = None
        win_area = None
        is_maxed = False
        is_window = container.isWindow()
        if is_window:
            is_maxed = container.isMaximized()
            if is_maxed:
                container.showNormal()
            window = QDockWindow.create(self, self._dock_area)
            self._dock_frames.append(window)
            self._proximity_handler.addFrame(window)
            window.setGeometry(container.geometry())
            win_area = window.dockArea()
            plug_frame(win_area, None, container, QGuideRose.Guide.AreaCenter)
        yield
        if is_window:
            window.show()
            if is_maxed:
                window.showMaximized()

    @contextmanager
    def _drop_window_context(self, window):
        """ Setup a drop contents for a dock window.

        This context manager prepares a QDockWindow to be dropped onto
        a dock area or dock container.

        Parameters
        ----------
        window : object
            The window of interest. The method will only operate on
            instances of QDockWindow, but it is safe to pass any other
            type.

        """
        is_window = isinstance(window, QDockWindow)
        if is_window:
            win_area = window.dockArea()
            maxed = win_area.maximizedWidget()
            if maxed is not None:
                container = self._find_container(maxed.objectName())
                if container is not None:
                    container.showNormal()
        ctxt = {'success': False}
        yield ctxt
        if is_window and ctxt['success']:
            window.close()

    # A mapping of direction to split item layout metadata.
    _split_item_guides = {
        'left': (QGuideRose.Guide.CompassWest, False),
        'top': (QGuideRose.Guide.CompassNorth, False),
        'right': (QGuideRose.Guide.CompassEast, True),
        'bottom': (QGuideRose.Guide.CompassSouth, True),
    }

    def _apply_op_split_item(self, direction, *item_names):
        """ This method is deprecated.

        """
        def missing(name):
            msg = "dock item '%s' was not found in the dock manager"
            warnings.warn(msg % name, stacklevel=5)
        containers = self._find_containers(item_names, missing)
        if len(containers) < 2:
            return

        # The items are reversed before inserting to the right or
        # to the bottom so that the net effect is a proper insert
        # order for the entire group.
        primary = containers.pop(0)
        guide, reverse = self._split_item_guides[direction]
        tabs = primary.parentDockTabWidget()
        if tabs is not None:
            guide = QGuideRose.Guide.CompassCenter
        if reverse and tabs is None:
            containers.reverse()

        with self._dock_context(primary):
            for container in containers:
                if container is primary:
                    continue
                area = primary.parentDockArea()
                if area is None:
                    continue
                container.unplug()
                plug_frame(area, tabs or primary, container, guide)

    # A mapping of direction to tabify item layout metadata.
    _tabify_item_guides = {
        'left': QGuideRose.Guide.CompassExWest,
        'top': QGuideRose.Guide.CompassExNorth,
        'right': QGuideRose.Guide.CompassExEast,
        'bottom': QGuideRose.Guide.CompassExSouth,
    }

    def _apply_op_tabify_item(self, direction, *item_names):
        """ This method is deprecated.

        """
        def missing(name):
            msg = "dock item '%s' was not found in the dock manager"
            warnings.warn(msg % name, stacklevel=5)
        containers = self._find_containers(item_names, missing)
        if len(containers) < 2:
            return

        primary = containers.pop(0)
        with self._dock_context(primary):
            for container in containers:
                if container is primary:
                    continue
                area = primary.parentDockArea()
                if area is None:
                    continue
                container.unplug()
                tabs = primary.parentDockTabWidget()
                if tabs is not None:
                    guide = QGuideRose.Guide.CompassCenter
                    plug_frame(area, tabs, container, guide)
                else:
                    guide = self._tabify_item_guides[direction]
                    plug_frame(area, primary, container, guide)

    _split_area_guides = {
        'left': (QGuideRose.Guide.BorderWest, True),
        'top': (QGuideRose.Guide.BorderNorth, True),
        'right': (QGuideRose.Guide.BorderEast, False),
        'bottom': (QGuideRose.Guide.BorderSouth, False),
    }

    def _apply_op_split_area(self, direction, *item_names):
        """ This method is deprecated.

        """
        def missing(name):
            msg = "dock item '%s' was not found in the dock manager"
            warnings.warn(msg % name, stacklevel=5)
        containers = self._find_containers(item_names, missing)
        if len(containers) < 1:
            return

        guide, reverse = self._split_area_guides[direction]
        if reverse:
            containers.reverse()

        area = self._dock_area
        for container in containers:
            container.unplug()
            if area.centralWidget() is None:
                plug_frame(area, None, container, QGuideRose.Guide.AreaCenter)
            else:
                plug_frame(area, None, container, guide)
