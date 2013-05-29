#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import warnings

from PyQt4.QtCore import Qt, QPoint, QRect, QObject, QMetaObject
from PyQt4.QtGui import QApplication

from atom.api import Atom, Typed, List

from enaml.layout.dock_layout import docklayout, dockarea, dockitem

from .dock_overlay import DockOverlay
from .event_types import DockAreaContentsChanged
from .layout_handling import (
    build_layout, save_layout, layout_hit_test, plug_frame, iter_containers
)
from .q_dock_area import QDockArea
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


class DockAreaFilter(QObject):
    """ An event filter to listen for content changes in a dock area.

    """
    def eventFilter(self, obj, event):
        """ Filter the events for dock area.

        """
        if event.type() == DockAreaContentsChanged:
            self.processArea(obj)
        return False

    def processArea(self, area):
        """ Process the contents change of a dock area.

        This will close the dock window if there is only one remaining
        container in the dock area.

        Parameters
        ----------
        area : QDockArea
            The dock area whose contents have changed.

        """
        window = area.parent()
        if isinstance(window, QDockWindow):
            widget = area.layoutWidget()
            if widget is None or isinstance(widget, QDockContainer):
                if window.isMaximized():
                    window.showNormal()
                geo = window.geometry()
                area.setLayoutWidget(None)
                if widget is not None:
                    widget.float()
                    widget.setGeometry(geo)
                    attr = Qt.WA_ShowWithoutActivating
                    old = widget.testAttribute(attr)
                    widget.setAttribute(attr, True)
                    widget.show()
                    widget.setAttribute(attr, old)
                    manager = widget.manager()
                    if manager is not None:
                        manager.stack_under_top(widget)
                # Hide before closing, or the window will steal mouse
                # events from the container being dragged, event though
                # the container has grabbed the mouse.
                window.hide()
                # Invoke the close slot later since it would remove this
                # event filter from the dock area while the event is in
                # process resulting in a segfault.
                QMetaObject.invokeMethod(window, 'close', Qt.QueuedConnection)


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    The manager is used by attaching it to a QDockArea and then adding
    dock items via the 'add_item' method and then setting a layout via
    the 'apply_layout' method. See the docstring  of the public api methods for more functionality.

    """
    #: The handler which holds the primary dock area.
    _dock_area = Typed(QDockArea)

    #: The overlay used when hovering over a dock area.
    _overlay = Typed(DockOverlay, ())

    #: The dock area filter installed on floating dock windows.
    _area_filter = Typed(DockAreaFilter, ())

    #: The list of QDockFrame instances maintained by the manager. The
    #: QDockFrame class maintains this list in proper Z-order.
    _dock_frames = List()

    #: The set of QDockItem instances added to the manager.
    _dock_items = Typed(set, ())

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

    def clear_items(self):
        """ Clear the dock items from the dock manager.

        This method will hide and unparent all of the dock items that
        were previously added to the dock manager.

        """
        for frame in self._dock_frames[:]:
            if isinstance(frame, QDockContainer):
                self._free_container(frame)
            else:
                self._free_window(frame)
        del self._dock_frames
        self._dock_area.setLayoutWidget(None)

    def save_layout(self):
        """ Get the current layout of the dock area.

        Returns
        -------
        result : docklayout
            A docklayout instance which represents the current layout
            state.

        """
        primary = None
        secondary = []

        area = self._dock_area
        widget = area.layoutWidget()
        if widget is not None:
            primary = dockarea(save_layout(widget))
            maxed = area.maximizedWidget()
            if maxed is not None:
                primary.maximized_item = maxed.objectName()

        for frame in self._floating_frames():
            if isinstance(frame, QDockWindow):
                area = frame.dockArea()
                item = dockarea(save_layout(area.layoutWidget()))
                maxed = area.maximizedWidget()
                if maxed is not None:
                    item.maximized_item = maxed.objectName()
            else:
                item = save_layout(frame)
            item.maximized = frame.isMaximized()
            if frame.isMaximized():
                geo = frame.normalGeometry()
            else:
                geo = frame.geometry()
            item.geometry = (geo.x(), geo.y(), geo.width(), geo.height())
            secondary.append(item)

        return docklayout(primary, *secondary)

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        Parameters
        ----------
        layout : docklayout
            The docklayout to apply to the managed area.

        """
        # Remove the layout widget before resetting the handlers. This
        # prevents a re-used container from being hidden by the call to
        # setLayoutWidget after it has already been reset. The reference
        # is held to the old widget so the containers are not destroyed
        # before they are reset.
        widget = self._dock_area.layoutWidget()
        self._dock_area.setLayoutWidget(None)
        containers = list(self._dock_containers())
        for container in containers:
            container.reset()
        for window in list(self._dock_windows()):
            window.close()

        # Emit a warning for an item referenced in the layout which
        # has not been added to the dock manager.
        names = set(container.objectName() for container in containers)
        filter_func = lambda item: isinstance(item, dockitem)
        for item in filter(filter_func, layout.traverse()):
            if item.name not in names:
                msg = "dock item '%s' was not found in the dock manager"
                warnings.warn(msg % item.name, stacklevel=2)

        # A convenience closure for populating a dock area.
        def popuplate_area(area, layout):
            widget = build_layout(layout.child, containers)
            area.setLayoutWidget(widget)
            if layout.maximized_item:
                maxed = self._find_container(layout.maximized_item)
                if maxed is not None:
                    maxed.showMaximized()

        # Setup the layout for the primary dock area widget.
        primary = layout.primary
        if primary is not None:
            if isinstance(primary, dockarea):
                popuplate_area(self._dock_area, primary)
            else:
                widget = build_layout(primary, containers)
                self._dock_area.setLayoutWidget(widget)

        # Setup the layout for the secondary floating dock area. This
        # classifies the secondary items according to their type as
        # each type has subtle differences in how they area handled.
        single_items = []
        single_areas = []
        multi_areas = []
        for secondary in layout.secondary:
            if isinstance(secondary, dockitem):
                single_items.append(secondary)
            elif isinstance(secondary.child, dockitem):
                single_areas.append(secondary)
            else:
                multi_areas.append(secondary)

        targets = []
        for item in single_items:
            target = self._find_container(item.name)
            if target is not None:
                target.float()
                targets.append((target, item))
        for item in single_areas:
            target = self._find_container(item.child.name)
            if target is not None:
                target.float()
                targets.append((target, item))
        for item in multi_areas:
            target = QDockWindow.create(self, self._dock_area)
            win_area = target.dockArea()
            popuplate_area(win_area, item)
            win_area.installEventFilter(self._area_filter)
            self._dock_frames.append(target)
            targets.append((target, item))

        for target, item in targets:
            rect = QRect(*item.geometry)
            if rect.isValid():
                rect = ensure_on_screen(rect)
                target.setGeometry(rect)
            target.show()
            if item.maximized:
                target.showMaximized()

    def apply_layout_op(self, op, direction, *item_names):
        """ Apply a layout operation to the managed items.

        Parameters
        ----------
        op : str
            The operation to peform. This must be one of 'split_item',
            'tabify_item', or 'split_area'.

        direction : str
            The direction to peform the operation. This must be one of
            'left', 'right', 'top', or 'bottom'.

        *item_names
            The list of string names of the dock items to include in
            the operation. See the notes about the requirements for
            the item names for a given layout operation.

        """
        handler_name = '_apply_op_' + op
        getattr(self, handler_name)(direction, *item_names)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
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

    def frame_moved(self, frame, pos):
        """ Handle a dock frame being moved by the user.

        This method is called by the framework at the appropriate times
        and should not be called directly by user code. It ensures that
        the dock overlay guides are shown and hidden appropriately.

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
            if target.layoutWidget() is None:
                overlay.mouse_over_widget(target, local, empty=True)
            else:
                widget = layout_hit_test(target, local)
                overlay.mouse_over_area(target, widget, local)
        else:
            overlay.hide()

    def frame_released(self, frame, pos):
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
        overlay = self._overlay
        overlay.hide()
        guide = overlay.guide_at(pos)
        if guide == QGuideRose.Guide.NoGuide:
            return
        target = self._dock_target(frame, pos)
        if isinstance(target, QDockArea):
            # Disallow docking onto an area with a maximized widget.
            # This prevents a non-intuitive user experience.
            if target.maximizedWidget() is not None:
                return
            with self._drop_window_context(frame):
                local = target.mapFromGlobal(pos)
                widget = layout_hit_test(target, local)
                plug_frame(target, widget, frame, guide)
        elif isinstance(target, QDockContainer):
            with self._dock_context(target):
                with self._drop_window_context(frame):
                    area = target.parentDockArea()
                    if area is not None:
                        plug_frame(area, target, frame, guide)

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
            area.removeEventFilter(self._area_filter)
            containers = list(iter_containers(area))
            geometries = {}
            for container in containers:
                pos = container.mapToGlobal(QPoint(0, 0))
                size = container.size()
                geometries[container] = QRect(pos, size)
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

    def _iter_dock_targets(self):
        """ Get an iterable of potential dock targets.

        Returns
        -------
        result : generator
            A generator which yields the dock container and dock area
            instances which are potential dock targets.

        """
        for target in reversed(self._dock_frames):
            if target.isWindow():
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
        for target in self._iter_dock_targets():
            if target is not frame:
                local = target.mapFromGlobal(pos)
                if target.rect().contains(local):
                    return target

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
            window.setGeometry(container.geometry())
            win_area = window.dockArea()
            plug_frame(win_area, None, container, QGuideRose.Guide.AreaCenter)
        yield
        if is_window:
            win_area.installEventFilter(self._area_filter)
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
        yield
        if is_window:
            window.close()

    # A mapping of direction to split item layout metadata.
    _split_item_guides = {
        'left': (QGuideRose.Guide.CompassWest, False),
        'top': (QGuideRose.Guide.CompassNorth, False),
        'right': (QGuideRose.Guide.CompassEast, True),
        'bottom': (QGuideRose.Guide.CompassSouth, True),
    }

    def _apply_op_split_item(self, direction, *item_names):
        """ Handle the 'split_item' layout operation.

        Parameters
        ----------
        direction : LayoutDirection
            The direction in which to perform the split.

        *item_names
            The item names which take part in the operation. There must
            be 2 or more names and they must refer to items which have
            been added to the manager.

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
        """ Handle the 'tabify_item' layout operation.

        Parameters
        ----------
        direction : LayoutDirection
            The direction in which to perform the split.

        *item_names
            The item names which take part in the operation. There must
            be 2 or more names and they must refer to items which have
            been added to the manager.

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
        """ Handle the 'split_area' layout operation.

        Parameters
        ----------
        direction : LayoutDirection
            The direction in which to perform the split.

        *item_names
            The item names which take part in the operation. There must
            be 1 or more names and they must refer to items which have
            been added to the manager.

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
            if area.layoutWidget() is None:
                plug_frame(area, None, container, QGuideRose.Guide.AreaCenter)
            else:
                plug_frame(area, None, container, guide)
