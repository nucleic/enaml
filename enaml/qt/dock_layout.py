#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint
from PyQt4.QtGui import QApplication, QSplitter, QTabWidget, QTabBar

from atom.api import Atom, List, Enum, Typed, ForwardTyped


class DockLayoutBase(Atom):
    """ A base class for the dock layout classes.

    """
    #: The parent of the dock layout. This is updated automatically
    #: by the various subclasses and should not be manipulated.
    parent = ForwardTyped(lambda: DockLayoutBase)

    def widget(self):
        """ Get the QWidget associated with the layout.

        """
        raise NotImplementedError

    def setGeometry(self, rect):
        """ Set the geometry for the layout.

        """
        widget = self.widget()
        if widget is not None:
            widget.setGeometry(rect)

    def sizeHint(self):
        """ Compute the size hint for the layout item.

        """
        widget = self.widget()
        if widget is not None:
            return widget.sizeHint()
        return QSize(0, 0)

    def minimumSize(self):
        """ Compute the minimum size of the layout item.

        """
        widget = self.widget()
        if widget is not None:
            return widget.minimumSizeHint()
        return QSize(0, 0)


def QDockItem():
    """ A forward declaration function for resolving QDockItem.

    """
    from .q_dock_item import QDockItem
    return QDockItem


class DockLayoutItem(DockLayoutBase):
    """ A dock layout which manages a QDockItem.

    """
    #: The QDockItem instance managed by this layout item.
    dock_item = ForwardTyped(QDockItem)

    #: An internal flag for testing emptiness.
    def __init__(self, dock_item):
        """ Initialize a DockLayoutItem.

        Parameters
        ----------
        dock_item : QDockItem
            The dock item to manage with this layout item.

        """
        super(DockLayoutItem, self).__init__(dock_item=dock_item)
        dock_item._dock_state.layout = self

    def widget(self):
        """ Get the QWidget associated with the layout.

        """
        return self.dock_item


class SplitDockLayout(DockLayoutBase):
    """ A dock layout which arranges its items in a splitter.

    """
    #: The orientation of the dock splitter
    orientation = Enum(Qt.Vertical, Qt.Horizontal)

    #: The list of items to include in the split dock layout.
    #: These must be instances of DockLayoutBase.
    items = List(DockLayoutBase)

    #: The QSplitter widget used to implement the layout.
    splitter = Typed(QSplitter)

    def __init__(self, items, **kwargs):
        """ Initialize a SplitDockLayout.

        Parameters
        ----------
        items : list
            The list of layout items to include in the splitter.

        **kwargs
            Additional configuration data for the layout item.

        """
        super(SplitDockLayout, self).__init__(items=items, **kwargs)
        splitter = self.splitter = QSplitter(self.orientation)
        for item in items:
            item.parent = self
            splitter.addWidget(item.widget())

    def widget(self):
        """ Get the widget associated with the layout.

        """
        return self.splitter

    def sizes(self):
        """ Get the list of sizes of the splitter items.

        Returns
        -------
        result : list
            The list of integer sizes of the items in the splitter.

        """
        return self.splitter.sizes()

    def setSizes(self, sizes):
        """ Set the sizes of the items in the splitter.

        Parameters
        ----------
        sizes : list
            The list of integer sizes to apply to the splitter.

        """
        self.splitter.setSizes(sizes)
        self.sizes = self.splitter.sizes()

    def addItem(self, item):
        """ Add an item to the splitter.

        Parameters
        ----------
        item : DockLayoutBase
            The layout item to add to the splitter, it must not already
            exist in the layout.

        """
        self.insertItem(len(self.items), item)

    def insertItem(self, index, item):
        """ Insert an item into the splitter at the given index.

        Parameters
        ----------
        index : int
            The integer index at which to insert the item.

        item : DockLayoutBase
            The item to insert into the splitter layout. It must not
            already exist in the layout.

        """
        assert item not in self.items, 'item already exists in the layout'
        item.parent = self
        self.items.insert(index, item)
        self.splitter.insertWidget(index, item.widget())

    def removeItem(self, item):
        """ Remove an item from the splitter layout.

        Parameters
        ----------
        item : DockLayoutBase
            The layout item to remove from the tabbed layout. It must
            already exist in the layout.

        """
        assert item in self.items, 'item does not exist in the layout'
        item.parent = None
        self.items.remove(item)
        widget = item.widget()
        widget.hide()
        widget.setParent(None)

    def releaseItem(self, item):
        assert item in self.items, 'item does not exist in the layout'
        item.parent = None
        self.items.remove(item)


class QDockTabBar(QTabBar):
    """ A custom QTabBar that manages safetly undocking a tab.

    The user can undock a tab by holding Shift before dragging the tab.

    """
    class DragState(Atom):
        """ A framework class for managing a tab drag.

        This class should not be used directly by user code.

        """
        #: The location of the users click on the tab.
        press_pos = Typed(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockTabBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget for the tab bar.

        """
        super(QDockTabBar, self).__init__(parent)
        self._drag_state = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _initDrag(self, pos):
        """ Initialize the drag state for the tab.

        If the drag state is already inited, this method is a no-op.

        Parameters
        ----------
        pos : QPoint
            The point where the user clicked the mouse, expressed in
            the local coordinate system.

        """
        if self._drag_state is not None:
            return
        state = self._drag_state = self.DragState()
        state.press_pos = pos

    def _startDrag(self):
        """" Start the drag process for the dock item.

        This method unplugs the dock item from the layout and transfers
        the repsonsibilty of moving the floating frame back to the dock
        item. After calling this method, no mouseReleaseEvent will be
        generated since the dock item grabs the mouse. If the item is
        already being dragged, this method is a no-op.

        """
        state = self._drag_state
        if state is None:
            return
        dock_item = self.parent().widget(self.currentIndex())
        dock_item.titleBarWidget().setVisible(True)
        dock_area = dock_item.dockArea()
        dock_area.unplug(dock_item)
        i_state = dock_item.DragState(press_pos=state.press_pos, dragging=True)
        dock_item._drag_state = i_state
        dock_item.grabMouse()
        self._drag_state = None

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """ Handle the mouse press event for the tab bar.

        If the shift key is pressed, and the click is over a tab, a
        dock drag is initiated.

        """
        shift = Qt.ShiftModifier
        if event.button() == Qt.LeftButton and event.modifiers() & shift:
            if self.tabAt(event.pos()) != -1:
                self._initDrag(event.pos())
        super(QDockTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the tab bar.

        If the dock drag is initiated and distances is greater than the
        start drag distances, the item will be undocked.

        """
        state = self._drag_state
        if state is None:
            super(QDockTabBar, self).mouseMoveEvent(event)
        else:
            dist = (event.pos() - state.press_pos).manhattanLength()
            if dist > QApplication.startDragDistance():
                self._startDrag()


class TabbedDockLayout(DockLayoutBase):
    """ A dock layout which arranges its items in a tabbed container.

    """
    #: The list of dock layout items managed by the layout.
    items = List(DockLayoutItem)

    #: The tab widget used to implement the layout.
    tab_widget = Typed(QTabWidget)

    def __init__(self, items, **kwargs):
        """ Initialize a TabbedDockLayout.

        Parameters
        ----------
        items : list
            The list of dock layout items to include in the tab layout.

        **kwargs
            Additional configuration data for the layout item.

        """
        super(TabbedDockLayout, self).__init__(items=items, **kwargs)
        tab_widget = self.tab_widget = QTabWidget()
        tab_widget.setTabBar(QDockTabBar())
        for item in items:
            item.parent = self
            dock = item.widget()
            dock.titleBarWidget().setVisible(False)
            tab_widget.addTab(dock, dock.title())
        tab_widget.setMovable(True)
        tab_widget.setDocumentMode(True)
        tab_widget.tabBar().tabMoved.connect(self._onTabMoved)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTabMoved(self, index_from, index_to):
        """ Handle the 'tabMoved' signal on the tab widget.

        """
        items = self.items
        items.insert(index_to, items.pop(index_from))

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def widget(self):
        """ Get the widget associated with the layout.

        """
        return self.tab_widget

    def addItem(self, item):
        """ Add an item to the tabbed layout.

        Parameters
        ----------
        item : DockLayoutItem
            The layout item to add to the tabbed layout, it must not
            already exist in the layout.

        """
        self.insertItem(len(self.items), item)

    def insertItem(self, index, item):
        """ Insert an item into the tabbed layout at the given index.

        Parameters
        ----------
        index : int
            The integer index at which to insert the item.

        item : DockLayoutItem
            The item to insert into the tabbed layout. It must not
            already exist in the layout.

        """
        assert item not in self.items, 'item already exists in the layout'
        item.parent = self
        self.items.insert(index, item)
        dock = item.widget()
        dock.titleBarWidget().setVisible(False)
        self.tab_widget.insertWidget(index, dock, dock.title())

    def removeItem(self, item):
        """ Remove an item from the tabbed layout.

        Parameters
        ----------
        item : DockLayoutItem
            The layout item to remove from the tabbed layout. It must
            already exist in the layout.

        """
        assert item in self.items, 'item does not exist in the layout'
        item.parent = None
        self.items.remove(item)
        widget = item.widget()
        widget.hide()
        widget.titleBarWidget().setVisible(True)
        widget.setParent(None)

    def releaseItem(self, item):
        assert item in self.items, 'item does not exist in the layout'
        item.parent = None
        self.items.remove(item)
        item.widget().titleBarWidget().setVisible(True)
