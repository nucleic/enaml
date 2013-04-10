#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect, QTimer
from PyQt4.QtGui import (
    QFrame, QLayout, QRubberBand, QPixmap, QWidget, QSplitter, QSplitterHandle
)

from atom.api import Atom, Int, Typed

from .dock_layout import DockLayoutItem, DockLayoutBase

from .q_guide_rose import QGuideRose


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
        self._dock_layout = None
        self._dock_guides = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _unplugRecursive(self, dock_item, parent, layout):
        """ A private method which unplugs the given dock item.

        """
        if isinstance(layout, DockLayoutItem):
            if layout.dock_item is dock_item:
                if parent is None:
                    self.setDockLayout(None)
                else:
                    parent.removeItem(layout)
                return True
            return False
        for sub_item in layout.items:
            if self._unplugRecursive(dock_item, layout, sub_item):
                if len(layout.items) == 0:
                    if parent is None:
                        self.setDockLayout(None)
                    else:
                        parent.removeItem(layout)
                elif len(layout.items) == 1 and parent is not None:
                    item = layout.items[0]
                    layout.releaseItem(item)
                    index = parent.items.index(layout)
                    #print 'trashing', layout
                    parent.removeItem(layout)
                    parent.insertItem(index, item)
                return True
        return False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockLayout(self):
        """ Get the dock layout for the layout area.

        Returns
        -------
        result : DockLayoutBase or None
            The dock layout for the layout area, or None.

        """
        return self._dock_layout

    def setDockLayout(self, layout):
        """ Set the dock layout for this layout area.

        The old layout will be unparented and hidden, but not destroyed.

        Parameters
        ----------
        layout : DockLayoutBase
            The dock layout node to use for the dock area.

        """
        old_layout = self._dock_layout
        if old_layout is not None:
            dock = old_layout.widget()
            dock.hide()
            dock.setParent(None)
        self._dock_layout = layout
        if layout is not None:
            layout.widget().setParent(self.parentWidget())
            if self._dock_guides:
                self._dock_guides.raise_()

    def unplug(self, item):
        """ Unplug a dock item from the layout.

        Parameters
        ----------
        item : QDockItem
            The dock item to unplug from the layout.

        """
        layout = self._dock_layout
        if layout is None:
            return
        self.parentWidget().setUpdatesEnabled(False)
        self._unplugRecursive(item, None, layout)
        self.parentWidget().setUpdatesEnabled(True)

    def pluggingRect(self, item, pos):
        """ Get the plugging rect at the given position.

        This can be useful for displaying a rubber band as potential
        dock site.

        Parameters
        ----------
        pos : QPoint
            The target point expressed in local coordinates of the
            dock area.

        Returns
        -------
        result : QRect
            A rect which represents the plug area. The rect will be
            invalid if the position does not indicate a valid area.

        """

    def dockHitTest(self, pos):
        """ Return the relevant widget under the point.

        """
        widget = self.parentWidget()
        if widget is None:
            return None
        layout = self._dock_layout
        if layout is None:
            return None

        # Hit test splitter handles
        splitters = widget.findChildren(QSplitter, 'dock_layout_splitter')
        for sp in splitters:
            pt = sp.mapFrom(widget, pos)
            for index in xrange(1, sp.count()):
                handle = sp.handle(index)
                rect = handle.rect().adjusted(-20, -20, 20, 20)
                if rect.contains(handle.mapFrom(sp, pt)):
                    return handle

        # Hit test dock items
        return layout.hitTest(pos)

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        layout = self._dock_layout
        if layout is not None:
            layout.setGeometry(rect)
        guides = self._dock_guides
        if guides is not None:
            p = self.parentWidget().mapToGlobal(QPoint(0, 0))
            guides.setGeometry(QRect(p, self.parentWidget().size()))
            #guides.updateMask()

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        layout = self._dock_layout
        if layout is not None:
            return layout.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size of the layout.

        """
        layout = self._dock_layout
        if layout is not None:
            return layout.minimumSize()
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
            h = 60 #owner.height() / 3
            s = QSize(owner.width() - m.left() - m.right(), h)
        elif guide_hit == Guide.BorderEast:
            w = 60 #owner.width() / 3
            p = QPoint(owner.width() - w - m.right(), m.top())
            s = QSize(w, owner.height() - m.top() - m.bottom())
        elif guide_hit == Guide.BorderSouth:
            h = 60 #owner.height() / 3
            p = QPoint(m.left(), owner.height() - h - m.bottom())
            s = QSize(owner.width() - m.left() - m.right(), h)
        elif guide_hit == Guide.BorderWest:
            p = QPoint(m.left(), m.top())
            w = 60 # owner.width() / 3
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
        dock_hit = self.layout().dockHitTest(pos)
        if isinstance(dock_hit, DockLayoutBase):
            target = dock_hit.widget()
            cpos = target.mapTo(self, QPoint(0, 0))
            cpos += QPoint(target.width() / 2, target.height() / 2)
            rose.update(cpos, Mode.Compass)
        elif isinstance(dock_hit, QSplitterHandle):
            if dock_hit.orientation() == Qt.Horizontal:
                mode = Mode.SplitHorizontal
            else:
                mode = Mode.SplitVertical
            cpos = dock_hit.mapTo(self, QPoint(0, 0))
            cpos += QPoint(dock_hit.width() / 2, dock_hit.height() / 2)
            rose.update(cpos, mode)
        else:
            rose.update(QPoint(), Mode.NoMode)

        # Make sure the rose is shown and hit test for the guide. Show
        # the rubber band for the appropriate guide hit.
        rose.show(self)
        guide_hit = rose.hover(pos)
        self._band.update(guide_hit, dock_hit, self)
        rose._rose.raise_()

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
        #item.show()
        state.floating = True
