#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QLayout, QSplitter, QSplitterHandle, QTabWidget

from .dock_layout_visitors import (
    LayoutBuilder, LayoutSaver, LayoutHitTester, LayoutUnplugger
)
from .q_dock_item import QDockItem


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
        self._hit_tester = None
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
        return LayoutSaver.save(root)

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
        area = self.parentWidget()
        newroot = LayoutBuilder.build(layout, area)
        if newroot is not None:
            newroot.setParent(area)
            if not area.isHidden():
                newroot.show()
        self._root = newroot
        self._hit_tester = None

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
        root = self._root
        if root is None:
            return
        if container is root:
            container.hide()
            container.setParent(None)
            self._root = None
            self._hit_tester = None
            return
        success, replace = LayoutUnplugger.unplug(root, container)
        if success:
            self._hit_tester = None
            if replace is not None:
                self._root = replace
                replace.setParent(self.parentWidget())
                replace.show()

    def hitTest(self, pos):
        """ Hit test the layout for a relevant widget under a point.

        Parameters
        ----------
        pos : QPoint
            The point of interest, expressed in the local coordinate
            system of the layout parent widget.

        Returns
        -------
        result : QWidget or None
            A widget which is relevant for docking purposes, or None
            if no such widget was found under the point. If the hit
            test is successful, the result will be a QDockContainer,
            QSplitterHandler, or QTabWidget.

        """
        tester = self._hit_tester
        if tester is None:
            root = self._root
            if root is None:
                return
            tester = self._hit_tester = LayoutHitTester.from_widget(root)
        return tester.hit_test(self.parentWidget(), pos)

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        root = self._root
        if root is not None:
            root.setGeometry(self.contentsRect())

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
        msg = 'Use `setDockLayout` instead.'
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
