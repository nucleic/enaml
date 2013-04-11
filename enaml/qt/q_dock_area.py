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

from atom.api import Atom, Int, Typed

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


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


ORIENTATION = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


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
        self._splitters = []
        self._items = set()
        self._tabs = []

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _buildLayoutRecursive(self, state):
        dock_items = self._items
        widget = self.parentWidget()

        if isinstance(state, TabbedLayout):
            found = []
            for item in state.items:
                child = widget.findChild(QDockItem, item.name)
                if child is not None and child not in dock_items:
                    found.append(child)
                    dock_items.add(child)
            if len(found) == 0:
                return None
            if len(found) == 1:
                return found[0]
            tw = QTabWidget()
            self._tabs.append(tw)
            tw.setTabBar(QDockTabBar())
            tw.setMovable(state.tabs_movable)
            tw.setDocumentMode(DOCUMENT_MODES[state.tab_style])
            tw.setTabPosition(TAB_POSITIONS[state.tab_position])
            for child in found:
                child.titleBarWidget().hide()
                tw.addTab(child, child.title())
            return tw

        if isinstance(state, SplitLayout):
            found = []
            for item in state.items:
                if isinstance(item, DockLayoutItem):
                    child = widget.findChild(QDockItem, item.name)
                    if child is not None and child not in dock_items:
                        found.append(child)
                        dock_items.add(child)
                else:
                    child = self._buildLayoutRecursive(item)
                    if child is not None:
                        found.append(child)
            if len(found) == 0:
                return None
            if len(found) == 1:
                return found[0]
            sp = QSplitter()
            self._splitters.append(sp)
            sp.setOrientation(ORIENTATION[state.orientation])
            for child in found:
                sp.addWidget(child)
            return sp

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockState(self):
        """ Get the current layout state for the layout.

        Returns
        -------
        result : DockLayout or None
            An Enaml DockLayout object for the current layout state, or
            None if the area has no docked items.

        """
        return None

    def setDockState(self, state):
        """ Set the layout state for the layout.

        Parameters
        ----------
        state : DockLayout
            The DockLayout state object which describes the layout to
            be assembled.

        """
        root = self._root
        if root is not None:
            root.hide()
            root.set_parent(None)
        newroot = self._buildLayoutRecursive(state)
        if newroot is not None:
            newroot.setParent(self.parentWidget())
            if not self.parentWidget().isHidden():
                newroot.show()
        print newroot
        self._root = newroot

    def unplug(self, item):
        """ Unplug a dock item from the layout.

        Parameters
        ----------
        item : QDockItem
            The dock item to unplug from the layout.

        """
        parent = item.parentWidget()
        item.setParent(None)
        while True:
            if parent is None:
                self._root = None
                return
            if isinstance(parent, (QSplitter, QTabWidget)):
                count = parent.count()
                if count > 1:
                    return
                temp = parent.parent()
                if count == 0:
                    if temp is None:
                        self._root = None
                    parent.setParent(None)
                else:
                    child = parent.widget(0)
                    if temp is None:
                        child.setParent(None)
                        self._root = None
                    elif temp is self.parentWidget():
                        child.setParent(self.parentWidget())
                        child.show()
                        self._root = child
                        parent.setParent(None)
                    else:
                        index = temp.indexOf(parent)
                        parent.setParent(None)
                        temp.insertWidget(index, child)
                parent = temp
            else:
                break
        # layout = self._dock_layout
        # if layout is None:
        #     return
        # self.parentWidget().setUpdatesEnabled(False)
        # self._unplugRecursive(item, None, layout)
        # self.parentWidget().setUpdatesEnabled(True)

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
        for tb in self._tabs:
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


class RoseManager(Atom):
    """ An object which assists in managing a QGuideRose.

    """
    #: The rose object being managed; created on-demand.
    _rose = Typed(QGuideRose, ())

    #: The target mode to apply to the rose on timeout.
    _target_mode = Int(QGuideRose.Mode.NoMode)

    #: The timer for changing the state of the rose.
    _timer = Typed(QTimer)

    #--------------------------------------------------------------------------
    # Default Value Methods
    #--------------------------------------------------------------------------
    def _default__timer(self):
        """ Create the timer for this rose manager.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_timer)
        return timer

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _on_timer(self):
        """ Handle the timeout event for the internal timer.

        """
        self._rose.setMode(self._target_mode)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def show(self, owner):
        """ Ensure the rose is visible and sized on the screen.

        Parameters
        ----------
        owner : QWidget
            The widget over which the rose should be shown.

        """
        if self._rose.isHidden():
            g = owner.mapToGlobal(QPoint(0, 0))
            self._rose.setGeometry(QRect(g, owner.size()))
            self._rose.show()

    def hide(self):
        """ Ensure the rose is hidden from the screen.

        """
        if not self._rose.isHidden():
            self._rose.hide()

    def hitTest(self, pos):
        """ Hit test the rose.

        Parameters
        ----------
        pos : QPoint
            The mouse position to hit test.

        Returns
        -------
        result : QGuideRose.Guide
            The enum value for the hit guide.

        """
        return self._rose.hitTest(pos)

    def hover(self, pos):
        """ Peform a hover event on the rose.

        Parameters
        ----------
        pos : QPoint
            The mouse position to hit test.

        Returns
        -------
        result : QGuideRose.Guide
            The enum value for the hit guide.

        """
        return self._rose.hover(pos)

    def update(self, pos, mode):
        """ Update the rose with a new center position and mode.

        Parameters
        ----------
        pos : QPoint
            The center position to apply to the rose.

        mode : QGuideRose.Mode
            The mode to apply to the rose.

        """
        if mode == QGuideRose.Mode.NoMode:
            self._timer.stop()
            self._rose.setMode(mode)
        elif mode != self._rose.mode():
            self._rose.setMode(QGuideRose.Mode.NoMode)
            self._target_mode = mode
            self._timer.start(30)
        self._rose.setCenter(pos)


class BandManager(Atom):

    #: The rose object being managed; created on-demand.
    _band = Typed(QRubberBand, (QRubberBand.Rectangle,))

    #: The target mode to apply to the rose on timeout.
    _target_geo = Typed(QRect, factory=lambda: QRect())

    #: The timer for changing the state of the rose.
    _timer = Typed(QTimer)

    #--------------------------------------------------------------------------
    # Default Value Methods
    #--------------------------------------------------------------------------
    def _default__timer(self):
        """ Create the timer for this rose manager.

        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_timer)
        return timer

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _on_timer(self):
        """ Handle the timeout event for the internal timer.

        """
        if self._target_geo.isValid():
            self._band.setGeometry(self._target_geo)
            self._band.show()
        else:
            self._band.hide()

    def show(self):
        """ Ensure the rose is visible and sized on the screen.

        Parameters
        ----------
        owner : QWidget
            The widget over which the rose should be shown.

        """
        if self._band.isHidden():
            self._band.setGeometry(self._target_geo)
            self._band.show()

    def hide(self):
        """ Ensure the rose is hidden from the screen.

        """
        self._timer.stop()
        if not self._band.isHidden():
            self._band.hide()

    def update(self, guide_hit, dock_hit, owner):
        """ Update the geometry of the rect.

        """
        Guide = QGuideRose.Guide
        if guide_hit == Guide.NoGuide:
            r = QRect()
            if self._target_geo != r:
                self._target_geo = QRect()
                self._timer.start(50)
            return

        # Border hits
        m = owner.contentsMargins()
        if guide_hit == Guide.BorderNorth:
            p = QPoint(m.left(), m.top())
            h = 60  # owner.height() / 3
            s = QSize(owner.width() - m.left() - m.right(), h)
        elif guide_hit == Guide.BorderEast:
            w = 60  # owner.width() / 3
            p = QPoint(owner.width() - w - m.right(), m.top())
            s = QSize(w, owner.height() - m.top() - m.bottom())
        elif guide_hit == Guide.BorderSouth:
            h = 60  # owner.height() / 3
            p = QPoint(m.left(), owner.height() - h - m.bottom())
            s = QSize(owner.width() - m.left() - m.right(), h)
        elif guide_hit == Guide.BorderWest:
            p = QPoint(m.left(), m.top())
            w = 60  # owner.width() / 3
            s = QSize(w, owner.height() - m.top() - m.bottom())

        # Compass Hits
        elif guide_hit == Guide.CompassNorth:
            w = dock_hit.widget()
            p = w.mapTo(owner, QPoint(0, 0))
            s = w.size()
            s.setHeight(s.height() / 3)
        elif guide_hit == Guide.CompassEast:
            w = dock_hit.widget()
            p = w.mapTo(owner, QPoint(0, 0))
            s = w.size()
            d = s.width() / 3
            r = s.width() - d
            s.setWidth(d)
            p.setX(p.x() + r)
        elif guide_hit == Guide.CompassSouth:
            w = dock_hit.widget()
            p = w.mapTo(owner, QPoint(0, 0))
            s = w.size()
            d = s.height() / 3
            r = s.height() - d
            s.setHeight(d)
            p.setY(p.y() + r)
        elif guide_hit == Guide.CompassWest:
            w = dock_hit.widget()
            p = w.mapTo(owner, QPoint(0, 0))
            s = w.size()
            s.setWidth(s.width() / 3)
        elif guide_hit == Guide.CompassCenter:
            w = dock_hit.widget()
            p = w.mapTo(owner, QPoint(0, 0))
            s = w.size()

        # Splitter
        elif guide_hit == Guide.SplitHorizontal:
            p = dock_hit.mapTo(owner, QPoint(0, 0))
            wo, r = divmod(60 - dock_hit.width(), 2)
            wo += r
            p.setX(p.x() - wo)
            s = QSize(2 * wo + dock_hit.width(), dock_hit.height())
        elif guide_hit == Guide.SplitVertical:
            p = dock_hit.mapTo(owner, QPoint(0, 0))
            ho, r = divmod(60 - dock_hit.height(), 2)
            ho += r
            p.setY(p.y() - ho)
            s = QSize(dock_hit.width(), 2 * ho + dock_hit.height())

        # Default no-op
        else:
            s = QSize()
            p = QPoint()

        p = owner.mapToGlobal(p)
        geo = QRect(p, s)
        if geo != self._target_geo:
            self._target_geo = geo
            self._timer.start(50)


class QDockArea(QFrame):

    def __init__(self, parent=None):
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._band = BandManager()
        self._rose = RoseManager()

        # FIXME temporary VS2010-like stylesheet
        from PyQt4.QtGui import QApplication
        QApplication.instance().setStyleSheet("""
            QDockArea {
                padding: 5px;
                background: rgb(41, 56, 85);
            }
            QDockItem {
                background: rgb(237, 237, 237);
                border-bottom-left-radius: 2px;
                border-bottom-right-radius: 2px;
            }
            QSplitter > QDockItem {
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
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
    # Private API
    #--------------------------------------------------------------------------
    def _showDropSite(self, item, pos):
        rose = self._rose
        Mode = QGuideRose.Mode
        # dock_hit = self.layout().dockHitTest(pos)
        # if isinstance(dock_hit, DockLayoutBase):
        #     target = dock_hit.widget()
        #     cpos = target.mapTo(self, QPoint(0, 0))
        #     cpos += QPoint(target.width() / 2, target.height() / 2)
        #     rose.update(cpos, Mode.Compass)
        # elif isinstance(dock_hit, QSplitterHandle):
        #     if dock_hit.orientation() == Qt.Horizontal:
        #         mode = Mode.SplitHorizontal
        #     else:
        #         mode = Mode.SplitVertical
        #     cpos = dock_hit.mapTo(self, QPoint(0, 0))
        #     cpos += QPoint(dock_hit.width() / 2, dock_hit.height() / 2)
        #     rose.update(cpos, mode)
        # else:
        #     rose.update(QPoint(), Mode.NoMode)

        # # Make sure the rose is shown and hit test for the guide. Show
        # # the rubber band for the appropriate guide hit.
        # rose.show(self)
        # guide_hit = rose.hover(pos)
        # self._band.update(guide_hit, dock_hit, self)
        # rose._rose.raise_()

    def _hideDropSite(self):
        self._rose.hide()
        self._band.hide()

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
        return self.layout().dockState()

    def setDockLayout(self, layout):
        """ Set the dock layout for the dock area.

        The old layout will be unparented and hidden, but not destroyed.

        Parameters
        ----------
        layout : DockLayoutBase
            The dock layout node to use for the dock area.

        """
        self.layout().setDockState(layout)

    def hover(self, item, pos, modifiers):
        """ Returns the dock item at the given global position.

        """
        local = self.mapFromGlobal(pos)
        if self.rect().contains(self.mapToParent(local)):
            self._showDropSite(item, local)
        else:
            self._hideDropSite()

    def endHover(self, item, pos, modifiers):
        self._hideDropSite()
        #self._tryPlug(pos, item)

    def _tryPlug(self, pos, item):
        local = self.mapFromGlobal(pos)
        if local.x() > 0 and local.x() < 40:
            item.setWindowFlags(Qt.Widget)
            dock_layout = self.layout().dockLayout()
            dock_layout.insertItem(0, item._dock_state.layout)
            item._dock_state.floating = False

    def unplug(self, item):
        """ Unplug a dock item from the dock area.

        This method is called by the framework when a QDockItem should
        be unplugged from the dock area. It should not typically be
        called directly by user code.

        Parameters
        ----------
        item : QDockItem
            The item to unplug from the dock area.

        """
        state = item._dock_state
        if state.floating:
            return
        item.hide()
        self.layout().unplug(item)
        item.setParent(self)
        flags = Qt.Window | Qt.FramelessWindowHint
        item.setWindowFlags(flags)
        state.floating = True
