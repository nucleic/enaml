#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QSize, QPoint
from PyQt4.QtGui import QWidget, QFrame, QLayout, QSplitter, QApplication

from atom.api import (
    Atom, Constant, Int, List, Enum, Range, ForwardTyped, Typed, Value,
    DefaultValue, Bool,
)

from casuarius import ConstraintVariable, Solver, medium


NoCorners = 0x0
TopLeftCorner = 0x1
TopRightCorner = 0x2
BottomLeftCorner = 0x4
BottomRightCorner = 0x8


class ConstraintMember(Constant):
    """ A custom Member class that generates a ConstraintVariable.

    """
    __slots__ = ()

    def __init__(self):
        super(ConstraintMember, self).__init__()
        mode = DefaultValue.MemberMethod_Object
        self.set_default_value_mode(mode, "default")

    def default(self, owner):
        """ Create the constraint variable for the member.

        """
        return ConstraintVariable(self.name)


class LayoutBase(Atom):
    """ A base class for the dock layout classes.

    """
    #: A reference to the parent node for the item.
    parent = ForwardTyped(lambda: LayoutBase)

    #: A reference to the QDockAreaLayout which owns the item.
    layout = ForwardTyped(lambda: QDockAreaLayout)

    #: The cached size hint for the layout item.
    size_hint = Typed(QSize)

    #: The cached minimum size for the layout item.
    min_size = Typed(QSize)

    #: The cached vertical stretch for the layout item.
    v_stretch = Int(-1)

    #: The cached horizontal stretch for the layout item.
    h_stretch = Int(-1)

    x = ConstraintMember()

    y = ConstraintMember()

    width = ConstraintMember()

    height = ConstraintMember()

    right = Constant()

    def _default_right(self):
        return self.x + self.width

    bottom = Constant()

    def _default_bottom(self):
        return self.y + self.height

    def invalidate(self):
        """ Invalidate the cached size data for the layout item.

        """
        del self.size_hint
        del self.min_size
        del self.v_stretch
        del self.h_stretch
        parent = self.parent
        if parent is not None:
            parent.invalidate()

    def sizeHint(self):
        """ Get the size hint of the layout item.

        """
        hint = self.size_hint
        if hint is None:
            hint = self.size_hint = self.doSizeHint()
        return hint

    def minimumSize(self):
        """ Get the minimum size of the layout item.

        """
        size = self.min_size
        if size is None:
            size = self.min_size = self.doMinimumSize()
        return size

    def verticalStretch(self):
        """ Get the vertical stretch factor for the layout item.

        """
        stretch = self.v_stretch
        if stretch == -1:
            stretch = self.v_stretch = self.doVerticalStretch()
        return stretch

    def horizontalStretch(self):
        """ Get the vertical stretch factor for the layout item.

        """
        stretch = self.h_stretch
        if stretch == -1:
            stretch = self.h_stretch = self.doHorizontalStretch()
        return stretch

    def doSizeHint(self):
        """ Compute and return the size hint for the layout item.

        """
        raise NotImplementedError

    def doMinimumSize(self):
        """ Compute and return the minimum size for the layout item.

        """
        raise NotImplementedError

    def doVerticalStretch(self):
        """ Compute and return the vertical stretch for the item.

        """
        raise NotImplementedError

    def doHorizontalStretch(self):
        """ Compute and return the vertical stretch for the item.

        """
        raise NotImplementedError


class LayoutArea(LayoutBase):
    """ A class which implements the layout for an area within a ring.

    """
    #: The ring address in which this area lives.
    ring = Range(low=0)

    #: The ring area occupied by this layout area.
    area = Enum('left', 'right', 'top', 'bottom')

    #: The list of DockItem instances managed by the area.
    dock_items = List()

    #: The QSplitter widget used to implement the layout.
    splitter = Typed(QSplitter)

    def addDockItem(self, item):
        """ Add a dock item to this layout area.

        Parameters
        ----------
        item : QDockItem
            A dock item which has an address pointing to this area.

        """
        self.dock_items.insert(item.index(), item)
        splitter = self.splitter
        if splitter is None:
            parent = self.layout.parentWidget()
            splitter = self.splitter = QSplitter(parent)
            splitter.setFrameShape(QSplitter.Box)
            splitter.setLineWidth(2)
            if self.area == 'left' or self.area == 'right':
                splitter.setOrientation(Qt.Vertical)
        self.splitter.insertWidget(item.index(), item)
        self.invalidate()

    def removeDockItem(self, item):
        """ Remove a dock item from the layout area.

        Parameters
        ----------
        item : QDockItem
            The item to remove from the area.

        """
        try:
            self.dock_items.remove(item)
        except ValueError:
            pass
        splitter = self.splitter
        if splitter is not None and item.parent() is splitter:
            item.setParent(None)
            if len(self.dock_items) == 0:
                splitter.setParent(None)
                del self.splitter
        self.invalidate()

    def setGeometry(self, rect):
        """ Set the geometry of the layout area.

        """
        splitter = self.splitter
        if splitter is not None:
            splitter.setGeometry(rect)

    def doSizeHint(self):
        """ Compute the size hint for the layout area.

        """
        splitter = self.splitter
        if splitter is not None:
            return splitter.sizeHint()
        return QSize(0, 0)

    def doMinimumSize(self):
        """ Compute the minimum size of the layout area.

        """
        splitter = self.splitter
        if splitter is not None:
            return splitter.minimumSizeHint()
        return QSize(0, 0)

    def doVerticalStretch(self):
        """ Compute the vertical stretch factor for the layout area.

        """
        dock_items = self.dock_items
        if not dock_items:
            return 0
        s = sum(item.verticalStretch() for item in dock_items)
        n = len(dock_items)
        if n > 1:
            s += 1
        return s / n

    def doHorizontalStretch(self):
        """ Compute the horizontal stretch factor for the layout area.

        """
        dock_items = self.dock_items
        if not dock_items:
            return 0
        s = sum(item.horizontalStretch() for item in dock_items)
        n = len(dock_items)
        if n > 1:
            s += 1
        return s / n

    def leadingCorners(self):
        if not self.dock_items:
            return NoCorners
        return self.dock_items[0].corners()

    def trailingCorners(self):
        if not self.dock_items:
            return NoCorners
        return self.dock_items[-1].corners()


class LayoutStruct(Atom):

    item = Typed(LayoutBase)

    fixed_x = Bool(False)

    fixed_y = Bool(False)

    fixed_right = Bool(False)

    fixed_bottom = Bool(False)

    @property
    def x(self):
        return self.item.x

    @property
    def y(self):
        return self.item.y

    @property
    def width(self):
        return self.item.width

    @property
    def height(self):
        return self.item.height

    @property
    def right(self):
        return self.item.right

    @property
    def bottom(self):
        return self.item.bottom

    def minimumSize(self):
        return self.item.minimumSize()


class Corners(Atom):

    top_left = Typed(LayoutBase)

    top_right = Typed(LayoutBase)

    bottom_left = Typed(LayoutBase)

    bottom_right = Typed(LayoutBase)


class LayoutRing(LayoutBase):
    """ A class which implements the layout for a ring.

    """
    #: The ring address occupied by this ring.
    ring = Range(low=0)

    #: The layout area occupying the top area of the ring.
    top = Typed(LayoutArea)

    #: The layout area occupying the left area of the ring.
    left = Typed(LayoutArea)

    #: The layout area occupying the right area of the ring.
    right_area = Typed(LayoutArea)

    #: The layout area occupying the bottom area of the ring.
    bottom_area = Typed(LayoutArea)

    #: The splitter handle assigned to the top layout area.
    top_handle = ForwardTyped(lambda: QDockHandle)

    #: The splitter handle assigned to the left layout area.
    left_handle = ForwardTyped(lambda: QDockHandle)

    #: The splitter handle assigned to the right layout area.
    right_handle = ForwardTyped(lambda: QDockHandle)

    #: The splitter handle assigned to the bottom layout area.
    bottom_handle = ForwardTyped(lambda: QDockHandle)

    #: The interior child ring for this layout ring.
    child_ring = ForwardTyped(lambda: LayoutRing)

    #: The object which holds the corner mappings.
    corners = Typed(Corners, ())

    solver = Typed(Solver)

    def do_layout(self):
        if self.child_ring:
            self.child_ring.do_layout()
        solver = self.solver = Solver(autosolve=False)
        for cn in self.constraints():
            solver.add_constraint(cn)
        solver.autosolve = True

    def constraints(self):
        cns = []

        structs = {}

        # Setup the layout structs
        top = self.top
        if top:
            top = LayoutStruct(item=top)
            structs[top.item] = top
        left = self.left
        if left:
            left = LayoutStruct(item=left)
            structs[left.item] = left
        right = self.right_area
        if right:
            right = LayoutStruct(item=right)
            structs[right.item] = right
        bottom = self.bottom_area
        if bottom:
            bottom = LayoutStruct(item=bottom)
            structs[bottom.item] = bottom
        child = self.child_ring
        if child:
            child = LayoutStruct(item=child)
            structs[child.item] = child

        # Basic constraints
        if top:
            top_min = top.minimumSize()
            cns.extend([
                top.y == self.y,
                top.width >= top_min.width(),
                top.height >= top_min.height(),
            ])
            top.fixed_y = True
        if left:
            left_min = left.minimumSize()
            cns.extend([
                left.x == self.x,
                left.width >= left_min.width(),
                left.height >= left_min.height(),
            ])
            left.fixed_x = True
        if right:
            right_min = right.minimumSize()
            cns.extend([
                right.right == self.right,
                right.width >= right_min.width(),
                right.height >= right_min.height(),
            ])
            right.fixed_right = True
        if bottom:
            bottom_min = bottom.minimumSize()
            cns.extend([
                bottom.bottom == self.bottom,
                bottom.width >= bottom_min.width(),
                bottom.height >= bottom_min.height(),
            ])
            bottom.fixed_bottom = True
        if child:
            child_min = child.minimumSize()
            cns.extend([
                child.width >= child_min.width(),
                child.height >= child_min.height(),
            ])
        else:
            child = LayoutStruct(item=LayoutRing())
            cns.extend([
                child.width >= 0,
                child.height >= 0,
                (child.width == 0) | 'weak',
                (child.height == 0) | 'weak',
            ])

        corners = self.corners

        # top left corner
        assert corners.top_left is not None
        st = structs[corners.top_left]
        cns.extend([
            st.x == self.x,
            st.y == self.y,
        ])
        st.fixed_x = True
        st.fixed_y = True

        # top right corner
        assert corners.top_right is not None
        st = structs[corners.top_right]
        cns.extend([
            st.right == self.right,
            st.y == self.y,
        ])
        st.fixed_right = True
        st.fixed_y = True

        # bottom left corner
        assert corners.bottom_left is not None
        st = structs[corners.bottom_left]
        cns.extend([
            st.x == self.x,
            st.bottom == self.bottom,
        ])
        st.fixed_x = True
        st.fixed_bottom = True

        # bottom right corner
        assert corners.bottom_right is not None
        st = structs[corners.bottom_right]
        cns.extend([
            st.right == self.right,
            st.bottom == self.bottom,
        ])
        st.fixed_right = True
        st.fixed_bottom = True

        # Fill out the the border constraints
        if top:
            if not top.fixed_x:
                if left:
                    cns.append(left.right == top.x)
                    left.fixed_right = True
                else:
                    cns.append(self.x == top.x)
                top.fixed_x = True
            if not top.fixed_right:
                if right:
                    cns.append(top.right == right.x)
                    right.fixed_x = True
                else:
                    cns.append(top.right == self.right)
                top.fixed_right = True

        if bottom:
            if not bottom.fixed_x:
                if left:
                    cns.append(left.right == bottom.x)
                    left.fixed_right = True
                else:
                    cns.append(self.x == bottom.x)
                bottom.fixed_x = True
            if not bottom.fixed_right:
                if right:
                    cns.append(bottom.right == right.x)
                    right.fixed_x = True
                else:
                    cns.append(bottom.right == self.right)
                bottom.fixed_right = True

        if left:
            if not left.fixed_y:
                if top:
                    cns.append(top.bottom == left.y)
                    top.fixed_bottom = True
                else:
                    cns.append(self.y == left.y)
                left.fixed_y = True
            if not left.fixed_bottom:
                if bottom:
                    cns.append(left.bottom == bottom.y)
                    bottom.fixed_y = True
                else:
                    cns.append(left.bottom == self.bottom)
                left.fixed_bottom = True

        if right:
            if not right.fixed_y:
                if top:
                    cns.append(top.bottom == right.y)
                    top.fixed_bottom = True
                else:
                    cns.append(self.y == right.y)
                right.fixed_y = True
            if not right.fixed_bottom:
                if bottom:
                    cns.append(right.bottom == bottom.y)
                    bottom.fixed_y = True
                else:
                    cns.append(right.bottom == self.bottom)
                right.fixed_bottom = True

        # Fill out the child constraints
        if not child.fixed_x:
            if left:
                cns.append(left.right == child.x)
                left.fixed_right = True
            else:
                cns.append(self.x == child.x)
            child.fixed_x = True
        if not child.fixed_y:
            if top:
                cns.append(top.bottom == child.y)
                top.fixed_bottom = True
            else:
                cns.append(self.y == child.y)
            child.fixed_y = True
        if not child.fixed_right:
            if right:
                cns.append(child.right == right.x)
                right.fixed_x = True
            else:
                cns.append(child.right == self.right)
            child.fixed_right = True
        if not child.fixed_bottom:
            if bottom:
                cns.append(child.bottom == bottom.y)
                bottom.fixed_y = True
            else:
                cns.append(child.bottom == self.bottom)
            child.fixed_bottom =  True

        these = filter(None, [left, right, bottom, top, child])
        if these:
            this = these.pop()
            while these:
                cns.extend([
                    (this.width == these[-1].width) | 'weak',
                    (this.height == these[-1].height) | 'weak',
                ])
                this = these.pop()

        return cns

    def getChildRing(self, ring, create=False):
        """ Get the child ring of the given number.

        Parameters
        ----------
        ring : int
            The target ring number. This must be less than the current
            ring number.

        force_create : bool, optional
            Whether to create the ring if needed. The default is False.

        Returns
        -------
        result : LayoutRing or None
            The child layout ring, or None if a match was not found.

        """
        child = self.child_ring
        if child is None:
            if create:
                child = LayoutRing(parent=self, layout=self.layout, ring=ring)
                self.child_ring = ring
            return child
        if child.ring == ring:
            return child
        if child.ring > ring:
            return child.getChildRing(ring, create)
        if create:
            child = LayoutRing(
                parent=self, layout=self.layout, ring=ring, child_ring=child
            )
            self.child_ring = child
            return child
        return None

    def resolveCorners(self):
        corners = self.corners
        top = self.top
        left = self.left
        right = self.right_area
        bottom = self.bottom_area
        child = self.child_ring

        if left:
            corners.top_left = left
            corners.bottom_left = left

        if right:
            corners.top_right = right
            corners.bottom_right = right

        # top left corner
        if (top and
            (not corners.top_left or
             ((top.leadingCorners() & TopLeftCorner) and not
              (corners.top_left.leadingCorners() & TopLeftCorner)))):
            corners.top_left = top
        elif child and not corners.top_left:
            corners.top_left = child
        elif right and not corners.top_left:
            corners.top_left = right
        elif bottom and not corners.top_left:
            corners.top_left = bottom

        # bottom left corner
        if (bottom and
            (not corners.bottom_left or
             ((bottom.leadingCorners() & BottomLeftCorner) and not
              (corners.bottom_left.leadingCorners() & BottomLeftCorner)))):
            corners.bottom_left = bottom
        elif child and not corners.bottom_left:
            corners.bottom_left = child
        elif right and not corners.bottom_left:
            corners.bottom_left = right
        elif top and not corners.bottom_left:
            corners.bottom_left = top

        # top right corner
        if (top and
            (not corners.top_right or
             ((top.trailingCorners() & TopRightCorner) and not
              (corners.top_right.trailingCorners() & TopRightCorner)))):
            corners.top_right = top
        elif child and not corners.top_right:
            corners.top_right = child
        elif left and not corners.top_right:
            corners.top_right = left
        elif bottom and not corners.top_right:
            corners.top_right = bottom

        # bottom right corner
        if (bottom and
            (not corners.bottom_right or
             ((bottom.trailingCorners() & BottomRightCorner) and not
              (corners.bottom_right.trailingCorners() & BottomRightCorner)))):
            corners.bottom_right = bottom
        elif child and not corners.bottom_right:
            corners.bottom_right = child
        elif left and not corners.bottom_right:
            corners.bottom_right = left
        elif top and not corners.bottom_right:
            corners.bottom_right = top

    def addDockItem(self, item):
        """ Add a dock item to this layout ring.

        Parameters
        ----------
        item : QDockItem
            A dock item which has an address pointing to this ring.

        """
        area_name = item.area()
        if area_name == 'right' or area_name == 'bottom':
            area = getattr(self, area_name + '_area')
        else:
            area = getattr(self, area_name)
        if area is None:
            area = LayoutArea(parent=self, layout=self.layout, area=area_name)
            if area_name == 'right' or area_name == 'bottom':
                setattr(self, area_name + '_area', area)
            else:
                setattr(self, area_name, area)
        area.addDockItem(item)
        self.resolveCorners()

    def removeDockItem(self, item):
        """ Remove a dock item from the layout ring.

        Parameters
        ----------
        item : QDockItem
            The item to remove from the ring.

        """
        area_name = item.area()
        area = getattr(self, area_name)
        if area is not None:
            area.removeDockItem(item)

    def setGeometry(self, rect):
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()
        values = [(self.x, x), (self.y, y), (self.width, w), (self.height, h)]
        with self.solver.suggest_values(values, medium, 1.0):
            for attr in ('top', 'left', 'right_area', 'bottom_area', 'child_ring'):
                item = getattr(self, attr)
                if item:
                    v_x = item.x.value
                    v_y = item.y.value
                    v_w = item.width.value
                    v_h = item.height.value
                    item.setGeometry(QRect(v_x, v_y, v_w, v_h))

    def doSizeHint(self):
        """ Compute the size hint for the layout ring.

        """
        width = height = 0
        child = self.child_ring
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
        bottom = self.bottom_area
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
        right = self.right_area
        if right is not None:
            size = right.sizeHint()
            width += size.width()
            height = max(height, size.height())
        right_handle = self.right_handle
        if right_handle is not None:
            width += right_handle.sizeHint().height()
        return QSize(width, height)

    def doMinimumSize(self):
        """ Compute the minimum size for the layout ring.

        """
        width = height = 0
        child = self.child_ring
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
        bottom = self.bottom_area
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
        right = self.right_area
        if right is not None:
            size = right.minimumSize()
            width += size.width()
            height = max(height, size.height())
        right_handle = self.right_handle
        if right_handle is not None:
            width += right_handle.minimumSizeHint().height()
        return QSize(width, height)

    def doVerticalStretch(self):
        """ Compute the vertical stretch factor for the ring.

        """
        s = n = 0
        child = self.child_ring
        if child is not None:
            n += 1
            s += child.verticalStretch()
        top = self.top
        if top is not None:
            n += 1
            s += top.verticalStretch()
        bottom = self.bottom
        if bottom is not None:
            n += 1
            s += bottom.verticalStretch()
        left = self.left
        if left is not None:
            n += 1
            s += left.verticalStretch()
        right = self.right
        if right is not None:
            n += 1
            s += right.verticalStretch()
        if n > 1:
            n += 1
        return s / n

    def doHorizontalStretch(self):
        """ Compute the horizontal stretch factor for the ring.

        """
        s = n = 0
        child = self.child_ring
        if child is not None:
            n += 1
            s += child.horizontalStretch()
        top = self.top
        if top is not None:
            n += 1
            s += top.horizontalStretch()
        bottom = self.bottom
        if bottom is not None:
            n += 1
            s += bottom.horizontalStretch()
        left = self.left
        if left is not None:
            n += 1
            s += left.horizontalStretch()
        right = self.right
        if right is not None:
            n += 1
            s += right.horizontalStretch()
        if n > 1:
            n += 1
        return s / n


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
        self._ring = LayoutRing(layout=self)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _get_ring(self, ring, create=False):
        """ Get the layout ring for the given ring number.

        Parameters
        ----------
        ring : int
            The target ring number.

        create : bool, optional
            Whether to create the ring if needed. The default is False.

        """
        r = self._ring
        if r.ring == ring:
            return r
        if r.ring > ring:
            return r.getChildRing(ring, create)
        if create:
            r = LayoutRing(layout=self, ring=ring, child_ring=r)
            self._ring = r
            return r
        return None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addDockItem(self, item):
        """ Add a dock item to the layout.

        Parameters
        ----------
        item : QDockItem
            A dock item to add to the layout.

        """
        ring = self._get_ring(item.ring(), create=True)
        ring.addDockItem(item)
        self.invalidate()

    def removeDockItem(self, item):
        """ Remove a dock item from the layout.

        Parameters
        ----------
        item : QDockItem
            The item to remove from the layout.

        """
        ring = self._get_ring(item.ring())
        if ring is not None:
            ring.removeDockItem(item)
            self.invalidate()

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        self._ring.setGeometry(rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        return self._ring.sizeHint()

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayoutItem` instead.

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


class QDockItem(QFrame):

    def __init__(self, parent=None):
        super(QDockItem, self).__init__(parent)
        self._title_bar = None
        self._h_stretch = 1
        self._v_stretch = 1
        self._ring = 0
        self._area = 'left'
        self._index = 0
        self._corners = 0

    def horizontalStretch(self):
        return self._h_stretch

    def verticalStretch(self):
        return self._v_stretch

    def ring(self):
        return self._ring

    def area(self):
        return self._area

    def index(self):
        return self._index

    def corners(self):
        return self._corners


class QDockArea(QWidget):

    def __init__(self, parent=None):
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

class QDockHandle(QWidget):
    pass


app = QApplication([])

m = QDockArea()
l = m.layout()

i1 = QDockItem()
i1.setMinimumSize(QSize(100, 100))
i1._area = 'top'
i2 = QDockItem()
i2.setMinimumSize(QSize(100, 100))
i2._area = 'top'
i3 = QDockItem()
i3.setMinimumSize(QSize(100, 100))
i3._area = 'left'
i4 = QDockItem()
i4.setMinimumSize(QSize(100, 100))
i4._area = 'left'
i5 = QDockItem()
i5.setMinimumSize(QSize(100, 100))
i5._area = 'right'
i6 = QDockItem()
i6.setMinimumSize(QSize(100, 100))
i6._area = 'right'
i7 = QDockItem()
i7.setMinimumSize(QSize(100, 100))
i7._area = 'bottom'
i8 = QDockItem()
i8.setMinimumSize(QSize(100, 100))
i8._area = 'bottom'


i1.setStyleSheet('QDockItem { background: red; }')
i2.setStyleSheet('QDockItem { background: green; }')
i3.setStyleSheet('QDockItem { background: blue; }')
i4.setStyleSheet('QDockItem { background: yellow; }')
i5.setStyleSheet('QDockItem { background: gray; }')
i6.setStyleSheet('QDockItem { background: steelblue; }')
i7.setStyleSheet('QDockItem { background: lightskyblue; }')
i8.setStyleSheet('QDockItem { background: orange; }')


l.addDockItem(i1)
l.addDockItem(i2)
l.addDockItem(i3)
l.addDockItem(i4)
l.addDockItem(i5)
l.addDockItem(i6)
l.addDockItem(i7)
l.addDockItem(i8)


s_i1 = QDockItem()
s_i1.setMinimumSize(QSize(100, 100))
s_i1._area = 'top'
s_i1._ring = 1
s_i2 = QDockItem()
s_i2.setMinimumSize(QSize(100, 100))
s_i2._area = 'top'
s_i2._ring = 1
s_i2._corners = TopLeftCorner
s_i3 = QDockItem()
s_i3.setMinimumSize(QSize(100, 100))
s_i3._area = 'left'
s_i3._ring = 1
s_i4 = QDockItem()
s_i4.setMinimumSize(QSize(100, 100))
s_i4._area = 'left'
s_i4._ring = 1
s_i5 = QDockItem()
s_i5.setMinimumSize(QSize(100, 100))
s_i5._area = 'right'
s_i5._ring = 1
s_i6 = QDockItem()
s_i6.setMinimumSize(QSize(100, 100))
s_i6._area = 'right'
s_i6._ring = 1
s_i7 = QDockItem()
s_i7.setMinimumSize(QSize(100, 100))
s_i7._area = 'bottom'
s_i7._ring = 1
s_i7._corners = BottomRightCorner
s_i8 = QDockItem()
s_i8.setMinimumSize(QSize(100, 100))
s_i8._area = 'bottom'
s_i8._ring = 1


s_i1.setStyleSheet('QDockItem { background: pink; }')
s_i2.setStyleSheet('QDockItem { background: teal; }')
s_i3.setStyleSheet('QDockItem { background: salmon; }')
s_i4.setStyleSheet('QDockItem { background: goldenrod; }')
s_i5.setStyleSheet('QDockItem { background: darkgray; }')
s_i6.setStyleSheet('QDockItem { background: lime; }')
s_i7.setStyleSheet('QDockItem { background: green; }')
s_i8.setStyleSheet('QDockItem { background: indianred; }')


l.addDockItem(s_i1)
l.addDockItem(s_i2)
l.addDockItem(s_i3)
l.addDockItem(s_i4)
l.addDockItem(s_i5)
l.addDockItem(s_i6)
l.addDockItem(s_i7)
l.addDockItem(s_i8)

l._ring.do_layout()

m.show()
app.exec_()
