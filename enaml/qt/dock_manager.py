#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QRect, QSize
from PyQt4.QtGui import QApplication, QSplitter, QTabWidget, QSplitterHandle

from atom.api import Atom, Bool, ForwardTyped, Typed, List

from .dock_overlay import DockOverlay
from .q_dock_area import QDockArea
from .q_dock_container import QDockContainer
from .q_dock_tabbar import QDockTabBar
from .q_guide_rose import QGuideRose


ORIENTATION = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


ORIENTATION_INV = dict((v, k) for k, v in ORIENTATION.items())


DOCUMENT_MODE = {
    'document': True,
    'preferences': False,
}


DOCUMENT_MODE_INV = dict((v, k) for k, v in DOCUMENT_MODE.items())


TAB_POSITION = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


TAB_POSITION_INV = dict((v, k) for k, v in TAB_POSITION.items())


class LayoutBuilder(Atom):
    """ A visitor class which builds the layout from a dict.

    The single public entry point is the 'build()' classmethod.

    """
    #: The set of seen names when building the layout.
    seen_names = Typed(set, ())

    @classmethod
    def build(cls, layout, area):
        """ Build the root layout widget for the layout description.

        Parameters
        ----------
        layout : dict
            The dictionary representation of the layout.

        area : QDockArea
            The dock area which owns the dock containers.

        Returns
        -------
        result : QWidget
            A QWidget which implements the dock area.

        """
        return cls().visit(layout, area)

    def visit(self, layout, area):
        """ The main visitor dispatch method.

        This method dispatches to the type-specific handlers.

        """
        name = 'visit_' + layout['type']
        return getattr(self, name)(layout, area)

    def visit_split(self, layout, area):
        """ The handler method for a split layout description.

        This handler will build and populate a QSplitter which holds
        the items declared in the layout.

        """
        children = (self.visit(child, area) for child in layout['children'])
        children = filter(None, children)
        if len(children) == 0:
            return None
        if len(children) == 1:
            return children[0]
        splitter = QSplitter(ORIENTATION[layout['orientation']])
        for child in children:
            splitter.addWidget(child)
            child.show()
        sizes = layout.get('sizes')
        if sizes is not None:
            splitter.setSizes(sizes)
        return splitter

    def visit_tabbed(self, layout, area):
        """ The handler method for a tabbed layout description.

        This handler will build and populate a QTabWidget which holds
        the items declared in the layout.

        """
        children = (self.visit(item, area) for item in layout['children'])
        children = filter(None, children)
        if len(children) == 0:
            return None
        if len(children) == 1:
            return children[0]
        tab_widget = QTabWidget()
        tab_widget.setTabBar(QDockTabBar())
        tab_widget.setDocumentMode(DOCUMENT_MODE[layout['tab_style']])
        tab_widget.setMovable(layout['tabs_movable'])
        tab_widget.setTabPosition(TAB_POSITION[layout['tab_position']])
        for child in children:
            dock_item = child.dockItem()
            dock_item.titleBarWidget().hide()
            tab_widget.addTab(child, dock_item.title())
            child.show()
        index = layout.get('index')
        if index is not None:
            tab_widget.setCurrentIndex(index)
        return tab_widget

    def visit_item(self, layout, area):
        """ The handler method for an item layout description.

        This handler will find and return the named dock container for
        the item, or None if the container is not found or the name is
        visited more than once.

        """
        name = layout['name']
        if name in self.seen_names:
            return None
        self.seen_names.add(name)
        container = area.findChild(QDockContainer, name)
        if container is not None:
            container.dockItem().titleBarWidget().show()
        return container


class LayoutSaver(Atom):
    """ A visitor class which saves the layout from a dict.

    The single public entry point is the 'save()' classmethod.

    """
    @classmethod
    def save(cls, area):
        """ Save the layout contained in the dock area.

        Parameters
        ----------
        area : QDockArea
            The dock area which owns the dock layout.

        Returns
        -------
        result : dict
            A dictionary which describes the layout.

        """
        widget = area.layout().layoutWidget()
        if widget is None:
            return {}
        return cls().visit(widget)

    def visit(self, widget):
        """ The main visitor dispatch method.

        This method dispatches to the type-specific handlers.

        """
        name = 'visit_' + type(widget).__name__
        return getattr(self, name)(widget)

    def visit_QTabWidget(self, widget):
        """ The handler method for a QTabWidget layout widget.

        """
        layout = {'type': 'tabbed'}
        layout['tabs_movable'] = widget.isMovable()
        layout['tab_style'] = DOCUMENT_MODE_INV[widget.documentMode()]
        layout['tab_position'] = TAB_POSITION_INV[widget.tabPosition()]
        children = []
        for index in xrange(widget.count()):
            children.append(self.visit(widget.widget(index)))
        layout['children'] = children
        layout['index'] = widget.currentIndex()
        return layout

    def visit_QSplitter(self, widget):
        """ The handler method for a QSplitter layout widget.

        """
        layout = {'type': 'split'}
        layout['sizes'] = widget.sizes()
        layout['orientation'] = ORIENTATION_INV[widget.orientation()]
        children = []
        for index in xrange(widget.count()):
            children.append(self.visit(widget.widget(index)))
        layout['children'] = children
        return layout

    def visit_QDockContainer(self, widget):
        """ The handler method for a QDockContainer layout widget.

        """
        return {'type': 'item', 'name': widget.objectName()}


class LayoutUnplugger(Atom):
    """ A visitor class which unplugs a container from a layout.

    The single public entry point is the 'unplug()' classmethod.

    """
    @classmethod
    def unplug(cls, area, container):
        """ Unplug a container from a layout.

        Parameters
        ----------
        area : QDockArea
            The dock area in which the container lives.

        container : QDockContainer
            The container to remove from the layout.

        Returns
        -------
        result : tuple
            A 2-tuple of (bool, QWidget or None) indicating whether the
            operation was successful and a potentially new widget to
            update as the new root of the layout.

        """
        layout = area.layout()
        root = layout.layoutWidget()
        if root is container:
            root.hide()
            root.setParent(None)
            layout.setLayoutWidget(None)
            return True
        success, replace = cls().visit(root, container)
        if not success:
            return False
        if replace is not None:
            layout.setLayoutWidget(replace)
        return True

    def visit(self, widget, container):
        """ The main visitor dispatch method.

        This method dispatches to the node-specific handlers.

        """
        name = 'visit_' + type(widget).__name__
        return getattr(self, name)(widget, container)

    def visit_QSplitter(self, widget, container):
        """ The visitor handler for a QSplitter node.

        This method will dispatch to the child handlers, and the clean
        up the splitter if there is only a single child remaining.

        """
        for index in xrange(widget.count()):
            success, replace = self.visit(widget.widget(index), container)
            if success:
                if replace is not None:
                    widget.insertWidget(index, replace)
                    replace.show()
                if widget.count() == 1:
                    replace = widget.widget(0)
                    replace.hide()
                    replace.setParent(None)
                    widget.hide()
                    widget.setParent(None)
                else:
                    replace = None
                return True, replace
        return False, None

    def visit_QTabWidget(self, widget, container):
        """ The visitor handler for a QTabWidget node.

        This method will dispatch to the child handlers, and the clean
        up the tab widget if there is only a single child remaining.

        """
        for index in xrange(widget.count()):
            success, replace = self.visit(widget.widget(index), container)
            if success:
                assert replace is None  # tabs never hold replaceable items
                if widget.count() == 1:
                    replace = widget.widget(0)
                    replace.hide()
                    replace.setParent(None)
                    replace.dockItem().titleBarWidget().show()
                    widget.hide()
                    widget.setParent(None)
                else:
                    replace = None
                return True, replace
        return False, None

    def visit_QDockContainer(self, widget, container):
        """ The visitor handler for a QDockContainer node.

        If the widget matches the container, this handler will hide and
        unparent the container.

        """
        if widget is container:
            container.hide()
            container.setParent(None)
            container.dockItem().titleBarWidget().show()
            return True, None
        return False, None


class LayoutPlugger(Atom):
    """ A class used to plug a container into a layout.

    This single public entry point in the 'plug()' classmethod.

    """
    #: The dock area into which the container is being plugged.
    area = Typed(QDockArea)

    @classmethod
    def plug(cls, area, widget, container, guide):
        """ Plug a container into the layout.

        Parameters
        ----------
        area : QDockArea
            The dock area which owns the layout into which the
            container is being plugged.

        widget : QWidget
            The widget under the mouse. This should be one of
            QSplitterHandle, QTabWidget, or QDockContainer.

        guide : QGuideRose.Guide
            The guide rose guide which indicates how to perform
            the plugging.

        Returns
        -------
        result : bool
            True if the plugging was successful, False otherwise.

        """
        self = cls(area=area)
        Guide = QGuideRose.Guide
        if guide == Guide.CompassCenter:
            res = self.plug_center_default(widget, container)
        elif guide == Guide.CompassExNorth:
            res = self.plug_center(widget, container, QTabWidget.North)
        elif guide == Guide.CompassExEast:
            res = self.plug_center(widget, container, QTabWidget.East)
        elif guide == Guide.CompassExSouth:
            res = self.plug_center(widget, container, QTabWidget.South)
        elif guide == Guide.CompassExWest:
            res = self.plug_center(widget, container, QTabWidget.West)
        elif guide == Guide.CompassNorth:
            res = self.plug_north(widget, container)
        elif guide == Guide.CompassEast:
            res = self.plug_east(widget, container)
        elif guide == Guide.CompassSouth:
            res = self.plug_south(widget, container)
        elif guide == Guide.CompassWest:
            res = self.plug_west(widget, container)
        elif guide == Guide.BorderNorth:
            res = self.plug_border_north(container)
        elif guide == Guide.BorderEast:
            res = self.plug_border_east(container)
        elif guide == Guide.BorderSouth:
            res = self.plug_border_south(container)
        elif guide == Guide.BorderWest:
            res = self.plug_border_west(container)
        elif guide == Guide.SplitHorizontal:
            res = self.plug_split(widget, container, guide)
        elif guide == Guide.SplitVertical:
            res = self.plug_split(widget, container, guide)
        else:
            res = False
        return res

    def prepare(self, container):
        """ Prepare a container to be plugged into the layout.

        """
        container.hide()
        container.setFloating(False)
        container.setWindowFlags(Qt.Widget)

    #--------------------------------------------------------------------------
    # Plug Handlers
    #--------------------------------------------------------------------------
    def plug_split(self, handle, container, guide):
        """ Plug the container onto a splitter handle.

        """
        Guide = QGuideRose.Guide
        if not isinstance(handle, QSplitterHandle):
            return False
        orientation = handle.orientation()
        if orientation == Qt.Horizontal:
            if guide != Guide.SplitHorizontal:
                return False
        elif guide != Guide.SplitVertical:
            return False
        splitter = handle.parent()
        for index in xrange(1, splitter.count()):
            if splitter.handle(index) is handle:
                self.prepare(container)
                splitter.insertWidget(index, container)
                container.show()
                return True
        return False

    def plug_center_default(self, widget, container):
        """ Create a tab widget using the default tab location.

        """
        # FIXME get the default position for new tabs from the dock area.
        if isinstance(widget, QTabWidget):
            return self.plug_center(widget, container, widget.tabPosition())
        return self.plug_center(widget, container, QTabWidget.North)

    def plug_center(self, widget, container, tab_pos):
        """ Create a tab widget from the widget and container.

        """
        if isinstance(widget, QTabWidget):
            if widget.tabPosition() != tab_pos:
                return False
            self.prepare(container)
            dock_item = container.dockItem()
            dock_item.titleBarWidget().hide()
            widget.addTab(container, dock_item.title())
            widget.setCurrentIndex(widget.count() - 1)
            container.show()
            return True
        if not isinstance(widget, QDockContainer):
            return False
        layout = self.area.layout()
        root = layout.layoutWidget()
        if widget is not root:
            if not isinstance(widget.parent(), QSplitter):
                return False
        tab_widget = QTabWidget()
        tab_widget.setTabBar(QDockTabBar())
        tab_widget.setTabPosition(tab_pos)
        tab_widget.setMovable(True)
        tab_widget.setDocumentMode(True)
        if widget is root:
            layout.setLayoutWidget(tab_widget)
        else:
            splitter = widget.parent()
            index = splitter.indexOf(widget)
            splitter.insertWidget(index, tab_widget)
        item = widget.dockItem()
        item.titleBarWidget().hide()
        tab_widget.addTab(widget, item.title())
        self.prepare(container)
        item = container.dockItem()
        item.titleBarWidget().hide()
        tab_widget.addTab(container, item.title())
        tab_widget.setCurrentIndex(1)
        container.show()
        return True

    def plug_north(self, widget, container):
        """ Plug the container to the north of the widget.

        """
        root = self.area.layout().layoutWidget()
        if widget is root:
            return self.split_root(Qt.Vertical, container, False)
        return self.split_widget(Qt.Vertical, widget, container, False)

    def plug_east(self, widget, container):
        """ Plug the container to the east of the widget.

        """
        root = self.area.layout().layoutWidget()
        if widget is root:
            return self.split_root(Qt.Horizontal, container, True)
        return self.split_widget(Qt.Horizontal, widget, container, True)

    def plug_south(self, widget, container):
        """ Plug the container to the south of the widget.

        """
        root = self.area.layout().layoutWidget()
        if widget is root:
            return self.split_root(Qt.Vertical, container, True)
        return self.split_widget(Qt.Vertical, widget, container, True)

    def plug_west(self, widget, container):
        """ Plug the container to the west of the widget.

        """
        root = self.area.layout().layoutWidget()
        if widget is root:
            return self.split_root(Qt.Horizontal, container, False)
        return self.split_widget(Qt.Horizontal, widget, container, False)

    def plug_border_north(self, container):
        """ Plug the container to the north border of the area.

        """
        return self.split_root(Qt.Vertical, container, False)

    def plug_border_east(self, container):
        """ Plug the container to the east border of the area.

        """
        return self.split_root(Qt.Horizontal, container, True)

    def plug_border_south(self, container):
        """ Plug the container to the south border of the area.

        """
        return self.split_root(Qt.Vertical, container, True)

    def plug_border_west(self, container):
        """ Plug the container to the west border of the area.

        """
        return self.split_root(Qt.Horizontal, container, False)

    def split_root(self, orientation, container, append):
        """ Split the root layout widget according the orientation.

        """
        layout = self.area.layout()
        root = layout.layoutWidget()
        is_splitter = isinstance(root, QSplitter)
        if not is_splitter or root.orientation() != orientation:
            new = QSplitter(orientation)
            layout.setLayoutWidget(new)
            new.addWidget(root)
            root.show()
            root = new
        self.prepare(container)
        if append:
            root.addWidget(container)
        else:
            root.insertWidget(0, container)
        container.show()
        return True

    def split_widget(self, orientation, widget, container, append):
        """ Split the widget according the orientation.

        """
        splitter = widget.parent()
        if not isinstance(splitter, QSplitter):
            return False
        index = splitter.indexOf(widget)
        if splitter.orientation() == orientation:
            if append:
                index += 1
            self.prepare(container)
            splitter.insertWidget(index, container)
            container.show()
            return True
        new = QSplitter(orientation)
        new.addWidget(widget)
        splitter.insertWidget(index, new)
        self.prepare(container)
        if append:
            new.addWidget(container)
        else:
            new.insertWidget(0, container)
        container.show()
        return True


class LayoutWalker(Atom):
    """ A class which walks a dock area layout and yields its widgets.

    """
    #: The dock area widget which owns the layout of interest.
    area = Typed(QDockArea)

    def __init__(self, area):
        """ Initialize a LayoutWalker.

        Parameters
        ----------
        area : QDockArea
            The dock area which owns the layout of interest.

        """
        assert area is not None
        self.area = area

    def splitter_handles(self):
        """ Get the splitter handles in the layout.

        Returns
        -------
        result : generator
            A generator which yields the QSplitterHandle instances
            contained within the layout.

        """
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QSplitter):
                for index in xrange(1, widget.count()):
                    yield widget.handle(index)
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))

    def tab_widgets(self):
        """ Get the tab widgets in the layout.

        Returns
        -------
        result : generator
            A generator which yields the QTabWidget instances contained
            within the layout.

        """
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QTabWidget):
                yield widget
            elif isinstance(widget, QSplitter):
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))

    def dock_containers(self):
        """ Get the dock containers in the layout.

        Returns
        -------
        result : generator
            A generator which yields the QDockContainer instances
            contained within the layout.

        """
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QDockContainer):
                yield widget
            elif isinstance(widget, (QSplitter, QTabWidget)):
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))


class DockHandler(Atom):
    """ A base class for defining handler objects for the dock manager.

    """
    #: The dock manager which owns the handler.
    manager = ForwardTyped(lambda: DockManager)

    def global_geometry(self):
        """ Get the global geometry of the handler widget.

        Returns
        -------
        result : QRect
            The global geometry rect of the handler widget.

        """
        raise NotImplementedError

    def show_overlay(self, pos):
        """ Show the dock overlay for the handler.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse. It is assumed that this
            lies within the bounds of the handler's primary widget.

        """
        raise NotImplementedError

    def plug(self, container, pos, guide):
        """ Plug the container into the layout.

        Parameters
        ----------
        container : QDockContainer
            The dock container to plug into the layout.

        pos : QPoint
            The global position of the of dock target.

        guide : QGuideRose.Guide
            The guide which defines how to plug the container.

        Returns
        -------
        result : bool
            True if the item was plugged successfully, False otherwise.

        """
        raise NotImplementedError


class DockContainerHandler(DockHandler):
    """ A dock handler which manages a QDockContainer.

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

    #: The dock container which owns the dock item.
    dock_container = Typed(QDockContainer)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
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
        return LayoutUnplugger.unplug(dock_area, container)

    def _dock_targets(self):
        """ Get the potential dock targets for the handler.

        Returns
        -------
        result : generator
            A generator which yields the dock handlers objects which
            are potential dock targets. They are yielded in Z-order
            with the top-most target first.

        """
        manager = self.manager
        for handler in reversed(manager.toplevel):
            if handler is not self:
                yield handler
        yield manager.primary

    def _dock_drag(self, pos):
        """ Handle a floating dock container drag.

        This handler will show the dock overlay at the proper location,
        or hide it if it should not be shown.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse.

        """
        for handler in self._dock_targets():
            if handler.global_geometry().contains(pos):
                handler.show_overlay(pos)
                return
        else:
            self.manager.overlay.hide()

    def _end_dock_drag(self, pos):
        """ End the dock drag operation for the handler.

        This method will hide the dock overlays for the manager and
        redock the container if it lies over a docking guide.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse.

        """
        overlay = self.manager.overlay
        overlay.hide()
        guide = overlay.guide_at(pos)
        if guide != QGuideRose.Guide.NoGuide:
            for handler in self._dock_targets():
                if handler.global_geometry().contains(pos):
                    if handler.plug(self.dock_container, pos, guide):
                        self.manager.toplevel.remove(self)
                        self.floating = False
                    return

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
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
        self.dragging = True
        self.floating = True
        self.manager.toplevel.append(self)
        container = self.dock_container
        container.setFloating(True)
        dock_item = container.dockItem()
        title = dock_item.titleBarWidget()
        margins = container.contentsMargins()
        x = title.width() / 2 + margins.left()
        y = title.height() / 2 + margins.top()
        self.press_pos = QPoint(x, y)
        flags = Qt.Tool | Qt.FramelessWindowHint
        container.setParent(self.manager.primary.area, flags)
        container.move(pos - self.press_pos)
        container.show()
        dock_item.grabMouse()
        return True

    #--------------------------------------------------------------------------
    # DockHandler Interface
    #--------------------------------------------------------------------------
    def global_geometry(self):
        """ Get the global geometry of the handler widget.

        Returns
        -------
        result : QRect
            The global geometry rect of the handler widget.

        """
        geo = self.dock_container.geometry()
        if self.floating:
            return geo
        pt = self.dock_container.mapToGlobal(QPoint(0, 0))
        return QRect(pt, geo.size())

    def show_overlay(self, pos):
        """ Show the dock overlay for this handler.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse. It is assumed that this
            lies within the bounds of the handler's primary widget.

        """
        container = self.dock_container
        pos = container.mapFromGlobal(pos)
        self.manager.overlay.mouse_over_widget(container, pos)

    def plug(self, container, pos, guide):
        """ Plug the container into the layout.

        Parameters
        ----------
        container : QDockContainer
            The dock container to plug into the layout.

        pos : QPoint
            The global position of the of dock target.

        guide : QGuideRose.Guide
            The guide which defines how to plug the container.

        Returns
        -------
        result : bool
            True if the item was plugged successfully, False otherwise.

        """
        return False

    #--------------------------------------------------------------------------
    # QDockContainer Handler Methods
    #--------------------------------------------------------------------------
    def window_activated(self):
        """ Handle the window activated event for the dock container.

        This handler is invoked by the container when it receives a
        WindowActivate event while floating. It is used to maintain
        knowledge of the Z-order of floating windows.

        """
        toplevel = self.manager.toplevel
        toplevel.remove(self)
        toplevel.append(self)

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

        self.floating = True
        self.manager.toplevel.append(self)
        container.setFloating(True)
        self.press_pos += QPoint(0, container.contentsMargins().top())
        flags = Qt.Tool | Qt.FramelessWindowHint
        container.setParent(self.manager.primary.area, flags)
        container.move(global_pos - self.press_pos)
        container.show()
        dock_item.grabMouse()
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
                self.dock_container.dockItem().releaseMouse()
                if self.floating:
                    self._end_dock_drag(event.globalPos())
                self.dragging = False
                self.press_pos = None
                return True
        return False


class DockAreaHandler(DockHandler):
    """ A dock handler which manages a QDockArea.

    """
    area = Typed(QDockArea)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _hit_test(self, pos):
        """ Hit test a dock area for a relevant dock target.

        Parameters
        ----------
        pos : QPoint
            The point of interest expressed in local area coordinates.

        Returns
        -------
        result : QWidget or None
            The relevant dock target under the position. This will be
            a QDockContainer, QTabWidget, or QSplitterHandle.

        """
        # Splitter handles have priority. Their active area is smaller
        # and overlaps that of other widgets. Giving dock containers
        # priority would make it difficult to hit a splitter reliably.
        # In certain configurations, there may be more than one handle
        # in the hit box, in which case the one closest to center wins.
        hits = []
        area = self.area
        walker = LayoutWalker(area)
        for handle in walker.splitter_handles():
            pt = handle.mapFrom(area, pos)
            rect = handle.rect().adjusted(-20, -20, 20, 20)
            if rect.contains(pt):
                dist = (rect.center() - pt).manhattanLength()
                hits.append((dist, handle))
        if len(hits) > 0:
            hits.sort()
            return hits[0][1]

        # Check for tab widgets next. A tab widget has dock containers,
        # but should have priority over the dock containers themselves.
        for tab_widget in walker.tab_widgets():
            pt = tab_widget.mapFrom(area, pos)
            if tab_widget.rect().contains(pt):
                return tab_widget

        # Check for QDockContainers last. The are the most common case,
        # but also have the least precedence compared to the others.
        for dock_container in walker.dock_containers():
            pt = dock_container.mapFrom(area, pos)
            if dock_container.rect().contains(pt):
                if not dock_container.isHidden():  # hidden tabs
                    return dock_container

    #--------------------------------------------------------------------------
    # DockHandler Interface
    #--------------------------------------------------------------------------
    def global_geometry(self):
        """ Get the global geometry of the handler widget.

        Returns
        -------
        result : QRect
            The global geometry rect of the handler widget.

        """
        area = self.area
        pt = area.mapToGlobal(QPoint(0, 0))
        return QRect(pt, area.size())

    def show_overlay(self, pos):
        """ Show the dock overlay for the handler.

        Parameters
        ----------
        pos : QPoint
            The global position of the mouse. It is assumed that this
            lies within the bounds of the handler's primary widget.

        """
        area = self.area
        manager = self.manager
        pos = area.mapFromGlobal(pos)
        if not area.rect().contains(pos):
            manager.overlay.hide()
        elif area.layout().layoutWidget() is None:
            manager.overlay.mouse_over_widget(area, pos, empty=True)
        else:
            widget = self._hit_test(pos)
            if widget is not None:
                manager.overlay.mouse_over_area(area, widget, pos)

    def plug(self, container, pos, guide):
        """ Plug the container into the layout.

        Parameters
        ----------
        container : QDockContainer
            The dock container to plug into the layout.

        pos : QPoint
            The global position of the of dock target.

        guide : QGuideRose.Guide
            The guide which defines how to plug the container.

        Returns
        -------
        result : bool
            True if the item was plugged successfully, False otherwise.

        """
        area = self.area
        widget = self._hit_test(area.mapFromGlobal(pos))
        if widget is None:
            if guide == QGuideRose.Guide.AreaCenter:
                layout = area.layout()
                if layout.layoutWidget() is None:
                    container.hide()
                    container.setFloating(False)
                    container.setWindowFlags(Qt.Widget)
                    layout.setLayoutWidget(container)
                    container.show()
                    return True
            return False
        return LayoutPlugger.plug(area, widget, container, guide)


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    """
    #: The handler which holds the primary dock area.
    primary = Typed(DockAreaHandler)

    #: The list of container handlers maintained by the manager.
    containers = List()

    #: The list of handlers which contain top-level windows. This list
    #: is maintained in proper Z-order with the top-most handler last.
    toplevel = List()

    #: The set of dock items added to the manager.
    dock_items = Typed(set, ())

    #: The overlay used when hovering over a dock area.
    overlay = Typed(DockOverlay, ())

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
        self.primary = DockAreaHandler(manager=self, area=dock_area)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_item(self, item):
        """ Add a dock item to the dock manager.

        If the item has already been added, this is a no-op.

        Parameters
        ----------
        items : QDockItem
            The item to be managed by this dock manager. It will be
            reparented to a dock container and made available to the
            the layout.

        """
        if item in self.dock_items:
            return
        self.dock_items.add(item)
        container = QDockContainer()
        container.setObjectName(item.objectName())
        container.setDockItem(item)
        container.setParent(self.primary.area)
        handler = DockContainerHandler(manager=self, dock_container=container)
        item.handler = handler
        container.handler = handler
        self.containers.append(handler)

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        """
        area = self.primary.area
        primary = LayoutBuilder.build(layout['primary'], area)
        area.layout().setLayoutWidget(primary)

        # FIXME not too happy with this; it doesn't handle floating areas
        # for f in floated:
        #     handler = f.handler
        #     handler.floating = True
        #     self.toplevel.append(handler)
        #     container = handler.dock_container
        #     container.setFloating(True)
        #     flags = Qt.Tool | Qt.FramelessWindowHint
        #     container.setParent(self.primary.area, flags)
        #     container.show()

    def save_layout(self):
        """ Get the dictionary representation of the dock layout.

        """
        layout = {'type': 'docklayout'}
        layout['primary'] = LayoutSaver.save(self.primary.area)
        layout['secondary'] = []
        return layout
