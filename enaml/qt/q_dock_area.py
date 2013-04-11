#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect, QTimer
from PyQt4.QtGui import (
    QFrame, QLayout, QRubberBand, QSplitter, QSplitterHandle, QTabWidget
)

from atom.api import Atom, Int, Typed, ForwardTyped

from enaml.widgets.dock_layout import DockLayoutItem, SplitLayout, TabbedLayout

from .q_dock_item import QDockItem
from .q_dock_tabbar import QDockTabBar
from .q_guide_rose import QGuideRose


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
        self._tab_widgets = set()
        self._containers = set()
        self._splitters = set()
        self._items = set()
        self._parents = {}
        self._root = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _resolveItems(self, items):
        """ Resolve a list of dock layout items.

        This an internal method used by the layout to generate the
        widget layout hierarchy from a DockLayout configuration.

        Parameters
        ----------
        items : list
            The list of DockLayout objects to resovle into their
            respective QWidget representations.

        """
        resolved = []
        these = self._items
        widget = self.parentWidget()
        for item in items:
            if isinstance(item, DockLayoutItem):
                child = widget.findChild(QDockItem, item.name)
                if child is not None and child not in these:
                    resolved.append(child)
                    these.add(child)
            elif isinstance(item, (SplitLayout, TabbedLayout)):
                child = self._buildLayout(item)
                if child is not None:
                    resolved.append(child)
        return resolved

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
        parents = self._parents
        if isinstance(layout, SplitLayout):
            items = self._resolveItems(layout.items)
            n = len(items)
            if n == 0:
                return None
            if n == 1:
                return items[0]
            sp = QSplitter()
            sp.setOrientation(ORIENTATION[layout.orientation])
            for child in items:
                sp.addWidget(child)
                parents[child] = sp
            self._containers.add(sp)
            self._splitters.add(sp)
            return sp
        if isinstance(layout, TabbedLayout):
            items = self._resolveItems(layout.items)
            n = len(items)
            if n == 0:
                return None
            if n == 1:
                return items[0]
            tw = QTabWidget()
            tw.setTabBar(QDockTabBar())
            tw.setMovable(layout.tabs_movable)
            tw.setDocumentMode(DOCUMENT_MODES[layout.tab_style])
            tw.setTabPosition(TAB_POSITIONS[layout.tab_position])
            for child in items:
                child.titleBarWidget().hide()
                tw.addTab(child, child.title())
                parents[child] = tw
            self._containers.add(tw)
            self._tab_widgets.add(tw)
            return tw
        if isinstance(layout, DockLayoutItem):
            child = self.parentWidget().findChild(QDockItem, layout.name)
            if child is not None:
                self._items.add(child)
            return child

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
        if isinstance(item, QDockItem):
            return DockLayoutItem(item.objectName())
        if isinstance(item, QSplitter):
            children = []
            for index in item.count():
                child = self._snapLayout(item.widget(index))
                if child is not None:
                    children.append(child)
            orient = ORIENTATION_INV[item.orientation()]
            return SplitLayout(*children, orientation=orient)
        if isinstance(item, QTabWidget):
            children = []
            for index in item.count():
                child = self._snapLayout(item.widget(index))
                if child is not None:
                    children.append(child)
            mode = DOCUMENT_MODES_INV[item.documentMode()]
            pos = TAB_POSITIONS_INV[item.tabPosition()]
            return TabbedLayout(*children, tab_style=mode, tab_position=pos)

    def _cleanupContainer(self, container):
        """ Cleanup the layout container.

        If the given container is empty it will be removed. If it has
        a single item, the item will be reparented and the container
        will be removed. This operation is performed recursively.

        Parameters
        ----------
        container : QSplitter or QTabWidget
            The layout container to cleanup.

        """
        count = container.count()
        if count == 0:
            # If there are no more items in the container, the container
            # removed from the layout. If the container has no logical
            # parent, that means there is nothing left in the dock area.
            # Otherwise the parent container needs to be recursively
            # cleaned to account for its new state.
            self._containers.remove(container)
            self._splitters.discard(container)
            self._tab_widgets.discard(container)
            parent = self._parents.pop(container, None)
            container.setParent(None)
            if parent is None:
                self._root = None
            else:
                self._cleaupContainer(parent)
        elif count == 1:
            # If there is only a single item in the container, it is
            # removed an reparented to the container's parent. This is
            # either another container, or the dock area widget. There
            # no need to recursively clean the parent since its overall
            # count does not change.
            self._containers.remove(container)
            self._splitters.discard(container)
            self._tab_widgets.discard(container)
            child = container.widget(0)
            parent = self._parents.pop(container, None)
            if parent is None:
                child.setParent(self.parentWidget())
                if not self.parentWidget().isHidden():
                    child.show()
                self._parents[child] = None
                self._root = child
            else:
                # Unparent the container first so that the size of
                # the parent container remains relatively unchanged.
                index = parent.indexOf(container)
                container.setParent(None)
                parent.insertWidget(index, child)
                self._parents[child] = parent
            if isinstance(container, QTabWidget):
               child.titleBarWidget().show()

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
        return len(self._items) > 0

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
        self._containers.clear()
        self._items.clear()
        self._parents.clear()
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
            The guide which determines how the item is plugged.

        Returns
        -------
        result : bool
            True if the item was successfully plugged, False otherwise.

        """
        if item in self._items:
            return False
        Guide = QGuideRose.Guide
        if guide == Guide.NoGuide:
            return False

        if guide == Guide.SingleCenter:
            if self._root is not None:
                return False
            self._root = item
            self._items.add(item)
            self._parents[item] = None
            item.hide()
            item.setWindowFlags(Qt.Widget)
            item.setParent(self.parentWidget())
            self.invalidate()
            item.show()
            return True

        if guide == Guide.CompassCenter:
            widget = self.hitTest(pos)

            if isinstance(widget, QTabWidget):
                self._items.add(item)
                self._parents[item] = widget
                item.hide()
                item.titleBarWidget().hide()
                item.setWindowFlags(Qt.Widget)
                widget.addTab(item, item.title())
                widget.setCurrentIndex(widget.count() - 1)
                item.show()
                return True

            if isinstance(widget, QDockItem):
                parent = self._parents.get(widget)
                if parent is None:
                    return False

                tw = QTabWidget()
                tw.setTabBar(QDockTabBar())
                tw.setDocumentMode(True)
                tw.setMovable(True)

                self._items.add(item)
                self._parents[widget] = tw
                self._parents[item] = tw
                self._parents[tw] = parent
                self._containers.add(tw)
                self._tab_widgets.add(tw)

                item.hide()
                item.setWindowFlags(Qt.Widget)
                item.titleBarWidget().hide()
                widget.hide()
                index = parent.indexOf(widget)
                widget.titleBarWidget().hide()

                tw.addTab(widget, widget.title())
                tw.addTab(item, item.title())
                tw.setCurrentIndex(1)

                parent.insertWidget(index, tw)
                widget.show()
                item.show()
                tw.show()
                return True

        if guide == Guide.CompassWest:
            widget = self.hitTest(pos)

            if isinstance(widget, QDockItem):
                parent = self._parents.get(widget)
                if not isinstance(parent, QSplitter):
                    return False
                self._items.add(item)
                item.hide()
                item.setWindowFlags(Qt.Widget)
                if parent.orientation() == Qt.Horizontal:
                    index = parent.indexOf(widget)
                    parent.insertWidget(index, item)
                    self._parents[item] = parent
                else:
                    sp = QSplitter()
                    sp.setOrientation(Qt.Horizontal)
                    index = parent.indexOf(widget)
                    self._containers.add(sp)
                    self._splitters.add(sp)
                    self._parents[widget] = sp
                    self._parents[item] = sp
                    self._parents[sp] = parent
                    widget.setParent(None)
                    sp.addWidget(item)
                    sp.addWidget(widget)
                    parent.insertWidget(index, sp)
                    widget.show()
                    sp.show()
                item.show()
                return True

        return False

    def unplug(self, item):
        """ Unplug a dock item from the layout.

        Parameters
        ----------
        item : QDockItem
            The dock item to unplug from the layout.

        """
        if item in self._items:
            parent = self._parents.pop(item, None)
            self._items.remove(item)
            item.setParent(None)
            if parent is None:
                self._root = None
            else:
                self._cleanupContainer(parent)

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
        # would make it very difficult to hit a splitter reliably.
        for sp in self._splitters:
            pt = sp.mapFrom(widget, pos)
            for index in xrange(1, sp.count()):
                handle = sp.handle(index)
                rect = handle.rect().adjusted(-20, -20, 20, 20)
                if rect.contains(handle.mapFrom(sp, pt)):
                    return handle

        # Check for tab widgets next. A tab widget holds a dock item,
        # but should have priority over the dock items.
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

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayout` instead.

        """
        msg = 'Use `setDockLayoutItem` instead.'
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


class DockOverlays(Atom):
    """ An object which manages the overlays for a QDockArea.

    This manager handles the state transitions for the overlays. The
    transitions are performed on a slightly-delayed timer to provide
    a more fluid user interaction experience.

    """
    #: The dock area owner of the overlays.
    _owner = ForwardTyped(lambda: QDockArea)

    #: The overlayed guide rose.
    _rose = Typed(QGuideRose, ())

    #: The overlayed rubber band.
    _band = Typed(QRubberBand, (QRubberBand.Rectangle,))

    #: The target mode to apply to the rose on timeout.
    _target_rose_mode = Int(QGuideRose.Mode.NoMode)

    #: The target geometry to apply to rubber band on timeout.
    _target_band_geo = Typed(QRect, factory=lambda: QRect())

    #: The value of the last guide which was hit in the rose.
    _last_guide = Int(-1)

    #: The hover position of the mouse to use for state changes.
    _hover_pos = Typed(QPoint)

    #: The timer for changing the state of the rose.
    _rose_timer = Typed(QTimer)

    #: The timer for changing the state of the band.
    _band_timer = Typed(QTimer)

    def __init__(self, owner):
        """ Initialize a DockOverlays.

        Parameters
        ----------
        owner : QDockArea
            The dock area owner of the overlays.

        """
        super(DockOverlays, self).__init__(_owner=owner)

    #--------------------------------------------------------------------------
    # Default Value Methods
    #--------------------------------------------------------------------------
    def _default__rose_timer(self):
        """ Create the timer for the rose state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_rose_timer)
        return timer

    def _default__band_timer(self):
        """ Create the timer for the band state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_band_timer)
        return timer

    #--------------------------------------------------------------------------
    # Timer Handlers
    #--------------------------------------------------------------------------
    def _on_rose_timer(self):
        """ Handle the timeout event for the internal rose timer.

        This handler transitions the rose to its new state and updates
        the position of the rubber band.

        """
        rose = self._rose
        rose.setMode(self._target_rose_mode)
        rose.hover(self._hover_pos)
        self._refresh_band()

    def _on_band_timer(self):
        """ Handle the timeout event for the internal band timer.

        """
        self._refresh_band()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_band(self):
        """ Refresh the state of the rubber band.

        """
        band = self._band
        geo = self._target_band_geo
        if geo.isValid():
            band.setGeometry(geo)
            if band.isHidden():
                band.show()
                self._rose.raise_()
        else:
            band.hide()

    def _band_geometry(self, guide, widget):
        """ Compute the rubber band geometry for a guide and a widget.

        Parameters
        ----------
        guide : QGuideRose.Guide
            The guide enum indicating which guide in the rose lies
            under the current mouse location.

        widget : QWidget
            The relevant dock widget which lies under the mouse. This
            will be a splitter handle, a dock item, or a tab widget.

        """
        border_size = 60
        owner = self._owner
        Guide = QGuideRose.Guide
        if guide == Guide.NoGuide:
            return QRect()

        # border hits
        m = owner.contentsMargins()
        if guide == Guide.BorderNorth:
            p = QPoint(m.left(), m.top())
            s = QSize(owner.width() - m.left() - m.right(), border_size)
        elif guide == Guide.BorderEast:
            p = QPoint(owner.width() - border_size - m.right(), m.top())
            s = QSize(border_size, owner.height() - m.top() - m.bottom())
        elif guide == Guide.BorderSouth:
            p = QPoint(m.left(), owner.height() - border_size - m.bottom())
            s = QSize(owner.width() - m.left() - m.right(), border_size)
        elif guide == Guide.BorderWest:
            p = QPoint(m.left(), m.top())
            s = QSize(border_size, owner.height() - m.top() - m.bottom())

        # compass hits
        elif guide == Guide.CompassNorth:
            p = widget.mapTo(owner, QPoint(0, 0))
            s = widget.size()
            s.setHeight(s.height() / 3)
        elif guide == Guide.CompassEast:
            p = widget.mapTo(owner, QPoint(0, 0))
            s = widget.size()
            d = s.width() / 3
            r = s.width() - d
            s.setWidth(d)
            p.setX(p.x() + r)
        elif guide == Guide.CompassSouth:
            p = widget.mapTo(owner, QPoint(0, 0))
            s = widget.size()
            d = s.height() / 3
            r = s.height() - d
            s.setHeight(d)
            p.setY(p.y() + r)
        elif guide == Guide.CompassWest:
            p = widget.mapTo(owner, QPoint(0, 0))
            s = widget.size()
            s.setWidth(s.width() / 3)
        elif guide == Guide.CompassCenter:
            p = widget.mapTo(owner, QPoint(0, 0))
            s = widget.size()

        # splitter handle hits
        elif guide == Guide.SplitHorizontal:
            p = widget.mapTo(owner, QPoint(0, 0))
            wo, r = divmod(border_size - widget.width(), 2)
            wo += r
            p.setX(p.x() - wo)
            s = QSize(2 * wo + widget.width(), widget.height())
        elif guide == Guide.SplitVertical:
            p = widget.mapTo(owner, QPoint(0, 0))
            ho, r = divmod(border_size - widget.height(), 2)
            ho += r
            p.setY(p.y() - ho)
            s = QSize(widget.width(), 2 * ho + widget.height())

        # default no-op
        else:
            s = QSize()
            p = QPoint()

        p = owner.mapToGlobal(p)
        return QRect(p, s)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def hide(self):
        """ Hide the overlay widgets from the screen.

        """
        self._rose_timer.stop()
        self._band_timer.stop()
        self._rose.hide()
        self._band.hide()

    def hover(self, pos):
        """ Update the overlays based on the mouse hover position.

        Parameters
        ----------
        pos : QPoint
            The hover position, expressed in the coordinate system
            of the owner dock area.

        """
        owner = self._owner
        rose = self._rose
        Mode = QGuideRose.Mode

        # Special case the hover when the dock area has no docked items.
        # In this case, the special single center guide mode is used. It
        # is a special case because no hit testing is necessary.
        if not owner.layout().hasItems():
            self._hover_pos = pos
            center = QPoint(owner.width() / 2, owner.height() / 2)
            rose.setMode(Mode.SingleCenter)
            rose.setCenter(center)
            rose.hover(pos)
            guide = rose.hitTest(pos, Mode.SingleCenter)
            origin = owner.mapToGlobal(QPoint(0, 0))
            if guide != self._last_guide:
                self._last_guide = guide
                if guide == QGuideRose.Guide.SingleCenter:
                    m = owner.contentsMargins()
                    g = QRect(origin, owner.size())
                    g = g.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
                    self._target_band_geo = g
                else:
                    self._target_band_geo = QRect()
                self._band_timer.start(50)
            if rose.isHidden():
                rose.setGeometry(QRect(origin, owner.size()))
                rose.show()
            return

        # Compute the target mode for the guide rose based on the
        # widget lying under the hover position.
        widget = owner.layout().hitTest(pos)
        if isinstance(widget, (QDockItem, QTabWidget)):
            center = widget.mapTo(owner, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
            target_mode = Mode.Compass
        elif isinstance(widget, QSplitterHandle):
            if widget.orientation() == Qt.Horizontal:
                target_mode = Mode.SplitHorizontal
            else:
                target_mode = Mode.SplitVertical
            center = widget.mapTo(owner, QPoint(0, 0))
            center += QPoint(widget.width() / 2, widget.height() / 2)
        else:
            target_mode = Mode.NoMode
            center = QPoint()

        # Update the state of the rose. If it is to be hidden, it is
        # done so immediately. If the target mode is different from
        # the current mode, the rose is hidden and the change update
        # is collapsed on a timer.
        self._target_rose_mode = target_mode
        if target_mode == Mode.NoMode:
            self._rose_timer.stop()
            rose.setMode(target_mode)
        elif target_mode != rose.mode():
            rose.setMode(Mode.NoMode)
            self._rose_timer.start(30)
        rose.setCenter(center)

        # Hit test the rose target update the target geometry for the
        # rubber band if the target guide has changed.
        update_band = False
        guide = rose.hitTest(pos, target_mode)
        if guide != self._last_guide:
            self._last_guide = guide
            self._target_band_geo = self._band_geometry(guide, widget)
            update_band = True

        # If the rose is currently visible, pass it the hover event so
        # that is can trigger a repaint of the guides if needed. Queue
        # an update for the band geometry. This prevents the band from
        # flickering when rapidly cycling between guide pads.
        if rose.mode() != Mode.NoMode:
            rose.hover(pos)
            if update_band:
                self._band_timer.start(50)

        # Ensure that the rose is shown on the screen.
        self._hover_pos = pos
        if rose.isHidden():
            origin = owner.mapToGlobal(QPoint(0, 0))
            rose.setGeometry(QRect(origin, owner.size()))
            rose.show()


class QDockArea(QFrame):
    """ A custom QFrame which provides an area for docking QDockItems.

    A dock area is used by creating QDockItem instances using the dock
    area as their parent. A DockLayout instance can then be created and
    applied to the dock area with the 'setDockLayout' method. The names
    in the DockLayoutItem objects are used to find the matching dock
    item widget child.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockArea.

        Parameters
        ----------
        parent : QWidget
            The parent of the dock area.

        """
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._overlays = DockOverlays(self)

        # FIXME temporary VS2010-like stylesheet
        from PyQt4.QtGui import QApplication
        QApplication.instance().setStyleSheet("""
            QDockArea {
                padding: 5px;
                background: rgb(41, 56, 85);
            }
            QDockItem {
                background: rgb(237, 237, 237);
            }
            QSplitter > QDockItem {
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border-bottom-left-radius: 2px;
                border-bottom-right-radius: 2px;
            }
            QDockTitleBar[p_titlePosition="2"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgb(78, 97, 132),
                            stop:0.5 rgb(66, 88, 124),
                            stop:1.0 rgb(64, 81, 124));
                color: rgb(250, 251, 254);

                border-top: 1px solid rgb(59, 80, 115);
            }
            QDockArea QDockTitleBar[p_titlePosition="2"] {
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QSplitterHandle {
                background: rgb(41, 56, 85);
            }
            """)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockLayout(self):
        """ Get the dock layout for the dock area.

        Returns
        -------
        result : DockLayoutBase or None
            The dock layout for the dock area, or None.

        """
        return self.layout().dockLayout()

    def setDockLayout(self, layout):
        """ Set the dock layout for the dock area.

        The old layout will be unparented and hidden, but not destroyed.

        Parameters
        ----------
        layout : DockLayoutBase
            The dock layout node to use for the dock area.

        """
        self.layout().setDockLayout(layout)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def hover(self, item, pos):
        """ Execute a hover operation for a dock item.

        This method is called by the docking framework as needed. It
        should not be called by user code.

        Parameters
        ----------
        item : QDockItem
            The dock item which is being hovered.

        pos : QPoint
            The global coordinates of the hover position.

        """
        local = self.mapFromGlobal(pos)
        if self.rect().contains(local):
            self._overlays.hover(local)
        else:
            self._overlays.hide()

    def endHover(self, item, pos):
        """ End a hover operation for a dock item.

        This method is called by the docking framework as needed. It
        should not be called by user code.

        Parameters
        ----------
        item : QDockItem
            The dock item which is being hovered.

        pos : QPoint
            The global coordinates of the hover position.

        """
        self._overlays.hide()

    def plug(self, item, pos):
        """ Plug a floating QDockItem back into the layout.

        This method is called by the docking framework as needed. It
        should not be called by user code.

        Parameters
        ----------
        item : QDockItem
            The dock item which is being hovered.

        pos : QPoint
            The global coordinates of the hover position.

        Returns
        -------
        result : bool
            True if the item was successfully plugged, False otherwise.

        """
        local = self.mapFromGlobal(pos)
        if self.rect().contains(local):
            layout = self.layout()
            mode = self._overlays._rose.mode()
            guide = self._overlays._rose.hitTest(local, mode)
            return layout.plug(item, local, guide)
        return False

    def unplug(self, item):
        """ Unplug a dock item from the dock area.

        This method is called by the framework when a QDockItem should
        be unplugged from the dock area. It should not be called by
        user code.

        Parameters
        ----------
        item : QDockItem
            The item to unplug from the dock area.

        """
        item.hide()
        self.layout().unplug(item)
