#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QRect, QSize
from PyQt4.QtGui import QWidget, QLayout

from atom.api import Atom, Int, List, Enum, Range, ForwardTyped, Typed


class LayoutObject(Atom):

    #: A reference to the parent of this layout object.
    parent = ForwardTyped(lambda: LayoutObject)

    #: The rect occupied by the layout object. This rect is updated
    #: during the call to setGeometry.
    rect = Typed(QRect)

    #: Private storage for the size hint of the object. This is created
    #: and cached as needed.
    _size_hint = Typed(QSize)

    #: Private storage for the min size of the object. This is created
    #: and cached as needed.
    _minimum_size = Typed(QSize)

    #: Private storage for the vertical stretch of the object. This
    #: is created and cached as needed.
    _vertical_stretch = Int(-1)

    #: Private storage for the horizontal stretch of the object. This
    #: is created and cached as needed.
    _horizontal_stretch = Int(-1)

    def sizeHint(self):
        size = self._size_hint
        if size is None:
            size = self.doSizeHint()
            if not size.isValid():
                size = QSize(256, 192)
            self._size_hint = size
        return size

    def minimumSize(self):
        size = self._minimum_size
        if size is None:
            size = self.doMinimumSize()
            if not size.isValid():
                size = QSize(0, 0)
            self._minimum_size = size
        return size

    def verticalStretch(self):
        stretch = self._vertical_stretch
        if stretch < 0:
            stretch = self.doVerticalStretch()
            if stretch < 0:
                stretch = 0
            self._vertical_stretch = stretch
        return stretch

    def horizontalStretch(self):
        stretch = self._horizontal_stretch
        if stretch < 0:
            stretch = self.doHorizontalStretch()
            if stretch < 0:
                stretch = 0
            self._horizontal_stretch = stretch
        return stretch

    def invalidate(self):
        self._size_hint = None
        self._minimum_size = None
        self._vertical_stretch = -1
        self._horizontal_stretch = -1

    def setGeometry(self, rect):
        self.rect = rect

    def doSizeHint(self):
        raise NotImplementedError

    def doMinimumSize(self):
        raise NotImplementedError

    def doVerticalStretch(self):
        raise NotImplementedError

    def doHorizontalStretch(self):
        raise NotImplementedError


class LayoutItem(LayoutObject):

    #: The layout ring occupied by the item.
    ring = Range(low=0)

    #: The area occupied by the item within its ring.
    area = Enum('left', 'right', 'top', 'bottom')

    #: The index occupied by the item within its area.
    index = Range(low=0)

    #: The dock item being managed by the layout item. This value
    #: should never be None.
    dock_item = ForwardTyped(lambda: QDockItem)

    def setGeometry(self, rect):
        super(LayoutItem, self).setGeometry(rect)
        self.dock_item.setGeometry(rect)

    def doSizeHint(self):
        return self.dock_item.sizeHint()

    def doMinimumSize(self):
        return self.dock_item.minimumSizeHint()

    def doVerticalStretch(self):
        return self.dock_item.verticalStretch()

    def doHorizontalStretch(self):
        return self.dock_item.horizontalStretch()


class LayoutArea(LayoutObject):

    #: The layout ring occupied by the area.
    ring = Range(low=0)

    #: The area occupied by the area within its ring.
    area = Enum('left', 'right', 'top', 'bottom')

    #: The list of LayoutItem instances held by this area.
    layout_items = List()

    #: The list of QDockHandle widgets splitting the items.
    handles = List()

    def setGeometry(self, rect):
        pass

    def doSizeHint(self):
        layout_items = self.layout_items
        if not layout_items:
            return QSize()
        width = height = 0
        area = self.area
        if area == 'top' or area == 'bottom':
            for item in layout_items:
                size = item.sizeHint()
                width += size.width()
                height = max(height, size.height())
            for handle in self.handles:
                width += handle.sizeHint().width()
        else:
            for item in layout_items:
                size = item.sizeHint()
                height += size.height()
                width = max(width, size.width())
            for handle in self.handles:
                height += handle.sizeHint().height()
        return QSize(width, height)

    def doMinimumSize(self):
        layout_items = self.layout_items
        if not layout_items:
            return QSize()
        width = height = 0
        area = self.area
        if area == 'top' or area == 'bottom':
            for item in layout_items:
                size = item.minimumSize()
                width += size.width()
                height = max(height, size.height())
            for handle in self.handles:
                width += handle.minimumSizeHint().width()
        else:
            for item in layout_items:
                size = item.minimumSize()
                height += size.height()
                width = max(width, size.width())
            for handle in self.handles:
                height += handle.minimumSize().height()
        return QSize(width, height)

    def doVerticalStretch(self):
        layout_items = self.layout_items
        if not layout_items:
            return 0
        s = sum(item.verticalStretch() for item in layout_items)
        n = len(layout_items)
        if n > 1:
            s += 1
        return s / n

    def doHorizontalStretch(self):
        layout_items = self.layout_items
        if not layout_items:
            return 0
        s = sum(item.horizontalStretch() for item in layout_items)
        n = len(layout_items)
        if n > 1:
            s += 1
        return s / n


class LayoutRing(LayoutObject):

    #: The layout ring level occupied by this ring.
    ring = Range(low=0)

    top = Typed(LayoutArea)

    left = Typed(LayoutArea)

    right = Typed(LayoutArea)

    bottom = Typed(LayoutArea)

    top_handle = ForwardTyped(lambda: QDockHandle)

    left_handle = ForwardTyped(lambda: QDockHandle)

    right_handle = ForwardTyped(lambda: QDockHandle)

    bottom_handle = ForwardTyped(lambda: QDockHandle)

    child_layout_ring = ForwardTyped(lambda: LayoutRing)

    def setGeometry(self):
        pass

    def doSizeHint(self):
        width = height = 0
        child = self.child_layout_ring
        if child is not None:
            size = child.sizeHint()
            width += size.width()
            height += size.height()
        top = self.top
        if top is not None:
            size = top.sizeHint()
            height += size.height()
            width = max(width, size.width())
        top_handle = self.top_handle
        if top_handle is not None:
            height += top_handle.sizeHint().height()
        bottom = self.bottom
        if bottom is not None:
            size = bottom.sizeHint()
            height += size.height()
            width = max(width, size.width())
        bottom_handle = self.bottom_handle
        if bottom_handle is not None:
            height += bottom_handle.sizeHint().height()
        left = self.left
        if left is not None:
            size = left.sizeHint()
            width += size.width()
            height = max(height, size.height())
        left_handle = self.left_handle
        if left_handle is not None:
            width += left_handle.sizeHint().height()
        right = self.right
        if right is not None:
            size = right.sizeHint()
            width += size.width()
            height = max(height, size.height())
        right_handle = self.right_handle
        if right_handle is not None:
            width += right_handle.sizeHint().height()
        return QSize(width, height)

    def doMinimumSize(self):
        width = height = 0
        child = self.child_layout_ring
        if child is not None:
            size = child.minimumSize()
            width += size.width()
            height += size.height()
        top = self.top
        if top is not None:
            size = top.minimumSize()
            height += size.height()
            width = max(width, size.width())
        top_handle = self.top_handle
        if top_handle is not None:
            height += top_handle.minimumSizeHint().height()
        bottom = self.bottom
        if bottom is not None:
            size = bottom.minimumSize()
            height += size.height()
            width = max(width, size.width())
        bottom_handle = self.bottom_handle
        if bottom_handle is not None:
            height += bottom_handle.minimumSizeHint().height()
        left = self.left
        if left is not None:
            size = left.minimumSize()
            width += size.width()
            height = max(height, size.height())
        left_handle = self.left_handle
        if left_handle is not None:
            width += left_handle.minimumSizeHint().height()
        right = self.right
        if right is not None:
            size = right.minimumSize()
            width += size.width()
            height = max(height, size.height())
        right_handle = self.right_handle
        if right_handle is not None:
            width += right_handle.minimumSizeHint().height()
        return QSize(width, height)

    def doVerticalStretch(self):
        s = n = 0
        child = self.child_layout_ring
        if child is not None:
            pass

    def doHorizontalStretch(self):
        pass


class LayoutManager(LayoutObject):

    layout_ring = Typed(LayoutRing)

    def setGeometry(self, rect):
        super(LayoutManager, self).setGeometry(rect)

    def doSizeHint(self):
        pass

    def doMinimumSize(self):
        pass

    def addItem(self, item):
        pass

    def removeItem(self, item):
        pass


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
        #self._dock_root = DockLayoutRoot()

    def dockLayoutItem(self):
        """ Get the DockLayoutRoot object for the dock area.

        Returns
        -------
        result : DockLayoutRoot
            The dock layout root for the dock area.

        """
        return self._dock_root

    def setDockLayoutRoot(self, root):
        """ Set the DockLayoutRoot object for the dock area.

        Parameters
        ----------
        item : DockLayoutRoot
            The root dock layout root to use for the dock area.

        """
        #assert isinstance(root, DockLayoutItem)
        self._dock_root = root
        self.invalidate()

    def invalidate(self):
        """ A reimplemented virtual method which invalidates the layout.

        """
        root = self._dock_root
        if root is not None:
            root.invalidate()
        super(QDockAreaLayout, self).invalidate()

    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayoutItem` instead.

        """
        msg = 'Use `setDockLayoutItem` instead.'
        raise NotImplementedError(msg)

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        return None

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        root = self._dock_root
        if root is not None:
            root.setGeometry(rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        root = self._dock_root
        if root is not None:
            return root.sizeHint()


class QDockItem(QWidget):

    def __init__(self, parent=None):
        super(QDockItem, self).__init__(parent)
        self._title_bar = None

    def titleBarWidget(self):
        return self._title_bar

    def setTitleBarWidget(self, widget):
        self._title_bar = widget


class QDockArea(QWidget):

    def __init__(self, parent=None):
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())


class QDockHandle(QWidget):
    pass

