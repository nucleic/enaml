#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import (
    QLayout, QSplitter, QSplitterHandle, QStackedWidget, QTabWidget
)

from enaml.widgets.dock_layout import DockLayoutItem, SplitLayout, TabbedLayout

from .q_dock_container import QDockContainer
from .q_dock_item import QDockItem
from .q_dock_tabbar import QDockTabBar


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


TAB_POSITIONS_INV = dict((v, k) for k, v in TAB_POSITIONS.items())


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


DOCUMENT_MODES_INV = dict((v, k) for k, v in DOCUMENT_MODES.items())


ORIENTATION = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


ORIENTATION_INV = dict((v, k) for k, v in ORIENTATION.items())


class QDockAreaLayout(QLayout):
    """ A custom QLayout which is part of the dock area implementation.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the layout.

        """
        super(QDockAreaLayout, self).__init__(parent)
        self._root = None
        self._splitters = set()
        self._containers = set()
        self._tab_widgets = set()
        self._plug_handlers = [
            '_plug_border_north',
            '_plug_border_east',
            '_plug_border_south',
            '_plug_border_west',
            '_plug_compass_north',
            '_plug_compass_east',
            '_plug_compass_south',
            '_plug_compass_west',
            '_plug_compass_center',
            None,                       # CompassCross
            '_plug_split_vertical',
            '_plug_split_horizontal',
            '_plug_single_center',
            None,                       # NoGuide
        ]

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _createContainer(self, item):
        """ Wrap a dock item in a dock container.

        """
        container = QDockContainer()
        container.setDockWidget(item)
        self._containers.add(container)
        return container

    def _createSplitter(self, orientation):
        """ Create a QSplitter for the given orientation.

        This method will add the splitter to the tracked set.

        """
        splitter = QSplitter(orientation)
        self._splitters.add(splitter)
        return splitter

    def _createTabWidget(self, doc_mode=None, movable=None, tab_pos=None):
        """ Create a tab widget for the layout.

        This method will add the tab widget to the tracked set.

        """
        tab_widget = QTabWidget()
        tab_widget.setTabBar(QDockTabBar())
        tab_widget.setDocumentMode(doc_mode)
        tab_widget.setMovable(movable)
        tab_widget.setTabPosition(tab_pos)
        self._tab_widgets.add(tab_widget)
        return tab_widget

    def _buildLayoutHelper(self, layout):
        """ Create the layout widget for the given layout item.

        This an internal method used by the layout to generate the
        widget layout hierarchy from a DockLayout configuration.

        Parameters
        ----------
        layout_item : DockLayout
            A dock layout description to convert into a widget.

        Returns
        -------
        results : QWidget or None
            A QWidget for the layout item, or None if one could not
            be created.

        """
        area = self.parentWidget()
        if isinstance(layout, DockLayoutItem):
            child = area.findChild(QDockItem, layout.name)
            if child is not None and child.parent() not in self._containers:
                return self._createContainer(child)
        elif isinstance(layout, (SplitLayout, TabbedLayout)):
            return self._buildLayout(layout)

    def _buildLayout(self, layout):
        """ Build the layout widget hierarchy for a configuration.

        This an internal method used by the layout to generate the
        widget layout hierarchy from a DockLayout configuration.

        Parameters
        ----------
        layout : DockLayout
            The dock layout object to convert into a QWidget for
            use by the area layout.

        Returns
        -------
        result : QWidget or None
            A QWidget object which implements the layout semantics,
            or None if the configuration resulted in an empty layout.

        """
        if isinstance(layout, (SplitLayout, TabbedLayout)):
            helper = self._buildLayoutHelper
            children = filter(None, (helper(item) for item in layout.items))
            n = len(children)
            if n <= 1:
                return None if n == 0 else children[0]
            if isinstance(layout, SplitLayout):
                widget = self._createSplitter(ORIENTATION[layout.orientation])
                for child in children:
                    widget.addWidget(child)
            else:
                doc_mode = DOCUMENT_MODES[layout.tab_style]
                movable = layout.tabs_movable
                tab_pos = TAB_POSITIONS[layout.tab_position]
                widget = self._createTabWidget(doc_mode, movable, tab_pos)
                for child in children:
                    dock_item = child.dockWidget()
                    dock_item.titleBarWidget().hide()
                    widget.addTab(child, dock_item.title())
            return widget
        if isinstance(layout, DockLayoutItem):
            child = self.parentWidget().findChild(QDockItem, layout.name)
            if child is not None and child.parent() not in self._containers:
                return self._createContainer(child)

    def _snapLayout(self, item):
        """ Snap the state of the layout item into a DockLayout object.

        Parameters
        ----------
        item : QWidget
            The widget implementing the layout semantics.

        Returns
        -------
        result : DockLayout
            A dock layout instance appropriate for the type.

        """
        # if isinstance(item, QDockItem):
        #     return DockLayoutItem(item.objectName())
        # if isinstance(item, (QSplitter, QTabWidget)):
        #     kids = []
        #     for index in item.count():
        #         child = self._snapLayout(item.widget(index))
        #         if child is not None:
        #             kids.append(child)
        #     if isinstance(item, QSplitter):
        #         orient = ORIENTATION_INV[item.orientation()]
        #         res = SplitLayout(*kids, orientation=orient)
        #     else:
        #         mode = DOCUMENT_MODES_INV[item.documentMode()]
        #         pos = TAB_POSITIONS_INV[item.tabPosition()]
        #         res = TabbedLayout(*kids, tab_style=mode, tab_position=pos)
        #     return res

    def _cleanup(self, widget):
        """ Cleanup the layout widget.

        Cleanup the widget such that it is removed from the layout
        if it contains one item or less. This operation is recursive
        and traverses up the widget hierarchy.

        Parameters
        ----------
        widget : QSplitter, QStackWidget, or QTabWidget
            The layout widget to cleanup. A QStackWidget is valid
            because it will be the *actual* parent of a QDockContainer
            when added to a QTabWidget.

        """
        # if isinstance(widget, QStackedWidget):
        #     widget = widget.parent()
        # count = widget.count()
        # if count <= 1:
        #     self._splitters.discard(widget)
        #     self._tab_widgets.discard(widget)
        #     parent = widget.parent()
        #     if count == 0:
        #         widget.hide()
        #         widget.setParent(None)
        #         if widget is self._root:
        #             self._root = None
        #         else:
        #             self._cleanup(parent)
        #     else:
        #         child = widget.widget(0)
        #         if widget is self._root:
        #             self._root = child
        #             widget.hide()
        #             widget.setParent(None)
        #             child.setParent(self.parentWidget())
        #             if not self.parentWidget().isHidden():
        #                 child.show()
        #         else:
        #             index = parent.indexOf(widget)
        #             widget.hide()
        #             widget.setParent(None)
        #             parent.insertWidget(index, child)
        #         #if isinstance(widget, QTabWidget):
        #         #    child.titleBarWidget().show()

    #--------------------------------------------------------------------------
    # Plug Handlers
    #--------------------------------------------------------------------------
    # FIXME these plug handlers can use some refactoring
    def _prep_item_plug(self, item, title_vis):
        self._items.add(item)
        item.hide()
        item.setWindowFlags(Qt.Widget)
        item.titleBarWidget().setVisible(title_vis)

    def _plug_border_north(self, item, pos):
        root = self._root
        if root is None:
            return False
        self._prep_item_plug(item, True)
        if isinstance(root, QSplitter) and root.orientation() == Qt.Vertical:
            root.insertWidget(0, item)
        else:
            sp = self._createSplitter(Qt.Vertical)
            sp.addWidget(item)
            sp.addWidget(self._root)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        item.show()
        return True

    def _plug_border_east(self, item, pos):
        root = self._root
        if root is None:
            return False
        self._prep_item_plug(item, True)
        if isinstance(root, QSplitter) and root.orientation() == Qt.Horizontal:
            root.addWidget(item)
        else:
            sp = self._createSplitter(Qt.Horizontal)
            sp.addWidget(self._root)
            sp.addWidget(item)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        item.show()
        return True

    def _plug_border_south(self, item, pos):
        root = self._root
        if root is None:
            return False
        self._prep_item_plug(item, True)
        if isinstance(root, QSplitter) and root.orientation() == Qt.Vertical:
            root.addWidget(item)
        else:
            sp = self._createSplitter(Qt.Vertical)
            sp.addWidget(self._root)
            sp.addWidget(item)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        item.show()
        return True

    def _plug_border_west(self, item, pos):
        root = self._root
        if root is None:
            return False
        self._prep_item_plug(item, True)
        if isinstance(root, QSplitter) and root.orientation() == Qt.Horizontal:
            root.insertWidget(0, item)
        else:
            sp = self._createSplitter(Qt.Horizontal)
            sp.addWidget(item)
            sp.addWidget(self._root)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        item.show()
        return True

    def _plug_compass_north(self, item, pos):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, (QTabWidget, QDockItem)):
            return False
        if hovered is self._root:
            self._prep_item_plug(item, True)
            sp = self._createSplitter(Qt.Vertical)
            sp.addWidget(item)
            sp.addWidget(self._root)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        else:
            # hovered parent should logically be a splitter, but the
            # assumption may break down during very heavy docking.
            parent = hovered.parent()
            if not isinstance(parent, QSplitter):
                return False
            self._prep_item_plug(item, True)
            index = parent.indexOf(hovered)
            if parent.orientation() == Qt.Vertical:
                parent.insertWidget(index, item)
            else:
                sp = self._createSplitter(Qt.Vertical)
                sp.addWidget(item)
                sp.addWidget(hovered)
                parent.insertWidget(index, sp)
                sp.show()
        item.show()
        return True

    def _plug_compass_east(self, item, pos):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, (QTabWidget, QDockItem)):
            return False
        if hovered is self._root:
            self._prep_item_plug(item, True)
            sp = self._createSplitter(Qt.Horizontal)
            sp.addWidget(self._root)
            sp.addWidget(item)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        else:
            # hovered parent should logically be a splitter, but the
            # assumption may break down during very heavy docking.
            parent = hovered.parent()
            if not isinstance(parent, QSplitter):
                return False
            self._prep_item_plug(item, True)
            index = parent.indexOf(hovered)
            if parent.orientation() == Qt.Horizontal:
                parent.insertWidget(index + 1, item)
            else:
                sp = self._createSplitter(Qt.Horizontal)
                sp.addWidget(hovered)
                sp.addWidget(item)
                parent.insertWidget(index, sp)
                sp.show()
        item.show()
        return True

    def _plug_compass_south(self, item, pos):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, (QTabWidget, QDockItem)):
            return False
        if hovered is self._root:
            self._prep_item_plug(item, True)
            sp = self._createSplitter(Qt.Vertical)
            sp.addWidget(self._root)
            sp.addWidget(item)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        else:
            # hovered parent should logically be a splitter, but the
            # assumption may break down during very heavy docking.
            parent = hovered.parent()
            if not isinstance(parent, QSplitter):
                return False
            self._prep_item_plug(item, True)
            index = parent.indexOf(hovered)
            if parent.orientation() == Qt.Vertical:
                parent.insertWidget(index + 1, item)
            else:
                sp = self._createSplitter(Qt.Vertical)
                sp.addWidget(hovered)
                sp.addWidget(item)
                parent.insertWidget(index, sp)
                sp.show()
        item.show()
        return True

    def _plug_compass_west(self, item, pos):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, (QTabWidget, QDockItem)):
            return False
        if hovered is self._root:
            self._prep_item_plug(item, True)
            sp = self._createSplitter(Qt.Horizontal)
            sp.addWidget(item)
            sp.addWidget(self._root)
            self._root = sp
            sp.setParent(self.parentWidget())
            sp.show()
        else:
            # hovered parent should logically be a splitter, but the
            # assumption may break down during very heavy docking.
            parent = hovered.parent()
            if not isinstance(parent, QSplitter):
                return False
            self._prep_item_plug(item, True)
            index = parent.indexOf(hovered)
            if parent.orientation() == Qt.Horizontal:
                parent.insertWidget(index, item)
            else:
                sp = self._createSplitter(Qt.Horizontal)
                sp.addWidget(item)
                sp.addWidget(hovered)
                parent.insertWidget(index, sp)
                sp.show()
        item.show()
        return True

    def _plug_compass_center(self, item, pos):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, (QTabWidget, QDockItem)):
            return False
        self._prep_item_plug(item, False)
        if isinstance(hovered, QTabWidget):
            hovered.addTab(item, item.title())
            hovered.setCurrentIndex(hovered.count() - 1)
        else:
            if hovered is not self._root:
                parent = hovered.parent()
                index = parent.indexOf(hovered)
            hovered.titleBarWidget().setVisible(False)
            tw = self._createTabWidget(True, True, QTabWidget.North)
            tw.addTab(hovered, hovered.title())
            tw.addTab(item, item.title())
            tw.setCurrentIndex(tw.count() - 1)
            if hovered is self._root:
                self._root = tw
                tw.setParent(self.parentWidget())
            else:
                parent.insertWidget(index, tw)
            tw.show()
        item.show()
        return True

    def _plug_splitter(self, item, pos, orient):
        hovered = self.hitTest(pos)
        if not isinstance(hovered, QSplitterHandle):
            return False
        if hovered.orientation() != orient:
            return False
        self._prep_item_plug(item, True)
        splitter = hovered.parent()
        for index in xrange(1, splitter.count()):
            if splitter.handle(index) is hovered:
                splitter.insertWidget(index, item)
                break
        item.show()
        return True

    def _plug_split_vertical(self, item, pos):
        return self._plug_splitter(item, pos, Qt.Vertical)

    def _plug_split_horizontal(self, item, pos):
        return self._plug_splitter(item, pos, Qt.Horizontal)

    def _plug_single_center(self, item, pos):
        if self._root is not None:
            return False
        self._root = item
        self._prep_item_plug(item, True)
        item.setParent(self.parentWidget())
        item.show()
        return True

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def hasItems(self):
        """ Get whether or not the layout has dock items.

        Returns
        -------
        result : bool
            True if the layout has dock items, False otherwise.

        """
        return len(self._containers) > 0

    def itemCount(self):
        """ Get the number of dock items managed by the area.

        Returns
        -------
        result : int
            The number of dock items in the dock area.

        """
        return len(self._containers)

    def dockLayout(self):
        """ Get the current layout configuration for the dock area.

        Returns
        -------
        result : DockLayout or None
            An Enaml DockLayout object for the current layout config,
            or None if the area has no docked items.

        """
        root = self._root
        if root is None:
            return None
        return self._snapLayout(root)

    def setDockLayout(self, layout):
        """ Set the layout configuration for the dock area.

        Parameters
        ----------
        layout : DockLayout
            The DockLayout object which describes the configuration
            of the dock area.

        """
        root = self._root
        if root is not None:
            root.hide()
            root.setParent(None)
        self._splitters.clear()
        self._containers.clear()
        self._tab_widgets.clear()
        newroot = self._buildLayout(layout)
        if newroot is not None:
            parent = self.parentWidget()
            newroot.setParent(parent)
            if not parent.isHidden():
                newroot.show()
        self._root = newroot

    def plug(self, item, pos, guide):
        """ Plug a dock item into the layout.

        Parameters
        ----------
        item : QDockItem
            The dock item which is being plugged.

        pos : QPoint
            The position at which to plug the item.

        mode : QGuideRose.Guide
            The guide which determines how the item should be plugged.

        Returns
        -------
        result : bool
            True if the item was successfully plugged, False otherwise.

        """
        if item in self._items:
            return False
        handler_name = self._plug_handlers[guide]
        if handler_name is None:
            return False
        handler = getattr(self, handler_name, None)
        if handler is None:
            return False
        return handler(item, pos)

    def unplug(self, container):
        """ Unplug a dock container from the layout.

        Parameters
        ----------
        container : QDockContainer
            The dock container to unplug from the layout.

        """
        if container in self._containers:
            container.hide()
            self._containers.remove(container)
            if container is self._root:
                self._root = None
                container.setParent(None)
            else:
                parent = container.parent()
                if parent is not None:
                    container.setParent(None)
                    #self._cleanup(parent)

    def hitTest(self, pos):
        """ Hit test the layout for a relevant widget under a point.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in coordinates of the
            parent widget.

        Returns
        -------
        result : QWidget or None
            A widget which is relevant for docking purposes, or None
            if no such widget was found under the point.

        """
        widget = self.parentWidget()
        if widget is None:
            return
        root = self._root
        if root is None:
            return

        # Splitter handles have priority. Their active area is smaller
        # and overlaps that of other widgets. Giving dock items priority
        # would make it very difficult to hit a splitter reliably. In
        # certain configurations, there may be more than one handle in
        # the hit box. In that case, the one closest to center wins.
        handles = []
        for sp in self._splitters:
            pt = sp.mapFrom(widget, pos)
            for index in xrange(1, sp.count()):  # handle 0 is always hidden
                handle = sp.handle(index)
                rect = handle.rect().adjusted(-20, -20, 20, 20)
                pt2 = handle.mapFrom(sp, pt)
                if rect.contains(pt2):
                    l = (rect.center() - pt2).manhattanLength()
                    handles.append((l, handle))
        if len(handles) > 0:
            handles.sort()
            return handles[0][1]

        # Check for tab widgets next. A tab widget holds dock items,
        # but should have priority over the dock items themselves.
        for tb in self._tab_widgets:
            pt = tb.mapFrom(widget, pos)
            if tb.rect().contains(pt):
                return tb

        # Check for QDockItems last. The are the most common case, but
        # also have the least precedence compared to the other cases.
        for it in self._items:
            pt = it.mapFrom(widget, pos)
            if it.rect().contains(pt):
                return it

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        root = self._root
        if root is not None:
            root.setGeometry(rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        root = self._root
        if root is not None:
            return root.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size of the layout.

        """
        root = self._root
        if root is not None:
            return root.minimumSizeHint()
        return QSize(256, 192)

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        widget = self._root
        if widget is not None:
            return widget.maximumSize()
        return QSize(16777215, 16777215)

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayout` instead.

        """
        msg = 'Use `setDockLayoutLayout` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        return 0

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        return None

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None
