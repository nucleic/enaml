#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from future.utils import with_metaclass

from .QtCore import Qt, QSize, QRect
from .QtWidgets import QLayout, QWidgetItem


class AbstractFlowWidget(with_metaclass(ABCMeta, object)):
    """ An abstract base class which defines the interface for widgets
    which can be used in a QFlowLayout.

    Users of QFlowLayout must register their custom QWidget classes with
    this class in order to use the QFlowLayout.

    """

    @abstractmethod
    def layoutData(self):
        """ An abstractmethod which must be implemented by subclasses.

        Returns
        -------
        result : FlowLayoutData
            The FlowLayoutData instance to use for this widget. The
            same data layout data instance should be returned for
            each call to this method.

        """
        raise NotImplementedError


class FlowLayoutData(object):
    """ The layout data object to use with AbstractFlowWidget instances.

    For performance reasons, there are no runtime checks on the limits
    of the values assigned to this class. Users should ensure that the
    values assigned conform to the documented limits. Users must set
    the `dirty` flag to True before calling `updateGeometry` in order
    for changes to have effect.

    """
    #: Whether or not the computed info for the layout item is dirty.
    #: This must be set to True before calling `updateGeometry` on
    #: the owner widget.
    dirty = True

    #: The flow stretch factor of the layout item. This value controls
    #: the amount of space that is taken up by an expandable item in the
    #: direction of the layout flow, relative to the other items in the
    #: line. The minimum is 0 which means the item should not expand.
    #: There is no maximum. The default is 0.
    stretch = 0

    #: The ortho stretch factor of the layout item. This value controls
    #: the amount of space that is taken up by an expandable item in the
    #: direction orthogonal to the layout flow, relative to other items
    #: in the line. The minimum is 0 which means the item should not
    #: expand. There is no maximum. The default is 0.
    ortho_stretch = 0

    #: The alignment of the layout item in the direction orthogonal to
    #: the layout flow. This must be one of the enums Qt.AlignLeading,
    #: Qt.AlignTrailing, or Qt.AlignCenter.
    alignment = Qt.AlignLeading

    #: The preferred size for the layout item. This size will be used
    #: as the size of the layout item to the extent possible. If this
    #: size is invalid in a particular dimension, the sizeHint of the
    #: item in that direction will be used.
    preferred_size = QSize()

    def __init__(self):
        """ Initialize a FlowLayoutData.

        """
        self.preferred_size = QSize()


class QFlowWidgetItem(QWidgetItem):
    """ A custom QWidgetItem for use with the QFlowLayout.

    """
    #: The FlowLayoutData associated with this widget item. It is a
    #: publically accesible attribute for performance reasons.
    data = None

    def __init__(self, widget, data):
        """ Initialize a QFlowWidgetItem.

        Parameters
        ----------
        widget : QWidget
            The widget to manage with this item.

        data : FlowLayoutData
            The layout data struct associated with this item.

        """
        super(QFlowWidgetItem, self).__init__(widget)
        self.data = data
        self._cached_hint = QSize()
        self._cached_max = QSize()
        self._cached_min = QSize()

    def maximumSize(self):
        """ Reimplemented maximum size computation.

        The max size for a flow widget item is cached and recomputed
        only when the widget item is invalidated.

        """
        if not self._cached_max.isValid():
            self._cached_max = super(QFlowWidgetItem, self).maximumSize()
        return self._cached_max

    def minimumSize(self):
        """ Reimplemented minimum size computation.

        The min size for a flow widget item is cached and recomputed
        only when the widget item is invalidated.

        """
        if not self._cached_min.isValid():
            self._cached_min = super(QFlowWidgetItem, self).minimumSize()
        return self._cached_min

    def sizeHint(self):
        """ Reimplemented size hint computation.

        The size hint for a flow widget item is cached and recomputed
        only when the widget item is invalidated. The size hint is the
        valid union of the preferred size, as indicated by the layout
        data, and the size hint of the widget.

        """
        if not self._cached_hint.isValid():
            hint = super(QFlowWidgetItem, self).sizeHint()
            pref = self.data.preferred_size
            smin = self.minimumSize()
            smax = self.maximumSize()
            if pref.width() != -1:
                pw = max(smin.width(), min(pref.width(), smax.width()))
                hint.setWidth(pw)
            if pref.height() != -1:
                ph = max(smin.height(), min(pref.height(), smax.height()))
                hint.setHeight(ph)
            self._cached_hint = hint
        return self._cached_hint

    def setGeometry(self, rect):
        """ Set the rectangle covered by this layout item.

        This reimplemented method ensures that layout always occurs at
        the origin of the given rect. The default QWidgetItem behavior
        is to center the item in the given space.

        Parameters
        ----------
        rect : QRect
            The rectangle that this layout item should cover.

        """
        if self.isEmpty():
            return
        s = rect.size().boundedTo(self.maximumSize())
        self.widget().setGeometry(rect.x(), rect.y(), s.width(), s.height())

    def invalidate(self):
        """ Invalidate the internal cached data for this widget item.

        The invalidation will only have an effect if the layout data
        associate with this item is marked as dirty.

        """
        if self.data.dirty:
            self._cached_hint = QSize()
            self._cached_min = QSize()
            self.data.dirty = False


class _LayoutRow(object):
    """ A private class used by QFlowLayout.

    This class accumulates information about a row of items as the items
    are added to the row. Instances of the this class are created by the
    QFlowLayout during a layout pass. For performance reasons, there are
    several publically accesible attributes. See their documentation for
    restrictions on their use.

    """
    #: The height to use for laying out the row. This attribute is
    #: modified directly by the layout as it distributes the vertical
    #: space amongst the rows.
    layout_height = 0

    #: The minimum height required for the row. This is automatically
    #: updated as items are added to the row. It should be considered
    #: read-only to external users.
    min_height = 0

    #: The minimum width required for the row. This is automatically
    #: updated as items are added to the row. It should be considered
    #: read-only to external users.
    min_width = 0

    #: The desired height for the row. This is automatically updated as
    #: items are added to the row. It should be considered read-only to
    #: external users.
    hint_height = 0

    #: The desired width for the row. This is automatically updated as
    #: items are added to the row. It should be considered read-only to
    #: external users.
    hint_width = 0

    #: The vertical stretch factor for the row. This is automatically
    #: updated as items are added to the row. It should be considered
    #: read-only by external users.
    stretch = 0

    def __init__(self, width, options):
        """ Initialize a layout row.

        Parameters
        ----------
        width : int
            The width of the layout area.

        options : _LayoutOptions
            The options in effect for the layout.

        """
        self._width = width
        self._options = options
        self._items_stretch = 0
        self._items = []

    @property
    def diff_height(self):
        """ A read-only property which computes the difference between
        the desired height and the minimum height.

        """
        return self.hint_height - self.min_height

    def add_item(self, item):
        """ Add an item to the layout row.

        Parameters
        ----------
        item : QFlowWidgetItem
            The flow widget item to add to the layout row.

        Returns
        -------
        result : bool
            True if the items was added. False if the item was not
            added. An item will not be added if the row already
            contains an item and adding another item would cause
            it to overflow.

        """
        min_size = item.minimumSize()
        hint_size = item.sizeHint()
        n = len(self._items)
        s = self._options.h_spacing
        if n > 0 and (self.hint_width + s + hint_size.width()) > self._width:
            return False
        self.min_height = max(self.min_height, min_size.height())
        self.hint_height = max(self.hint_height, hint_size.height())
        self.stretch = max(self.stretch, item.data.ortho_stretch)
        self.min_width += min_size.width()
        self.hint_width += hint_size.width()
        self._items_stretch += item.data.stretch
        if n > 0:
            self.min_width += s
            self.hint_width += s
        self._items.append(item)
        return True

    def layout(self, x, y):
        """ Layout the row using the given starting coordinates.

        Parameters
        ----------
        x : int
            The x coordinate of the row origin.

        y : int
            The y coordinate of the row origin.

        """
        opts = self._options
        layout_width = self._width
        layout_height = self.layout_height
        delta = self._width - self.hint_width
        items = self._items

        # Short circuit the case where there is negative extra space.
        # This means that there must be only a single item in the row,
        # in which case the width may shrink to the minimum if needed.
        if delta < 0:
            assert len(items) == 1
            item = items[0]
            w = max(layout_width, item.minimumSize().width())
            if item.data.ortho_stretch > 0:
                h = min(layout_height, item.maximumSize().height())
            else:
                h = min(layout_height, item.sizeHint().height())
            delta_h = layout_height - h
            if delta_h > 0:
                align = item.data.alignment
                if align == QFlowLayout.AlignTrailing:
                    y += delta_h
                elif align == QFlowLayout.AlignCenter:
                    y += delta_h / 2
            item.setGeometry(QRect(x, y, w, h))
            return

        # Reversing the items reverses the layout direction. All of the
        # computation up to this point has be independent of direction.
        if opts.direction == QFlowLayout.RightToLeft:
            items.reverse()

        # Precompute a map of starting widths for the items. These will
        # be progressively modified as the delta space is distributed.
        widths = {}
        for item in items:
            widths[item] = item.sizeHint().width()

        # If the flow stretch for the row is greater than zero. Then
        # there exists an item or items which have flow stretch. It's
        # not sufficient to simply distribute the delta space according
        # to relative stretch factors, because an item may have a max
        # width which is less than the adjusted width. This causes the
        # rest of the adjustments to be invalid, yielding a potential
        # O(n^2) solution. Instead, the items which can stretch are
        # sorted according to the differences between their desired
        # width and max width. When distributing the delta space in this
        # order, any unused space from an item is added back to the pool
        # and its stretch factor removed from further computation. This
        # gives an O(n log n) solution to the problem. This algorithm
        # iteratively removes space from the delta, so that the alignment
        # pass below operates on the adjusted free space amount.
        items_stretch = self._items_stretch
        if items_stretch > 0:
            diffs = []
            for item in items:
                if item.data.stretch > 0:
                    h = item.sizeHint().width()
                    m = item.maximumSize().width()
                    diffs.append((m - h, item))
            diffs.sort()
            for ignored, item in diffs:
                item_stretch = item.data.stretch
                max_width = item.maximumSize().width()
                d = item_stretch * delta / items_stretch
                items_stretch -= item_stretch
                item_width = widths[item]
                if item_width + d > max_width:
                    widths[item] = max_width
                    delta -= max_width - item_width
                else:
                    widths[item] = item_width + d
                    delta -= d

        # The widths of all items are now computed. Any leftover delta
        # space is used for alignment purposes. This is accomplished by
        # shifting the starting location and, in the case of justify,
        # adding to the horizontal space value.
        start_x = x
        space = opts.h_spacing
        if opts.alignment == QFlowLayout.AlignLeading:
            if opts.direction == QFlowLayout.RightToLeft:
                start_x += delta
        elif opts.alignment == QFlowLayout.AlignTrailing:
            if opts.direction == QFlowLayout.LeftToRight:
                start_x += delta
        elif opts.alignment == QFlowLayout.AlignCenter:
            start_x += delta / 2
        else:
            d = delta / (len(items) + 1)
            space += d
            start_x += d

        # Make a final pass over the items and perform the layout. This
        # pass handles the orthogonal alignment of the item if there is
        # any leftover vertical space for the item.
        curr_x = start_x
        for item in items:
            w = widths[item]
            if item.data.ortho_stretch > 0:
                h = min(layout_height, item.maximumSize().height())
            else:
                h = min(layout_height, item.sizeHint().height())
            delta = layout_height - h
            this_y = y
            if delta > 0:
                align = item.data.alignment
                if align == QFlowLayout.AlignTrailing:
                    this_y = y + delta
                elif align == QFlowLayout.AlignCenter:
                    this_y = y + delta / 2
            item.setGeometry(QRect(curr_x, this_y, w, h))
            curr_x += (w + space)


class _LayoutColumn(object):
    """ A private class used by QFlowLayout.

    This class accumulates information about a column of items as the
    items are added to the column. Instances of the this class are
    created by the QFlowLayout during a layout pass. For performance
    reasons, there are several publically accesible attributes. See
    their documentation for restrictions on their use.

    """
    #: The width to use for laying out the column. This attribute is
    #: modified directly by the layout as it distributes the horizontal
    #: space amongst the columns.
    layout_width = 0

    #: The minimum height required for the column. This is automatically
    #: updated as items are added to the column. It should be considered
    #: read-only to external users.
    min_height = 0

    #: The minimum width required for the column. This is automatically
    #: updated as items are added to the column. It should be considered
    #: read-only to external users.
    min_width = 0

    #: The desired height for the column. This is automatically updated
    #: as items are added to the column. It should be considered
    #: read-only to external users.
    hint_height = 0

    #: The desired width for the column. This is automatically updated
    #: as items are added to the column. It should be considered
    #: read-only to external users.
    hint_width = 0

    #: The vertical stretch factor for the column. This is automatically
    #: updated as items are added to the column. It should be considered
    #: read-only by external users.
    stretch = 0

    def __init__(self, height, options):
        """ Initialize a layout column.

        Parameters
        ----------
        height : int
            The height of the layout area.

        options : _LayoutOptions
            The options in effect for the layout.

        """
        self._height = height
        self._options = options
        self._items_stretch = 0
        self._items = []

    @property
    def diff_width(self):
        """ A read-only property which computes the difference between
        the desired width and the minimum width.

        """
        return self.hint_width - self.min_width

    def add_item(self, item):
        """ Add an item to the layout column.

        Parameters
        ----------
        item : QFlowWidgetItem
            The flow widget item to add to the layout column.

        Returns
        -------
        result : bool
            True if the items was added. False if the item was not
            added. An item will not be added if the column already
            contains an item and adding another item would cause
            it to overflow.

        """
        min_size = item.minimumSize()
        hint_size = item.sizeHint()
        n = len(self._items)
        s = self._options.v_spacing
        if n > 0 and self.hint_height + s + hint_size.height() > self._height:
            return False
        self.min_width = max(self.min_width, min_size.width())
        self.hint_width = max(self.hint_width, hint_size.width())
        self.stretch = max(self.stretch, item.data.ortho_stretch)
        self.min_height += min_size.height()
        self.hint_height += hint_size.height()
        self._items_stretch += item.data.stretch
        if n > 0:
            self.min_height += s
            self.hint_height += s
        self._items.append(item)
        return True

    def layout(self, x, y):
        """ Layout the row using the given starting coordinates.

        Parameters
        ----------
        x : int
            The x coordinate of the column origin.

        y : int
            The y coordinate of the column origin.

        """
        opts = self._options
        layout_height = self._height
        layout_width = self.layout_width
        delta = self._height - self.hint_height
        items = self._items

        # Short circuit the case where there is negative extra space.
        # This means that there must be only a single item in the column,
        # in which case the height may shrink to the minimum if needed.
        if delta < 0:
            assert len(items) == 1
            item = items[0]
            h = max(layout_height, item.minimumSize().height())
            if item.data.ortho_stretch > 0:
                w = min(layout_width, item.maximumSize().width())
            else:
                w = min(layout_width, item.sizeHint().width())
            delta_w = layout_width - w
            if delta_w > 0:
                align = item.data.alignment
                if align == QFlowLayout.AlignTrailing:
                    x += delta_w
                elif align == QFlowLayout.AlignCenter:
                    x += delta_w / 2
            item.setGeometry(QRect(x, y, w, h))
            return

        # Reversing the items reverses the layout direction. All of the
        # computation up to this point has be independent of direction.
        if opts.direction == QFlowLayout.BottomToTop:
            items.reverse()

        # Precompute a map of starting heights for the items. These will
        # be progressively modified as the delta space is distributed.
        heights = {}
        for item in items:
            heights[item] = item.sizeHint().height()

        # See the long comment in _LayoutRow for the explanation about
        # this section of code. This section is simply the transpose.
        items_stretch = self._items_stretch
        if items_stretch > 0:
            diffs = []
            for item in items:
                if item.data.stretch > 0:
                    h = item.sizeHint().height()
                    m = item.maximumSize().height()
                    diffs.append((m - h, item))
            diffs.sort()
            for ignored, item in diffs:
                item_stretch = item.data.stretch
                max_height = item.maximumSize().height()
                d = item_stretch * delta / items_stretch
                items_stretch -= item_stretch
                item_height = heights[item]
                if item_height + d > max_height:
                    heights[item] = max_height
                    delta -= max_height - item_height
                else:
                    heights[item] = item_height + d
                    delta -= d

        # The heights of all items are now computed. Any leftover delta
        # space is used for alignment purposes. This is accomplished by
        # shifting the starting location and, in the case of justify,
        # adding to the vertical space value.
        start_y = y
        space = opts.v_spacing
        if opts.alignment == QFlowLayout.AlignLeading:
            if opts.direction == QFlowLayout.BottomToTop:
                start_y += delta
        elif opts.alignment == QFlowLayout.AlignTrailing:
            if opts.direction == QFlowLayout.TopToBottom:
                start_y += delta
        elif opts.alignment == QFlowLayout.AlignCenter:
            start_y += delta / 2
        else:
            d = delta / (len(items) + 1)
            space += d
            start_y += d

        # Make a final pass over the items and perform the layout. This
        # pass handles the orthogonal alignment of the item if there is
        # any leftover horizontal space for the item.
        curr_y = start_y
        for item in items:
            h = heights[item]
            if item.data.ortho_stretch > 0:
                w = min(layout_width, item.maximumSize().width())
            else:
                w = min(layout_width, item.sizeHint().width())
            delta = layout_width - w
            this_x = x
            if delta > 0:
                align = item.data.alignment
                if align == QFlowLayout.AlignTrailing:
                    this_x = x + delta
                elif align == QFlowLayout.AlignCenter:
                    this_x = x + delta / 2
            item.setGeometry(QRect(this_x, curr_y, w, h))
            curr_y += (h + space)


class QFlowLayout(QLayout):
    """ A custom QLayout which implements a flowing wraparound layout.

    """
    #: Lines are filled from left to right and stacked top to bottom.
    LeftToRight = 0

    #: Lines are filled from right to left and stacked top to bottom.
    RightToLeft = 1

    #: Lines are filled from top to bottom and stacked left to right.
    TopToBottom = 2

    #: Lines are filled from bottom to top and stacked left to right.
    BottomToTop = 3

    #: Lines are aligned to their leading edge.
    AlignLeading = 4

    #: Lines are aligned to their trailing edge.
    AlignTrailing = 5

    #: Lines are aligned centered within any extra space.
    AlignCenter = 6

    #: Lines are aligned justified within any extra space.
    AlignJustify = 7

    def __init__(self):
        """ Initialize a QFlowLayout.

        """
        super(QFlowLayout, self).__init__()
        self._items = []
        self._options = _LayoutOptions()
        self._cached_w = -1
        self._cached_hfw = -1
        self._cached_min = None
        self._cached_hint = None
        self._wfh_size = None

    def addWidget(self, widget):
        """ Add a widget to the end of the flow layout.

        Parameters
        ----------
        widget : AbstractFlowWidget
            The flow widget to add to the layout.

        """
        self.insertWidget(self.count(), widget)

    def insertWidget(self, index, widget):
        """ Insert a widget into the flow layout.

        Parameters
        ----------
        index : int
            The index at which to insert the widget.

        widget : AbstractFlowWidget
            The flow widget to insert into the layout.

        """
        assert isinstance(widget, AbstractFlowWidget), 'invalid widget type'
        self.addChildWidget(widget)
        item = QFlowWidgetItem(widget, widget.layoutData())
        self._items.insert(index, item)
        widget.show()
        self.invalidate()

    def direction(self):
        """ Get the direction of the flow layout.

        Returns
        -------
        result : QFlowLayout direction enum
            The direction of the layout. The default is LeftToRight.

        """
        return self._options.direction

    def setDirection(self, direction):
        """ Set the direction of the flow layout.

        Parameters
        ----------
        direction : QFlowLayout direction enum
            The desired flow direction of the layout.

        """
        self._options.direction = direction
        self.invalidate()

    def alignment(self):
        """ Get the alignment for the lines in the layout.

        Returns
        -------
        result : QFlowLayout alignment enum
            The alignment of the lines in the layout. The default is
            AlignLeading.

        """
        return self._options.alignment

    def setAlignment(self, alignment):
        """ Set the alignment for the lines in the layout.

        Parameters
        ----------
        alignment : QFlowLayout alignment enum
            The desired alignment of the lines in the layout.

        """
        self._options.alignment = alignment
        self.invalidate()

    def horizontalSpacing(self):
        """ Get the horizontal spacing for the layout.

        Returns
        -------
        result : int
            The number of pixels of horizontal space between items in
            the layout. The default is 10px.

        """
        return self._options.h_spacing

    def setHorizontalSpacing(self, spacing):
        """ Set the horizontal spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of horizontal space to place between
            items in the layout.

        """
        self._options.h_spacing = spacing
        self.invalidate()

    def verticalSpacing(self):
        """ Get the vertical spacing for the layout.

        Returns
        -------
        result : int
            The number of pixels of vertical space between items in the
            layout. The default is 10px.

        """
        return self._options.v_spacing

    def setVerticalSpacing(self, spacing):
        """ Set the vertical spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of vertical space to place between
            items in the layout.

        """
        self._options.v_spacing = spacing
        self.invalidate()

    def hasHeightForWidth(self):
        """ Whether the height of the layout depends on its width.

        Returns
        -------
        result : bool
            True if the flow direction is horizontal, False otherwise.

        """
        return self._options.direction in (self.LeftToRight, self.RightToLeft)

    def heightForWidth(self, width):
        """ Get the height of the layout for the given width.

        This value only applies if `hasHeightForWidth` returns True.

        Parameters
        ----------
        width : int
            The width for which to determine a height.

        """
        if self._cached_w != width:
            left, top, right, bottom = self.getContentsMargins()
            adj_width = width - (left + right)
            height = self._doLayout(QRect(0, 0, adj_width, 0), True)
            self._cached_hfw = height + top + bottom
            self._cached_w = adj_width
        return self._cached_hfw

    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. The methods `addWidget` and
        `insertWidget` should be used instead.

        """
        msg = 'Use `addWidget` and `insertWidget` instead.'
        raise NotImplementedError(msg)

    def invalidate(self):
        """ Invalidate the cached values of the layout.

        """
        self._cached_w = -1
        self._cached_hfw = -1
        self._cached_wfh = -1
        self._cached_min = None
        self._cached_hint = None
        for item in self._items:
            item.invalidate()
        super(QFlowLayout, self).invalidate()

    def count(self):
        """ A virtual method implementation which returns the number of
        items in the layout.

        """
        return len(self._items)

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item
        for the given index or None if one does not exist.

        """
        items = self._items
        if idx < len(items):
            return items[idx]

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        items = self._items
        if idx < len(items):
            item = items[idx]
            del items[idx]
            item.widget().hide()
            # The creation path of the layout items bypasses the virtual
            # wrapper methods, this means that the ownership of the cpp
            # pointer is never transfered to Qt. If the item is returned
            # here it will be delete by Qt, which doesn't own the pointer.
            # A double free occurs once the Python item falls out of scope.
            # To avoid this, this method always returns None and the item
            # cleanup is performed by Python, which owns the cpp pointer.

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QFlowLayout, self).setGeometry(rect)
        self._doLayout(self.contentsRect())

    def sizeHint(self):
        """ A virtual method implementation which returns the size hint
        for the layout.

        """
        if self._cached_hint is None:
            size = QSize(0, 0)
            for item in self._items:
                size = size.expandedTo(item.sizeHint())
            left, top, right, bottom = self.getContentsMargins()
            size.setWidth(size.width() + left + right)
            size.setHeight(size.height() + top + bottom)
            self._cached_hint = size
        return self._cached_hint

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        if self._cached_min is None:
            size = QSize(0, 0)
            for item in self._items:
                size = size.expandedTo(item.minimumSize())
            left, top, right, bottom = self.getContentsMargins()
            size.setWidth(size.width() + left + right)
            size.setHeight(size.height() + top + bottom)
            self._cached_min = size
        # XXX hack! We really need hasWidthForHeight! This doesn't quite
        # work because a QScrollArea internally caches the min size.
        d = self._options.direction
        if d == self.TopToBottom or d == self.BottomToTop:
            m = QSize(self._cached_min)
            if m.width() < self._cached_wfh:
                m.setWidth(self._cached_wfh)
            return m
        return self._cached_min

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _doLayout(self, rect, test=False):
        """ Perform the layout for the given rect.

        Parameters
        ----------
        rect : QRect
            The area to use for performing the layout.

        test : bool, optional
            If True, perform a trial run of the layout without actually
            updating any of the item geometries.

        Returns
        -------
        result : int
            The layout space (width or height) required in the direction
            orthogonal to the layout flow.

        """
        d = self._options.direction
        if d == self.LeftToRight or d == self.RightToLeft:
            res = self._doHorizontalLayout(rect, test)
        else:
            res = self._doVerticalLayout(rect, test)
            # XXX hack! we need hasWidthForHeight
            self._cached_wfh = res + rect.x()
        return res

    def _doHorizontalLayout(self, rect, test):
        """ Perform the layout for a horizontal flow direction.

        The method signature is identical to the `_doLayout` method.

        """
        # Walk over the items and create the layout rows.
        rows = []
        width = rect.width()
        opts = self._options
        for item in self._items:
            if len(rows) == 0:
                row = _LayoutRow(width, opts)
                row.add_item(item)
                rows.append(row)
            else:
                row = rows[-1]
                if not row.add_item(item):
                    row = _LayoutRow(width, opts)
                    row.add_item(item)
                    rows.append(row)

        # After collecting rows all of the rows, compute the metrics. If
        # this is a test run, only the minimum height is required.
        space = opts.v_spacing * (len(rows) - 1)
        if test:
            return sum(row.min_height for row in rows) + space

        min_height = space
        hint_height = space
        total_diff = 0
        stretch = 0
        for row in rows:
            min_height += row.min_height
            hint_height += row.hint_height
            total_diff += row.diff_height
            stretch += row.stretch

        # Make an initial pass to distribute extra space to rows which
        # lie between their minimum height and desired height.
        height = rect.height()
        play_space = max(0, height - min_height)
        diff_space = max(total_diff, 1)  # Guard against divide by zero
        layout_height = 0
        for row in rows:
            d = play_space * row.diff_height / diff_space
            row.layout_height = min(row.min_height + d, row.hint_height)
            layout_height += row.layout_height
        layout_height += space

        # Make a second pass to distribute remaining space to rows
        # which with a stretch factor greater than zero.
        remaining = height - layout_height
        if remaining > 0 and stretch > 0:
            for row in rows:
                if row.stretch > 0:
                    row.layout_height += remaining * row.stretch / stretch

        # Make a final pass to layout the rows, computing the overall
        # final layout height along the way.
        final_height = 0
        x = rect.x()
        curr_y = rect.y()
        v_space = opts.v_spacing
        for row in rows:
            row.layout(x, curr_y)
            d = row.layout_height + v_space
            final_height += d
            curr_y += d

        return final_height

    def _doVerticalLayout(self, rect, test):
        """ Perform the layout for a vertical flow direction.

        The method signature is identical to the `_doLayout` method.

        """
        # Walk over the items and create the layout columns.
        cols = []
        height = rect.height()
        opts = self._options
        for item in self._items:
            if len(cols) == 0:
                col = _LayoutColumn(height, opts)
                col.add_item(item)
                cols.append(col)
            else:
                col = cols[-1]
                if not col.add_item(item):
                    col = _LayoutColumn(height, opts)
                    col.add_item(item)
                    cols.append(col)

        # After collecting rows all of the columns, compute the metrics.
        # If this is a test run, only the minimum width is required.
        space = opts.h_spacing * (len(cols) - 1)
        if test:
            return sum(col.min_width for col in cols) + space

        min_width = space
        hint_width = space
        total_diff = 0
        stretch = 0
        for col in cols:
            min_width += col.min_width
            hint_width += col.hint_width
            total_diff += col.diff_width
            stretch += col.stretch

        # Make an initial pass to distribute extra space to columns
        # which lie between their minimum width and desired width.
        width = rect.width()
        play_space = max(0, width - min_width)
        diff_space = max(total_diff, 1)  # Guard against divide by zero
        layout_width = 0
        for col in cols:
            d = play_space * col.diff_width / diff_space
            col.layout_width = min(col.min_width + d, col.hint_width)
            layout_width += col.layout_width
        layout_width += space

        # Make a second pass to distribute remaining space to columns
        # which with a stretch factor greater than zero.
        remaining = width - layout_width
        if remaining > 0 and stretch > 0:
            for col in cols:
                if col.stretch > 0:
                    col.layout_width += remaining * col.stretch / stretch

        # Make a final pass to layout the columns, computing the overall
        # final layout width along the way.
        final_width = 0
        y = rect.y()
        curr_x = rect.x()
        h_space = opts.h_spacing
        for col in cols:
            col.layout(curr_x, y)
            d = col.layout_width + h_space
            final_width += d
            curr_x += d

        return final_width


class _LayoutOptions(object):
    """ A private class used by QFlowLayout to store layout options.

    """
    #: The flow direction of the layout.
    direction = QFlowLayout.LeftToRight

    #: The alignment of a line in the layout.
    alignment = QFlowLayout.AlignLeading

    #: The horizontal spacing between items or lines in the layout.
    h_spacing = 10

    #: The vertical spacing between items or lines in the layout.
    v_spacing = 10
