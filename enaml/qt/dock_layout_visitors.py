#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTabWidget, QSplitter

from atom.api import Atom, List, Typed

from enaml.widgets.dock_layout import LayoutItem, TabbedLayout, SplitLayout

from .q_dock_container import QDockContainer
from .q_dock_item import QDockItem
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

    items = Typed(set, ())

    @classmethod
    def build(cls, layout, area):
        return cls().visit(layout, area)

    def visit(self, layout, area):
        name = 'visit_' + type(layout).__name__
        return getattr(self, name)(layout, area)

    def visit_SplitLayout(self, layout, area):
        children = (self.visit(item, area) for item in layout.items)
        children = filter(None, children)
        if len(children) == 0:
            return None
        if len(children) == 1:
            return children[0]
        splitter = QSplitter(ORIENTATION[layout.orientation])
        for child in children:
            splitter.addWidget(child)
        return splitter

    def visit_TabbedLayout(self, layout, area):
        children = (self.visit(item, area) for item in layout.items)
        children = filter(None, children)
        if len(children) == 0:
            return None
        if len(children) == 1:
            return children[0]
        tab_widget = QTabWidget()
        tab_widget.setTabBar(QDockTabBar())
        tab_widget.setDocumentMode(DOCUMENT_MODE[layout.tab_style])
        tab_widget.setMovable(layout.tabs_movable)
        tab_widget.setTabPosition(TAB_POSITION[layout.tab_position])
        for child in children:
            dock_item = child.dockItem()
            dock_item.titleBarWidget().hide()
            tab_widget.addTab(child, dock_item.title())
        return tab_widget

    def visit_LayoutItem(self, layout, area):
        child = area.findChild(QDockItem, layout.name)
        if child is not None and child not in self.items:
            self.items.add(child)
            container = QDockContainer()
            container.setDockItem(child)
            return container


class LayoutSaver(Atom):

    @classmethod
    def save(cls, widget):
        return cls().visit(widget)

    def visit(self, widget):
        name = 'visit_' + type(widget).__name__
        return getattr(self, name)(widget)

    def visit_QSplitter(self, widget):
        children = (self.visit(widget.widget(i)) for i in widget.count())
        children = filter(None, children)
        orientation = ORIENTATION_INV[widget.orientation()]
        return SplitLayout(*children, orientation=orientation)

    def visit_QTabWidget(self, widget):
        children = (self.visit(widget.widget(i)) for i in widget.count())
        children = filter(None, children)
        kw = {}
        kw['tab_style'] = DOCUMENT_MODE_INV[widget.documentMode()]
        kw['tab_position'] = TAB_POSITION_INV[widget.tabPosition()]
        kw['tabs_movable'] = widget.movable()
        return TabbedLayout(*children, **kw)

    def visit_QDockContainer(self, widget):
        return LayoutItem(widget.objectName())


class LayoutHitTester(Atom):

    _splitter_handles = List()

    _tab_widgets = List()

    _containers = List()

    @classmethod
    def from_widget(cls, widget):
        self = cls()
        self.visit(widget)
        return self

    #--------------------------------------------------------------------------
    # Visitor Methods
    #--------------------------------------------------------------------------
    def visit(self, widget):
        name = 'visit_' + type(widget).__name__
        return getattr(self, name)(widget)

    def visit_QSplitter(self, widget):
        handles = self._splitter_handles
        for index in xrange(1, widget.count()):
            handles.append(widget.handle(index))
        for index in xrange(widget.count()):
            self.visit(widget.widget(index))

    def visit_QTabWidget(self, widget):
        self._tab_widgets.append(widget)
        for index in xrange(widget.count()):
            self.visit(widget.widget(index))

    def visit_QDockContainer(self, widget):
        self._containers.append(widget)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def hit_test(self, area, pos):
        # Splitter handles have priority. Their active area is smaller
        # and overlaps that of other widgets. Giving dock containers
        # priority would make it difficult to hit a splitter reliably.
        # In certain configurations, there may be more than one handle
        # in the hit box, in which case the one closest to center wins.
        hits = []
        for handle in self._splitter_handles:
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
        for tab_widget in self._tab_widgets:
            pt = tab_widget.mapFrom(area, pos)
            if tab_widget.rect().contains(pt):
                return tab_widget

        # Check for QDockContainers last. The are the most common case,
        # but also have the least precedence compared to the others.
        for container in self._containers:
            pt = container.mapFrom(area, pos)
            if container.rect().contains(pt):
                return container


class LayoutUnplugger(Atom):

    @classmethod
    def unplug(cls, root, container):
        return cls().visit(root, container)

    def visit(self, widget, container):
        name = 'visit_' + type(widget).__name__
        return getattr(self, name)(widget, container)

    def visit_QSplitter(self, widget, container):
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
        if widget is container:
            container.hide()
            container.setParent(None)
            container.dockItem().titleBarWidget().show()
            return True, None
        return False, None
