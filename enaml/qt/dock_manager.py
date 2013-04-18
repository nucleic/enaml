#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QRect, QSize
from PyQt4.QtGui import QApplication, QSplitter, QTabWidget

from atom.api import Atom, Bool, ForwardTyped, Typed, List

from .dock_overlay import DockOverlay
from .q_dock_area import QDockArea
from .q_dock_container import QDockContainer
from .q_dock_tabbar import QDockTabBar


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
            A widget which implements the semantics of the layout.

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
            # FIXME i don't really like this
            child.show()
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
            # FIXME i don't really like this
            child.show()
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
        return area.findChild(QDockContainer, name)


class LayoutUnplugger(Atom):
    """ A visitor class which unplugs a container from a layout.

    The single public entry point is the 'unplug()' classmethod.

    """
    @classmethod
    def unplug(cls, root, container):
        """ Unplug a container from a layout.

        Parameters
        ----------
        root : QWidget
            The root layout widget.

        container : QDockContainer
            The container to remove from the layout.

        Returns
        -------
        result : tuple
            A 2-tuple of (bool, QWidget or None) indicating whether the
            operation was successful and a potentially new widget to
            update as the new root of the layout.

        """
        return cls().visit(root, container)

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
                assert replace is None # tabs never hold replaceable items
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


class LayoutWalker(Atom):

    area = Typed(QDockArea)

    def __init__(self, area):
        assert area is not None
        self.area = area

    def splitter_handles(self):
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QSplitter):
                for index in xrange(1, widget.count()):
                    yield widget.handle(index)
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))

    def tab_widgets(self):
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QTabWidget):
                yield widget
            elif isinstance(widget, QSplitter):
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))

    def dock_containers(self):
        stack = [self.area.layout().layoutWidget()]
        while stack:
            widget = stack.pop()
            if isinstance(widget, QDockContainer):
                yield widget
            elif isinstance(widget, (QSplitter, QTabWidget)):
                for index in xrange(widget.count()):
                    stack.append(widget.widget(index))


class DockContainerHandler(Atom):
    """ A framework class for handling a QDockContainer.

    """
    class DockContainerState(Atom):
        """ A framework class for storing a QDockContainer dock state.

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

    #: The state for the dock container associated with this handler.
    state = Typed(DockContainerState, ())

    #: The dock container which owns the dock item.
    dock_container = Typed(QDockContainer)

    #: The dock manager state object which is shared between handlers.
    manager = ForwardTyped(lambda: DockManager)

    @staticmethod
    def unplug(container):
        """ A staticmethod which unplugs a container from its dock area.

        This method assumes the provided container is in a state which
        is suitable for unplugging. If the operation is successful, the
        container will be hidden and its parent will be None.

        Parameters
        ----------
        container : QDockContainer
            The container to unplug from its dock area.

        Returns
        -------
        result : bool
            True if unplugging was a success, False otherwise.

        """
        dock_area = None
        parent = container.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                dock_area = parent
                break
            parent = parent.parent()
        if dock_area is None:
            return False

        # FIXME special cased root removal
        layout = dock_area.layout()
        root = layout.layoutWidget()
        if root is container:
            root.hide()
            root.setParent(None)
            layout.setLayoutWidget(None)
            return True

        success, replace = LayoutUnplugger.unplug(root, container)
        if not success:
            return False
        if replace is not None:
            layout.setLayoutWidget(replace)
        return True

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
            state = self.state
            if state.press_pos is None:
                container = self.dock_container
                dock_item = container.dockItem()
                title_bar = dock_item.titleBarWidget()
                if not title_bar.isHidden():
                    if title_bar.geometry().contains(event.pos()):
                        pos = dock_item.mapTo(container, event.pos())
                        state.press_pos = pos
                        return True
        return False

    def mouse_move_event(self, event):
        """ Handle a mouse move event for the dock item.

        This handler manages docking and undocking the item.

        """
        # Protect against being called with bad state. This can happen
        # when clicking and dragging a child of the item which doesn't
        # handle the move event.
        state = self.state
        if state.press_pos is None:
            return False

        # If the title bar is dragged while the container is floating,
        # the container is moved to the proper location.
        container = self.dock_container
        if state.dragging:
            if state.floating:
                container.move(event.globalPos() - state.press_pos)
                self.manager.dock_drag(self, event.globalPos())
            return True

        dock_item = container.dockItem()
        pos = dock_item.mapTo(container, event.pos())
        dist = (pos - state.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return False

        # If the container is already floating, there is nothing to do.
        # The call to this event handler will move the container.
        state.dragging = True
        if state.floating:
            return True

        if not self.unplug(container):
            return False

        state.floating = True
        container.setFloating(True)
        state.press_pos += QPoint(0, container.contentsMargins().top())
        flags = Qt.Tool | Qt.FramelessWindowHint
        container.setParent(self.manager.primary_area, flags)
        container.move(event.globalPos() - state.press_pos)
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
            state = self.state
            if state.press_pos is not None:
                self.dock_container.dockItem().releaseMouse()
                if state.floating:
                    self.manager.dock_end_drag(self)
                state.dragging = False
                state.press_pos = None
                return True
        return False


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    """
    #: The primary dock area being managed by the manager.
    primary_area = Typed(QDockArea)

    #: The list of dock container handlers for the manager.
    handlers = List()

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
        self.primary_area = dock_area

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def release_items(self):
        pass

    def add_item(self, item):
        if item in self.dock_items:
            return
        self.dock_items.add(item)
        container = QDockContainer()
        # FIXME i don't really like this
        container.hide()
        container.setObjectName(item.objectName())
        container.setDockItem(item)
        container.setParent(self.primary_area)
        handler = DockContainerHandler()
        handler.dock_container = container
        handler.manager = self
        item.handler = handler
        self.handlers.append(handler)

    def remove_item(self, item):
        pass

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        """
        area = self.primary_area
        layout_widget = LayoutBuilder.build(layout, area)
        area.layout().setLayoutWidget(layout_widget)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def hit_test(self, area, pos):
        walker = LayoutWalker(area)

        # Splitter handles have priority. Their active area is smaller
        # and overlaps that of other widgets. Giving dock containers
        # priority would make it difficult to hit a splitter reliably.
        # In certain configurations, there may be more than one handle
        # in the hit box, in which case the one closest to center wins.
        hits = []
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
                if not dock_container.isHidden():
                    return dock_container


    def _hdrag(self, handler, pos):
        self.overlay.mouse_over_widget(handler.dock_container, pos)

    def dock_drag(self, handler, pos):
        for ohandler in self.handlers:
            if ohandler is handler:
                continue
            if ohandler.state.floating:
                if ohandler.dock_container.geometry().contains(pos):
                    pos = ohandler.dock_container.mapFromGlobal(pos)
                    self._hdrag(ohandler, pos)
                    return

        area = self.primary_area
        pos = area.mapFromGlobal(pos)
        if not area.rect().contains(pos):
            self.overlay.hide()
        elif area.layout().layoutWidget() is None:
            self.overlay.mouse_over_widget(area, pos, empty=True)
        else:
            widget = self.hit_test(area, pos)
            if widget is not None:
                self.overlay.mouse_over(area, widget, pos)

    def dock_end_drag(self, handler):
        self.overlay.hide()

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


    #     self._hit_tester = None
    #     self._plug_handlers = [
    #         '_plug_border_north',
    #         '_plug_border_east',
    #         '_plug_border_south',
    #         '_plug_border_west',
    #         '_plug_compass_north',
    #         '_plug_compass_east',
    #         '_plug_compass_south',
    #         '_plug_compass_west',
    #         '_plug_compass_center',
    #         None,                       # CompassCross
    #         '_plug_split_vertical',
    #         '_plug_split_horizontal',
    #         '_plug_single_center',
    #         None,                       # NoGuide
    #     ]

    # #--------------------------------------------------------------------------
    # # Plug Handlers
    # #--------------------------------------------------------------------------
    # # FIXME these plug handlers can use some refactoring
    # def _prep_item_plug(self, item, title_vis):
    #     self._items.add(item)
    #     item.hide()
    #     item.setWindowFlags(Qt.Widget)
    #     item.titleBarWidget().setVisible(title_vis)

    # def _plug_border_north(self, item, pos):
    #     root = self._root
    #     if root is None:
    #         return False
    #     self._prep_item_plug(item, True)
    #     if isinstance(root, QSplitter) and root.orientation() == Qt.Vertical:
    #         root.insertWidget(0, item)
    #     else:
    #         sp = self._createSplitter(Qt.Vertical)
    #         sp.addWidget(item)
    #         sp.addWidget(self._root)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     item.show()
    #     return True

    # def _plug_border_east(self, item, pos):
    #     root = self._root
    #     if root is None:
    #         return False
    #     self._prep_item_plug(item, True)
    #     if isinstance(root, QSplitter) and root.orientation() == Qt.Horizontal:
    #         root.addWidget(item)
    #     else:
    #         sp = self._createSplitter(Qt.Horizontal)
    #         sp.addWidget(self._root)
    #         sp.addWidget(item)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     item.show()
    #     return True

    # def _plug_border_south(self, item, pos):
    #     root = self._root
    #     if root is None:
    #         return False
    #     self._prep_item_plug(item, True)
    #     if isinstance(root, QSplitter) and root.orientation() == Qt.Vertical:
    #         root.addWidget(item)
    #     else:
    #         sp = self._createSplitter(Qt.Vertical)
    #         sp.addWidget(self._root)
    #         sp.addWidget(item)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     item.show()
    #     return True

    # def _plug_border_west(self, item, pos):
    #     root = self._root
    #     if root is None:
    #         return False
    #     self._prep_item_plug(item, True)
    #     if isinstance(root, QSplitter) and root.orientation() == Qt.Horizontal:
    #         root.insertWidget(0, item)
    #     else:
    #         sp = self._createSplitter(Qt.Horizontal)
    #         sp.addWidget(item)
    #         sp.addWidget(self._root)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     item.show()
    #     return True

    # def _plug_compass_north(self, item, pos):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, (QTabWidget, QDockItem)):
    #         return False
    #     if hovered is self._root:
    #         self._prep_item_plug(item, True)
    #         sp = self._createSplitter(Qt.Vertical)
    #         sp.addWidget(item)
    #         sp.addWidget(self._root)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     else:
    #         # hovered parent should logically be a splitter, but the
    #         # assumption may break down during very heavy docking.
    #         parent = hovered.parent()
    #         if not isinstance(parent, QSplitter):
    #             return False
    #         self._prep_item_plug(item, True)
    #         index = parent.indexOf(hovered)
    #         if parent.orientation() == Qt.Vertical:
    #             parent.insertWidget(index, item)
    #         else:
    #             sp = self._createSplitter(Qt.Vertical)
    #             sp.addWidget(item)
    #             sp.addWidget(hovered)
    #             parent.insertWidget(index, sp)
    #             sp.show()
    #     item.show()
    #     return True

    # def _plug_compass_east(self, item, pos):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, (QTabWidget, QDockItem)):
    #         return False
    #     if hovered is self._root:
    #         self._prep_item_plug(item, True)
    #         sp = self._createSplitter(Qt.Horizontal)
    #         sp.addWidget(self._root)
    #         sp.addWidget(item)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     else:
    #         # hovered parent should logically be a splitter, but the
    #         # assumption may break down during very heavy docking.
    #         parent = hovered.parent()
    #         if not isinstance(parent, QSplitter):
    #             return False
    #         self._prep_item_plug(item, True)
    #         index = parent.indexOf(hovered)
    #         if parent.orientation() == Qt.Horizontal:
    #             parent.insertWidget(index + 1, item)
    #         else:
    #             sp = self._createSplitter(Qt.Horizontal)
    #             sp.addWidget(hovered)
    #             sp.addWidget(item)
    #             parent.insertWidget(index, sp)
    #             sp.show()
    #     item.show()
    #     return True

    # def _plug_compass_south(self, item, pos):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, (QTabWidget, QDockItem)):
    #         return False
    #     if hovered is self._root:
    #         self._prep_item_plug(item, True)
    #         sp = self._createSplitter(Qt.Vertical)
    #         sp.addWidget(self._root)
    #         sp.addWidget(item)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     else:
    #         # hovered parent should logically be a splitter, but the
    #         # assumption may break down during very heavy docking.
    #         parent = hovered.parent()
    #         if not isinstance(parent, QSplitter):
    #             return False
    #         self._prep_item_plug(item, True)
    #         index = parent.indexOf(hovered)
    #         if parent.orientation() == Qt.Vertical:
    #             parent.insertWidget(index + 1, item)
    #         else:
    #             sp = self._createSplitter(Qt.Vertical)
    #             sp.addWidget(hovered)
    #             sp.addWidget(item)
    #             parent.insertWidget(index, sp)
    #             sp.show()
    #     item.show()
    #     return True

    # def _plug_compass_west(self, item, pos):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, (QTabWidget, QDockItem)):
    #         return False
    #     if hovered is self._root:
    #         self._prep_item_plug(item, True)
    #         sp = self._createSplitter(Qt.Horizontal)
    #         sp.addWidget(item)
    #         sp.addWidget(self._root)
    #         self._root = sp
    #         sp.setParent(self.parentWidget())
    #         sp.show()
    #     else:
    #         # hovered parent should logically be a splitter, but the
    #         # assumption may break down during very heavy docking.
    #         parent = hovered.parent()
    #         if not isinstance(parent, QSplitter):
    #             return False
    #         self._prep_item_plug(item, True)
    #         index = parent.indexOf(hovered)
    #         if parent.orientation() == Qt.Horizontal:
    #             parent.insertWidget(index, item)
    #         else:
    #             sp = self._createSplitter(Qt.Horizontal)
    #             sp.addWidget(item)
    #             sp.addWidget(hovered)
    #             parent.insertWidget(index, sp)
    #             sp.show()
    #     item.show()
    #     return True

    # def _plug_compass_center(self, item, pos):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, (QTabWidget, QDockItem)):
    #         return False
    #     self._prep_item_plug(item, False)
    #     if isinstance(hovered, QTabWidget):
    #         hovered.addTab(item, item.title())
    #         hovered.setCurrentIndex(hovered.count() - 1)
    #     else:
    #         if hovered is not self._root:
    #             parent = hovered.parent()
    #             index = parent.indexOf(hovered)
    #         hovered.titleBarWidget().setVisible(False)
    #         tw = self._createTabWidget(True, True, QTabWidget.North)
    #         tw.addTab(hovered, hovered.title())
    #         tw.addTab(item, item.title())
    #         tw.setCurrentIndex(tw.count() - 1)
    #         if hovered is self._root:
    #             self._root = tw
    #             tw.setParent(self.parentWidget())
    #         else:
    #             parent.insertWidget(index, tw)
    #         tw.show()
    #     item.show()
    #     return True

    # def _plug_splitter(self, item, pos, orient):
    #     hovered = self.hitTest(pos)
    #     if not isinstance(hovered, QSplitterHandle):
    #         return False
    #     if hovered.orientation() != orient:
    #         return False
    #     self._prep_item_plug(item, True)
    #     splitter = hovered.parent()
    #     for index in xrange(1, splitter.count()):
    #         if splitter.handle(index) is hovered:
    #             splitter.insertWidget(index, item)
    #             break
    #     item.show()
    #     return True

    # def _plug_split_vertical(self, item, pos):
    #     return self._plug_splitter(item, pos, Qt.Vertical)

    # def _plug_split_horizontal(self, item, pos):
    #     return self._plug_splitter(item, pos, Qt.Horizontal)

    # def _plug_single_center(self, item, pos):
    #     if self._root is not None:
    #         return False
    #     self._root = item
    #     self._prep_item_plug(item, True)
    #     item.setParent(self.parentWidget())
    #     item.show()
    #     return True

    # def plug(self, item, pos, guide):
    #     """ Plug a dock item into the layout.

    #     Parameters
    #     ----------
    #     item : QDockItem
    #         The dock item which is being plugged.

    #     pos : QPoint
    #         The position at which to plug the item.

    #     mode : QGuideRose.Guide
    #         The guide which determines how the item should be plugged.

    #     Returns
    #     -------
    #     result : bool
    #         True if the item was successfully plugged, False otherwise.

    #     """
    #     if item in self._items:
    #         return False
    #     handler_name = self._plug_handlers[guide]
    #     if handler_name is None:
    #         return False
    #     handler = getattr(self, handler_name, None)
    #     if handler is None:
    #         return False
    #     return handler(item, pos)

    # def unplug(self, container):
    #     """ Unplug a dock container from the layout.

    #     Parameters
    #     ----------
    #     container : QDockContainer
    #         The dock container to unplug from the layout.

    #     """
    #     root = self._root
    #     if root is None:
    #         return
    #     if container is root:
    #         container.hide()
    #         container.setParent(None)
    #         self._root = None
    #         self._hit_tester = None
    #         return
    #     success, replace = LayoutUnplugger.unplug(root, container)
    #     if success:
    #         self._hit_tester = None
    #         if replace is not None:
    #             self._root = replace
    #             replace.setParent(self.parentWidget())
    #             replace.show()

    # def hitTest(self, pos):
    #     """ Hit test the layout for a relevant widget under a point.

    #     Parameters
    #     ----------
    #     pos : QPoint
    #         The point of interest, expressed in the local coordinate
    #         system of the layout parent widget.

    #     Returns
    #     -------
    #     result : QWidget or None
    #         A widget which is relevant for docking purposes, or None
    #         if no such widget was found under the point. If the hit
    #         test is successful, the result will be a QDockContainer,
    #         QSplitterHandler, or QTabWidget.

    #     """
    #     tester = self._hit_tester
    #     if tester is None:
    #         root = self._root
    #         if root is None:
    #             return
    #         tester = self._hit_tester = LayoutHitTester.from_widget(root)
    #     return tester.hit_test(self.parentWidget(), pos)
