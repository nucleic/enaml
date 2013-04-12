#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect, QTimer, QPropertyAnimation
from PyQt4.QtGui import (
    QFrame, QLayout, QRubberBand, QSplitter, QSplitterHandle, QStackedWidget,
    QTabWidget
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
        self._splitters = set()
        self._items = set()
        self._root = None
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
        dock_items = self._items
        widget = self.parentWidget()
        for item in items:
            if isinstance(item, DockLayoutItem):
                child = widget.findChild(QDockItem, item.name)
                if child is not None and child not in dock_items:
                    resolved.append(child)
                    dock_items.add(child)
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
        if isinstance(layout, (SplitLayout, TabbedLayout)):
            items = self._resolveItems(layout.items)
            n = len(items)
            if n <= 1:
                return None if n == 0 else items[0]
            if isinstance(layout, SplitLayout):
                widget = self._createSplitter(ORIENTATION[layout.orientation])
                for child in items:
                    widget.addWidget(child)
            else:
                doc_mode = DOCUMENT_MODES[layout.tab_style]
                movable = layout.tabs_movable
                tab_pos = TAB_POSITIONS[layout.tab_position]
                widget = self._createTabWidget(doc_mode, movable, tab_pos)
                for child in items:
                    child.titleBarWidget().hide()
                    widget.addTab(child, child.title())
            return widget
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
        if isinstance(item, (QSplitter, QTabWidget)):
            kids = []
            for index in item.count():
                child = self._snapLayout(item.widget(index))
                if child is not None:
                    kids.append(child)
            if isinstance(item, QSplitter):
                orient = ORIENTATION_INV[item.orientation()]
                res = SplitLayout(*kids, orientation=orient)
            else:
                mode = DOCUMENT_MODES_INV[item.documentMode()]
                pos = TAB_POSITIONS_INV[item.tabPosition()]
                res = TabbedLayout(*kids, tab_style=mode, tab_position=pos)
            return res

    def _cleanupContainer(self, container):
        """ Cleanup the layout container.

        Cleanup the container such that it is removed from the layout
        if it contains one item or less. This operation is recursive
        and traverses up the widget hierarchy.

        Parameters
        ----------
        container : QSplitter, QStackWidget, or QTabWidget
            The layout container to cleanup. A QStackWidget is valid
            because it will be the *actual* parent of a QDockItem
            when added to a QTabWidget.

        """
        if isinstance(container, QStackedWidget):
            container = container.parent()
        count = container.count()
        if count <= 1:
            self._splitters.discard(container)
            self._tab_widgets.discard(container)
            parent = container.parent()
            if count == 0:
                container.hide()
                container.setParent(None)
                if container is self._root:
                    self._root = None
                else:
                    self._cleanupContainer(parent)
            else:
                child = container.widget(0)
                if container is self._root:
                    self._root = child
                    container.hide()
                    container.setParent(None)
                    child.setParent(self.parentWidget())
                    if not self.parentWidget().isHidden():
                        child.show()
                else:
                    index = parent.indexOf(container)
                    container.hide()
                    container.setParent(None)
                    parent.insertWidget(index, child)
                if isinstance(container, QTabWidget):
                    child.titleBarWidget().show()

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
        self._tab_widgets.clear()
        self._splitters.clear()
        self._items.clear()
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

    def unplug(self, item):
        """ Unplug a dock item from the layout.

        Parameters
        ----------
        item : QDockItem
            The dock item to unplug from the layout.

        """
        if item in self._items:
            item.hide()
            self._items.remove(item)
            if item is self._root:
                self._root = None
                item.setParent(None)
            else:
                parent = item.parent()
                if parent is not None:
                    item.setParent(None)
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


class DockOverlays(Atom):
    """ An object which manages the overlays for a QDockArea.

    This manager handles the state transitions for the overlays. The
    transitions are performed on a slightly-delayed timer to provide
    a more fluid user interaction experience.

    """
    #: The size of the rubber band when docking on the border, in px.
    BORDER_DOCK_SIZE = 60

    #: The delay to use when triggering the rose timer, in ms.
    ROSE_DELAY = 30

    #: The delay to use when triggering the band timer, in ms.
    BAND_DELAY = 50

    #: The target opacity to use when making the band visible.
    BAND_TARGET_OPACITY = 0.6

    #: The duration of the band visibilty animation, in ms.
    BAND_VIS_DURATION = 100

    #: the duration of the band geometry animation, in ms.
    BAND_GEO_DURATION = 100

    #: The dock area owner of the overlays.
    _owner = ForwardTyped(lambda: QDockArea)

    #: The overlayed guide rose.
    _rose = Typed(QGuideRose, ())

    #: The overlayed rubber band.
    _band = Typed(QRubberBand, (QRubberBand.Rectangle,))

    #: The property animator for the rubber band geometry.
    _geo_animator = Typed(QPropertyAnimation)

    #: The property animator for the rubber band visibility.
    _vis_animator = Typed(QPropertyAnimation)

    #: The target mode to apply to the rose on timeout.
    _target_rose_mode = Int(QGuideRose.Mode.NoMode)

    #: The target geometry to apply to rubber band on timeout.
    _target_band_geo = Typed(QRect, factory=lambda: QRect())

    #: The queued band geo.
    _queued_band_geo = Typed(QRect)

    #: The value of the last guide which was hit in the rose.
    _last_guide = Int(-1)

    #: The hover position of the mouse to use for state changes.
    _hover_pos = Typed(QPoint)

    #: The timer for changing the state of the rose.
    _rose_timer = Typed(QTimer)

    #: The timer for changing the state of the band.
    _band_timer = Typed(QTimer)

    def __init__(self, owner):
        """ Initialize a DockOverlays instance.

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
        """ Create the default timer for the rose state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_rose_timer)
        return timer

    def _default__band_timer(self):
        """ Create the default timer for the band state changes.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_band_timer)
        return timer

    def _default__geo_animator(self):
        """ Create the default property animator for the rubber band.

        """
        p = QPropertyAnimation(self._band, 'geometry')
        p.setDuration(self.BAND_GEO_DURATION)
        return p

    def _default__vis_animator(self):
        """ Create the default property animator for the rubber band.

        """
        p = QPropertyAnimation(self._band, 'windowOpacity')
        p.setDuration(self.BAND_VIS_DURATION)
        p.finished.connect(self._on_vis_finished)
        return p

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
        self._update_band_state()

    def _on_band_timer(self):
        """ Handle the timeout event for the internal band timer.

        This handler updates the position of the rubber band.

        """
        self._update_band_state()

    #--------------------------------------------------------------------------
    # Animation Handlers
    #--------------------------------------------------------------------------
    def _on_vis_finished(self):
        """ Handle the 'finished' signal from the visibility animator.

        This handle will hide the rubber band when its opacity is 0.

        """
        band = self._band
        if band.windowOpacity() == 0.0:
            band.hide()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_band_state(self):
        """ Refresh the geometry and visible state of the rubber band.

        The state will be updated using animated properties to provide
        a nice fluid user experience.

        """
        # A valid geometry indicates that the rubber should be shown on
        # the screen. An invalid geometry means it should be hidden. If
        # the validity is changed during animation, the animators are
        # restarted using the current state as their starting point.
        band = self._band
        geo = self._target_band_geo
        if geo.isValid():
            # If the band is already hidden, the geometry animation can
            # be bypassed since the band can be located anywhere. The
            # rose must be raised because QRubberBand raises itself
            # when it receives a showEvent.
            if band.isHidden():
                band.setGeometry(geo)
                self._start_vis_animator(self.BAND_TARGET_OPACITY)
                self._rose.raise_()
                return
            self._start_vis_animator(self.BAND_TARGET_OPACITY)
            self._start_geo_animator(geo)
        else:
            self._start_vis_animator(0.0)

    def _start_vis_animator(self, opacity):
        """ (Re)start the visibility animator.

        Parameters
        ----------
        opacity : float
            The target opacity of the target object.

        """
        animator = self._vis_animator
        if animator.state() == animator.Running:
            animator.stop()
        target = animator.targetObject()
        if target.isHidden() and opacity != 0.0:
            target.setWindowOpacity(0.0)
            target.show()
        animator.setStartValue(target.windowOpacity())
        animator.setEndValue(opacity)
        animator.start()

    def _start_geo_animator(self, geo):
        """ (Re)start the visibility animator.

        Parameters
        ----------
        geo : QRect
            The target geometry for the target object.

        """
        animator = self._geo_animator
        if animator.state() == animator.Running:
            animator.stop()
        target = animator.targetObject()
        animator.setStartValue(target.geometry())
        animator.setEndValue(geo)
        animator.start()

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
        border_size = self.BORDER_DOCK_SIZE
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

    def hit_test_rose(self, pos):
        """ Hit test the guide rose for the given position.

        The hit test is performed using the current rose mode.

        Parameters
        ----------
        pos : QPoint
            The position to hit test, expressed in the coordinate
            system of the owner dock area.

        Returns
        -------
        result : QGuideRose.Guide
            The guide enum which lies under the given point.

        """
        rose = self._rose
        return rose.hitTest(pos, rose.mode())

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
        # No hit testing is necessary when using the single center mode.
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
                self._band_timer.start(self.BAND_DELAY)
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
        # the current mode, the rose is hidden and the state change
        # is collapsed on a timer.
        self._hover_pos = pos
        self._target_rose_mode = target_mode
        if target_mode == Mode.NoMode:
            self._rose_timer.stop()
            rose.setMode(target_mode)
        elif target_mode != rose.mode():
            rose.setMode(Mode.NoMode)
            self._rose_timer.start(self.ROSE_DELAY)
        rose.setCenter(center)

        # Hit test the rose and update the target geometry for the
        # rubber band if the target guide has changed.
        update_band = False
        guide = rose.hitTest(pos, target_mode)
        if guide != self._last_guide:
            self._last_guide = guide
            self._target_band_geo = self._band_geometry(guide, widget)
            update_band = True

        # If the rose is currently visible, pass it the hover event so
        # that it can trigger a repaint of the guides if needed. Queue
        # an update for the band geometry which prevents the band from
        # flickering when rapidly cycling between guide pads.
        if rose.mode() != Mode.NoMode:
            rose.hover(pos)
            if update_band:
                self._band_timer.start(self.BAND_DELAY)

        # Ensure that the rose is shown on the screen.
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
            QSplitter > QDockItem, QDockArea > QDockItem, QDockItemWindow > QDockItem {
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
            QDockItemWindow {
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
            The dock item which should be plugged into the area.

        pos : QPoint
            The global coordinates of the hover position.

        Returns
        -------
        result : bool
            True if the item was successfully plugged, False otherwise.

        """
        local = self.mapFromGlobal(pos)
        if self.rect().contains(local):
            guide = self._overlays.hit_test_rose(local)
            return self.layout().plug(item, local, guide)
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
        self.layout().unplug(item)
