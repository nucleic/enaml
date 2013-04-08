#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QPoint, QRect
from PyQt4.QtGui import QFrame, QLayout, QRubberBand

from .dock_layout import DockLayoutItem, SplitDockLayout, TabbedDockLayout


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
        self._unplugRecursive(item, None, layout)

    def plugRect(self, pos):
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
        widget = self.parentWidget()
        m = widget.contentsMargins()
        corner = QPoint(widget.width(), widget.height())

        # Positions within 40 pixels of the boundary are treated with
        # priority for docking around the edges of the area.
        if pos.x() < 40 or pos.y() < 40:
            if pos.x() < pos.y():
                r = QRect(0, 0, corner.x() / 4, corner.y())
            else:
                r = QRect(0, 0, corner.x(), corner.y() / 4)
            return r.adjusted(m.left(), m.top(), -m.right(), -m.top())
        delta = corner - pos
        if delta.x() < 40 or delta.y() < 40:
            if delta.x() < delta.y():
                w = corner.x() / 4
                r = QRect(corner.x() - w, 0, w, corner.y())
            else:
                h = corner.y() / 4
                r = QRect(0, corner.y() - h, corner.x(), h)
            return r.adjusted(m.left(), m.top(), -m.right(), -m.top())
        return QRect()

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        layout = self._dock_layout
        if layout is not None:
            layout.setGeometry(rect)

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
        self._band = QRubberBand(QRubberBand.Rectangle, self)

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
            """)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _showDropSite(self, pos):
        band = self._band
        rect = self.layout().plugRect(pos)
        if rect.isValid():
            band.setGeometry(rect)
            if band.isHidden():
                band.show()
        else:
            if band.isVisible():
                band.hide()

    def _hideDropSite(self):
        band = self._band
        if band.isVisible():
            band.hide()

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

    def hover(self, pos):
        """ Returns the dock item at the given global position.

        """
        local = self.mapFromGlobal(pos)
        if self.rect().contains(self.mapToParent(local)):
            self._showDropSite(local)
        else:
            self._hideDropSite()
            # leaf = self.childAt(local)
            # while leaf is not None:
            #     if isinstance(leaf, QDockItem):
            #         self._showDropSite(leaf)
            #         return
            #     leaf = leaf.parent()

    def endHover(self, pos, item):
        self._hideDropSite()
        self._tryPlug(pos, item)

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
        flags = Qt.Tool | Qt.FramelessWindowHint
        item.setWindowFlags(flags)
        item.show()
        state.floating = True
