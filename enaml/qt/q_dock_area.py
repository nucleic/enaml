#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect
from PyQt4.QtGui import QFrame, QLayout, QRubberBand, QPixmap, QWidget, QSplitterHandle

from .dock_layout import DockLayoutItem, SplitDockLayout, TabbedDockLayout

from .q_dock_guides import QDockGuides


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
        # dock_layout = self._dock_layout
        # dock_area = self.parentWidget()
        # area_width = dock_area.width()
        # area_height = dock_area.height()
        # margins = dock_area.contentsMargins()

        # # If there is nothing in the layout. The plugging rect is the
        # # entire dock area.
        # if dock_layout is None:
        #     rect = QRect(0, 0, area_width, area_height).adjusted(
        #         margins.left(), margins.top(),
        #         -margins.right(), -margins.bottom()
        #     )
        #     return rect



        # # Positions within 40 pixels of the boundary are treated with
        # # priority for docking around the edges of the area.
        # pw = 0.3 * widget.width()
        # ph = 0.3 * widget.height()

        # if pos.x() < 20 or pos.y() < 20:
        #     if pos.x() < pos.y():
        #         height = widget.height() - m.top() - m.bottom()
        #         rect = QRect(m.left(), m.top(), pw, height)
        #     else:
        #         width = widget.width() - m.left() - m.right()
        #         rect = QRect(m.left(), m.top(), width, ph)
        #     return rect
        # delta = corner - pos
        # if delta.x() < 20 or delta.y() < 20:
        #     if delta.x() < delta.y():
        #         r = QRect(corner.x() - pw + m.left(), m.top(), pw, corner.y())
        #     else:
        #         r = QRect(0, corner.y() - ph, corner.x(), ph)
        #     return r.adjusted(m.left(), m.top(), -m.right(), -m.bottom())

        # # Find the dock item or splitter handle that is being hovered.
        # target = None
        # leaf = widget.childAt(pos)
        # from .q_dock_item import QDockItem
        # from PyQt4.QtGui import QSplitterHandle
        # while leaf is not None:
        #     if isinstance(leaf, (QDockItem, QSplitterHandle)):
        #         target = leaf
        #         break
        #     leaf = leaf.parent()

        # if isinstance(target, QSplitterHandle):
        #     o = target.mapTo(widget, QPoint(0, 0))
        #     if target.orientation() == Qt.Horizontal:
        #         return QRect(o.x() - 20, o.y(), target.width() + 40, target.height())
        #     return QRect(o.x(), o.y() - 20, target.width(), target.height() + 40)

        # if isinstance(target, QDockItem):
        #     p = target._dock_state.layout.parent
        #     if isinstance(p, TabbedDockLayout):
        #         target = p.widget()
        #     origin = target.mapTo(widget, QPoint(0, 0))
        #     h_frac = (pos.y() - origin.y()) / float(target.height())
        #     w_frac = (pos.x() - origin.x()) / float(target.width())
        #     h_frac2 = 1.0 - h_frac
        #     w_frac2 = 1.0 - w_frac
        #     quads = [(w_frac, 0), (h_frac, 1), (w_frac2, 2), (h_frac2, 3)]
        #     quads.sort()
        #     qf, q = quads[0]
        #     if qf < 0.3:
        #         if q == 0 and qf * target.width() > 5:
        #             w = 0.3 * target.width()
        #             r = QRect(origin.x(), origin.y(), w, target.height())
        #         elif q == 1 and qf * target.height() > 5:
        #             h = 0.3 * target.height()
        #             r = QRect(origin.x(), origin.y(), target.width(), h)
        #         elif q == 2 and qf * target.width() > 5:
        #             w = 0.3 * target.width()
        #             r = QRect(origin.x() + target.width() - w, origin.y(), w, target.height())
        #         elif q == 3 and qf * target.height() > 5:
        #             h = 0.3 * target.height()
        #             r = QRect(origin.x(), origin.y() + target.height() - h, target.width(), h)
        #         else:
        #             r = QRect()
        #         return r
        #     return QRect(origin.x(), origin.y(), target.width(), target.height())

        # return QRect()

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


class QDockArea(QFrame):

    def __init__(self, parent=None):
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._band = QRubberBand(QRubberBand.Rectangle)
        self._dock_guides = QDockGuides()

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
        guides = self._dock_guides
        needshow = guides.isHidden()
        if needshow:
            gpos = self.mapToGlobal(QPoint(0, 0))
            guides.setGeometry(QRect(gpos, self.size()))

        target = None
        handle = None
        leaf = self.childAt(pos)
        from .q_dock_item import QDockItem
        while leaf is not None:
            if isinstance(leaf, QDockItem):
                target = leaf
                break
            elif isinstance(leaf, QSplitterHandle):
                handle = leaf
                break
            leaf = leaf.parent()
        if target is not None:
            cpos = target.mapTo(self, QPoint(0, 0))
            cpos += QPoint(target.width() / 2, target.height() / 2)
            guides.setGuideCenter(cpos)
        if handle is not None:
            p = handle.mapToGlobal(QPoint(0, 0))
            s = handle.size()
            if handle.orientation() == Qt.Horizontal:
                p -= QPoint(20, 0)
                s += QSize(40, 0)
            else:
                p -= QPoint(0, 20)
                s += QSize(0, 40)
            self._band.setGeometry(QRect(p, s))
            self._band.show()

        if needshow:
            guides.show()

        guides.hover(pos)

    def _hideDropSite(self):
        guides = self._dock_guides
        if not guides.isHidden():
            guides.hide()
            guides.setGuideCenter(QPoint())
        #band = self._band
        #if band.isVisible():
        #    band.hide()

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
        item.show()
        state.floating = True
