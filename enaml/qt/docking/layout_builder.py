#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import warnings

from enaml.nodevisitor import NodeVisitor

from enaml.qt.QtCore import Qt, QRect
from enaml.qt.QtWidgets import QApplication

from enaml.layout.dock_layout import ItemLayout, AreaLayout

from .event_types import QDockItemEvent, DockItemDocked
from .layout_handling import plug_frame
from .q_dock_bar import QDockBar
from .q_dock_splitter import QDockSplitter
from .q_dock_tab_widget import QDockTabWidget
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

    Returns
    -------
    result : QRect
        The potentially adjusted QRect which fits on the screen.

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


class LayoutBuilder(NodeVisitor):
    """ A NodeVisitor which builds and updates a dock manager layout.

    Instances of this class should be used once and discarded.

    """
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

    TAB_POSITION = {
        'top': QDockTabWidget.North,
        'bottom': QDockTabWidget.South,
        'left': QDockTabWidget.West,
        'right': QDockTabWidget.East,
    }

    ORIENTATION = {
        'horizontal': Qt.Horizontal,
        'vertical': Qt.Vertical,
    }

    def __init__(self, manager):
        """ Initialize a LayoutBuilder.

        Parameters
        ----------
        manager : DockManager
            The dock manager for which work is being performed.

        """
        self.manager = manager
        self._containers = None

    def setup(self, node):
        """ Setup the layout updater.

        """
        self.stack = []

    def teardown(self, node):
        """ Teardown the updater.

        """
        del self.stack

    def default_visit(self, node):
        """ The default visitor method.

        The default visitor emits a warning for unhandled layout nodes.

        """
        msg = "unhandled layout node '%s'" % type(node).__name__
        warnings.warn(msg)

    @property
    def containers(self):
        """ Get a dictionary of available dock containers.

        """
        containers = self._containers
        if containers is None:
            c_list = self.manager.dock_containers()
            containers = dict((c.objectName(), c) for c in c_list)
            self._containers = containers
        return containers

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def init_dock_area(self, area, layout):
        """ Initialize and populate a dock area.

        This initializer populates the dock area with it children and
        dock bars, and sets the maximized item if appropriate.

        Parameters
        ----------
        area : QDockArea
            The dock area which should be populated with children.

        layout : AreaLayout
            The area layout node which describes the children to
            build for the area.

        """
        containers = self.containers
        if layout.item is not None:
            self.visit(layout.item)
            area.setCentralWidget(self.stack.pop())
        for bar_layout in layout.dock_bars:
            position = self.BAR_POSITIONS[bar_layout.position]
            for item in bar_layout.items:
                container = containers.get(item.name)
                if container is not None:
                    area.addToDockBar(container, position)
        for item in layout.find_all(ItemLayout):
            if item.maximized:
                container = containers.get(item.name)
                if container is not None:
                    container.showMaximized()
                    break

    def init_floating_frame(self, frame, layout):
        """ Initialize a floating frame.

        This initializer sets up the geometry, maximized state, and
        linked state for the floating frame.

        Parameters
        ----------
        frame : QDockFrame
            The floating dock frame of interest.

        layout : ItemLayout or AreaLayout
            The layout describing the floating state of the frame.

        """
        rect = QRect(*layout.geometry)
        if rect.isValid():
            rect = ensure_on_screen(rect)
            frame.setGeometry(rect)
        frame.show()
        if layout.linked:
            frame.setLinked(True)
        if layout.maximized:
            frame.showMaximized()

    @contextmanager
    def dock_context(self, container):
        """ Setup a context for docking onto a QDockContainer target.

        This context manager will setup a QDockWindow for a floating
        dock container, which ensures that a new dock area will be
        available for docking.

        Parameters
        ----------
        container : QDockContainer
            The container dock target of the operation.

        """
        is_window = container.isWindow()
        if is_window:
            is_maxed = container.isMaximized()
            if is_maxed:
                container.showNormal()
            manager = self.manager
            window = QDockWindow(manager, manager.dock_area())
            manager.add_window(window)
            window.setGeometry(container.geometry())
            win_area = window.dockArea()
            plug_frame(win_area, None, container, QGuideRose.Guide.AreaCenter)
            self.post_docked_event(container)
        yield
        if is_window:
            window.show()
            if is_maxed:
                window.showMaximized()

    @contextmanager
    def drop_frame(self, frame):
        """ Setup a drop context for a QDockFrame.

        This context manager prepares a QDockFrame to be dropped onto
        a dock area or dock container. It ensures that a dock window is
        cleaned up after the docking operation and that the appropriate
        event is emitted on the object.

        Parameters
        ----------
        window : QDockFrame
            The dock frame of interest.

        """
        if isinstance(frame, QDockWindow):
            win_area = frame.dockArea()
            maxed = win_area.maximizedWidget()
            if maxed is not None:
                container = self.containers.get(maxed.objectName())
                if container is not None:
                    container.showNormal()
        yield
        if isinstance(frame, QDockWindow) and frame.dockArea() is None:
            frame.close()
        elif not frame.isWindow():  # QDockContainer was docked.
            self.post_docked_event(frame)

    def post_docked_event(self, container):
        """ Post the docked event for the given container.

        Parameters
        ----------
        container : QDockContainer
            The dock container which was undocked.

        """
        root_area = container.manager().dock_area()
        if root_area.dockEventsEnabled():
            event = QDockItemEvent(DockItemDocked, container.objectName())
            QApplication.postEvent(root_area, event)

    #--------------------------------------------------------------------------
    # LayoutNode Visitors
    #--------------------------------------------------------------------------
    def visit_ItemLayout(self, node):
        """ Visit an ItemLayout node.

        This visitor pushes the named container onto the stack. If the
        name is not valid, None is pushed instead.

        """
        self.stack.append(self.containers.get(node.name))

    def visit_TabLayout(self, node):
        """ Visit a TabLayout node.

        This visitor visits its children, pops them from the stack, and
        adds them to a tab widget. The completed tab widget is pushed
        onto the stack as the return value. If there are no children,
        None is pushed. If there is a single child, it is pushed.

        """
        children = []
        for item in node.items:
            self.visit(item)
            children.append(self.stack.pop())
        children = [_f for _f in children if _f]
        if len(children) == 0:
            self.stack.append(None)
            return
        if len(children) == 1:
            self.stack.append(children[0])
            return
        tab_widget = QDockTabWidget()
        tab_widget.setTabPosition(self.TAB_POSITION[node.tab_position])
        for child in children:
            child.hideTitleBar()
            tab_widget.addTab(child, child.icon(), child.title())
        tab_widget.setCurrentIndex(node.index)
        self.stack.append(tab_widget)

    def visit_SplitLayout(self, node):
        """ Visit a SplitLayout node.

        This visitor visits its children, pops them from the stack, and
        adds them to a split widget. The completed tab widget is pushed
        onto the stack as the return value. If there are no children,
        None is pushed. If there is a single child, it is pushed.

        """
        children = []
        for item in node.items:
            self.visit(item)
            children.append(self.stack.pop())
        children = [_f for _f in children if _f]
        if len(children) == 0:
            self.stack.append(None)
            return
        if len(children) == 1:
            self.stack.append(children[0])
            return
        splitter = QDockSplitter(self.ORIENTATION[node.orientation])
        for child in children:
            splitter.addWidget(child)
        if len(node.sizes) >= splitter.count():
            splitter.setSizes(node.sizes)
        self.stack.append(splitter)

    def visit_DockLayout(self, node):
        """ Visit a DockLayout node.

        This visitor assemble a new layout from scratch for the dock
        manager. It is only invoked from the 'apply_layout' method of
        the dock manager when a completely new layout is being applied.

        """
        # Reset everything before applying a completely new layout.
        manager = self.manager
        for container in manager.dock_containers():
            container.reset()
        for window in manager.dock_windows():
            window.close()
        dock_area = manager.dock_area()
        dock_area.clearDockBars()
        dock_area.setCentralWidget(None)

        has_primary = False
        for item in node.items:
            if isinstance(item, AreaLayout):
                if not item.floating and not has_primary:
                    self.init_dock_area(dock_area, item)
                    has_primary = True
                else:
                    frame = QDockWindow(manager, dock_area)
                    self.init_dock_area(frame.dockArea(), item)
                    manager.add_window(frame)
                    self.init_floating_frame(frame, item)
            else:
                frame = self.containers.get(item.name)
                if frame is not None:
                    frame.float()
                    self.init_floating_frame(frame, item)

    #--------------------------------------------------------------------------
    # DockLayoutOp Visitors
    #--------------------------------------------------------------------------
    def visit_InsertItem(self, op):
        """ Handle the InsertItem dock layout operation.

        This visitor inserts the dock item into the layout according to
        the data specified in the operation.

        """
        item = self.containers.get(op.item)
        if item is None:
            return
        target = self.containers.get(op.target)
        if target is None:
            self.visit_InsertBorderItem(op)  # duck type to InsertBorderItem
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

        with self.dock_context(target):
            area = target.parentDockArea()
            widget = target.parentDockTabWidget() or target
            plug_frame(area, widget, item, self.ITEM_GUIDES[op.position])

    def visit_InsertBorderItem(self, op):
        """ Handle the InsertBorderItem dock layout operation.

        This visitor inserts the dock item into the dock area border
        according to the data specified in the operation.

        """
        item = self.containers.get(op.item)
        if item is None:
            return

        if not item.isWindow():
            item.unplug()

        guide = self.BORDER_GUIDES[op.position]
        target = self.containers.get(op.target)
        if target is None:
            area = self.manager.dock_area()
            if area.centralWidget() is None:
                guide = QGuideRose.Guide.AreaCenter
            plug_frame(area, None, item, guide)
        else:
            with self.dock_context(target):
                area = target.parentDockArea()
                if area.centralWidget() is None:
                    guide = QGuideRose.Guide.AreaCenter
                plug_frame(area, None, item, guide)

    def visit_InsertDockBarItem(self, op):
        """ Handle the InsertDockBarItem dock layout operation.

        This visitor inserts the dock item into the dock area's dock
        bar according to the data specified in the operation.

        """
        item = self.containers.get(op.item)
        if item is None:
            return

        if item.isWindow():
            item.unfloat()
        else:
            item.unplug()
        item.showTitleBar()

        position = self.BAR_POSITIONS[op.position]
        target = self.containers.get(op.target)
        if target is None:
            area = self.manager.dock_area()
            area.addToDockBar(item, position, op.index)
        else:
            with self.dock_context(target):
                area = target.parentDockArea()
                area.addToDockBar(item, position, op.index)

    def visit_InsertTab(self, op):
        """ Handle the InsertTab dock layout operation.

        This visitor inserts the dock item as a tab in the layout
        according to the data specified in the operation.

        """
        item = self.containers.get(op.item)
        if item is None:
            return

        if not item.isWindow():
            item.unplug()

        target = self.containers.get(op.target)
        if target is None:
            area = self.manager.dock_area()
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

        with self.dock_context(target):
            area = target.parentDockArea()
            widget = target.parentDockTabWidget()
            if widget is None:
                widget = target
                guide = self.TAB_GUIDES[op.tab_position]
            else:
                guide = QGuideRose.Guide.CompassCenter
            plug_frame(area, widget, item, guide)

        tabs = target.parentDockTabWidget()
        if tabs is not None:
            index = tabs.indexOf(item)
            tabs.tabBar().moveTab(index, op.index)

    def visit_FloatItem(self, op):
        """ Handle the FloatItem dock layout op.

        This visitor converts the item into a floating dock item.

        """
        layout = op.item
        container = self.containers.get(layout.name)
        if container is None:
            return
        if not container.isWindow():
            container.unplug()
            container.float()
        self.init_floating_frame(container, layout)

    def visit_FloatArea(self, op):
        """ Handle the FloatArea dock layout op.

        This visitor creates a new floating dock area window.

        """
        # Reset the relevant containers before creating the new area.
        containers = self.containers
        for item in op.area.find_all(ItemLayout):
            container = containers.get(item.name)
            if container is not None:
                if not container.isWindow():
                    container.unplug()
                container.reset()
        manager = self.manager
        frame = QDockWindow(manager, manager.dock_area())
        self.init_dock_area(frame.dockArea(), op.area)
        manager.add_window(frame)
        self.init_floating_frame(frame, op.area)

    def visit_RemoveItem(self, op):
        """ Handle the RemoveItem dock layout op.

        This visitor removes the item from the layout and hides it.

        """
        container = self.containers.get(op.item)
        if container is None:
            return
        if container.isWindow():
            container.unfloat()
        else:
            container.unplug()
        container.hide()

    def visit_ExtendItem(self, op):
        """ Handle the ExtendItem dock layout op.

        This visitor will extend the item provided it lives in a
        dock bar.

        """
        container = self.containers.get(op.item)
        if container is None:
            return
        area = container.parentDockArea()
        if area is not None:
            area.extendFromDockBar(container)

    def visit_RetractItem(self, op):
        """ Handle the RetractItem dock layout op.

        This visitor will retract the item provided it lives in a
        dock bar.

        """
        container = self.containers.get(op.item)
        if container is None:
            return
        area = container.parentDockArea()
        if area is not None:
            area.retractToDockBar(container)
