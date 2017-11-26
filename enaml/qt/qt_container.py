#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque
from contextlib import contextmanager

from atom.api import Atom, Callable, Float, Typed

from enaml.layout.layout_manager import LayoutItem, LayoutManager
from enaml.widgets.constraints_widget import ConstraintsWidget
from enaml.widgets.container import ProxyContainer

from .QtCore import QRect, QSize, QTimer, Signal
from .QtWidgets import QFrame, QWidgetItem, QSizePolicy

from .qt_constraints_widget import QtConstraintsWidget
from .qt_frame import QtFrame


# Commonly used default sizes
DEFAULT_BEST_SIZE = QSize(-1, -1)
DEFAULT_MIN_SIZE = QSize(0, 0)
DEFAULT_MAX_SIZE = QSize(16777215, 16777215)

# The size policy to apply to containers. This allows the container
# to behave properly when added to standard Qt layouts and widgets.
CONTAINER_POLICY = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class LayoutPoint(Atom):
    """ A class which represents a point in layout space.

    """
    #: The x-coordinate of the point.
    x = Float(0.0)

    #: The y-coordinate of the point.
    y = Float(0.0)


class QtLayoutItem(LayoutItem):
    """ A concrete LayoutItem implementation for a QtConstraintsWidget.

    """
    #: The constraints widget declaration object for the layout item.
    declaration = Typed(ConstraintsWidget)

    #: The widget item used for laying out the underlying widget.
    widget_item = Typed(QWidgetItem)

    #: The layout point which represents the offset of the parent item
    #: from the origin of the root item.
    offset = Typed(LayoutPoint)

    #: The layout point which represents the offset of this item from
    #: the offset of the root item.
    origin = Typed(LayoutPoint)

    def constrainable(self):
        """ Get a reference to the underlying constrainable object.

        Returns
        -------
        result : Constrainable
            An object which implements the Constrainable interface.

        """
        return self.declaration

    def margins(self):
        """ Get the margins for the underlying widget.

        Returns
        -------
        result : tuple
            An empty tuple as constraints widgets do not have margins.

        """
        return ()

    def size_hint(self):
        """ Get the size hint for the underlying widget.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            size hint of the widget.

        """
        hint = self.widget_item.sizeHint()
        return (hint.width(), hint.height())

    def min_size(self):
        """ Get the minimum size for the underlying widget.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            min size of the widget. If any value is less than zero,
            constraints will not be generated for that dimension.

        """
        min_size = self.widget_item.widget().minimumSize()
        if min_size != DEFAULT_MIN_SIZE:
            return (min_size.width(), min_size.height())
        return (-1, -1)

    def max_size(self):
        """ Get the maximum size for the underlying widget.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            max size of the widget. If any value is less than zero,
            constraints will not be generated for that dimension.

        """
        max_size = self.widget_item.widget().maximumSize()
        if max_size != DEFAULT_MAX_SIZE:
            return (max_size.width(), max_size.height())
        return (-1, -1)

    def constraints(self):
        """ Get the user-defined constraints for the item.

        Returns
        -------
        result : list
            The list of user-defined constraints.

        """
        return self.declaration.layout_constraints()

    def set_geometry(self, x, y, width, height):
        """ Set the geometry of the underlying widget.

        Parameters
        ----------
        x : float
            The new value for the x-origin of the widget.

        y : float
            The new value for the y-origin of the widget.

        width : float
            The new value for the width of the widget.

        height : float
            The new value for the height of the widget.

        """
        origin = self.origin
        origin.x = x
        origin.y = y
        offset = self.offset
        x -= offset.x
        y -= offset.y
        self.widget_item.setGeometry(QRect(x, y, width, height))


class QtContainerItem(QtLayoutItem):
    """ A QtLayoutItem subclass which handles container margins.

    """
    #: A callable used to get the container widget margins.
    margins_func = Callable()

    def margins(self):
        """ Get the margins for the underlying widget.

        Returns
        -------
        result : tuple
            A 4-tuple of ints representing the container margins.

        """
        a, b, c, d = self.declaration.padding
        e, f, g, h = self.margins_func(self.widget_item)
        return (a + e, b + f, c + g, d + h)


class QtSharedContainerItem(QtContainerItem):
    """ A QtContainerItem subclass which works for shared containers.

    """
    def size_hint_constraints(self):
        """ Get the size hint constraints for the item.

        A shared container does not generate size hint constraints.

        """
        return []


class QtChildContainerItem(QtLayoutItem):
    """ A QtLayoutItem subclass which works for child containers.

    """
    def constraints(self):
        """ Get the user constraints for the item.

        A child container does not expose its user defined constraints
        to the parent container.

        """
        return []

    def min_size(self):
        """ Get the minimum size for the underlying widget.

        The min size for a child container lives on the proxy object.
        The QWidgetItem limits must be bypassed for child container.

        """
        min_size = self.declaration.proxy.min_size
        if min_size != DEFAULT_MIN_SIZE:
            return (min_size.width(), min_size.height())
        return (-1, -1)

    def max_size(self):
        """ Get the maximum size for the underlying widget.

        The max size for a child container lives on the proxy object.
        The QWidgetItem limits must be bypassed for child container.

        """
        max_size = self.declaration.proxy.max_size
        if max_size != DEFAULT_MAX_SIZE:
            return (max_size.width(), max_size.height())
        return (-1, -1)


class QContainer(QFrame):
    """ A subclass of QFrame which behaves as a container.

    """
    #: A signal which is emitted on a resize event.
    resized = Signal()

    #: The internally cached size hint.
    _size_hint = QSize()

    def resizeEvent(self, event):
        """ Converts a resize event into a signal.

        """
        super(QContainer, self).resizeEvent(event)
        self.resized.emit()

    def sizeHint(self):
        """ Returns the previously set size hint. If that size hint is
        invalid, the superclass' sizeHint will be used.

        """
        hint = self._size_hint
        if not hint.isValid():
            hint = super(QContainer, self).sizeHint()
        return QSize(hint)

    def setSizeHint(self, hint):
        """ Sets the size hint to use for this widget.

        """
        self._size_hint = QSize(hint)

    def minimumSizeHint(self):
        """ Returns the minimum size hint for the widget.

        For a QContainer, the minimum size hint is equivalent to the
        minimum size as computed by the layout manager.

        """
        return self.minimumSize()


class QtContainer(QtFrame, ProxyContainer):
    """ A Qt implementation of an Enaml ProxyContainer.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QContainer)

    #: The minimum size of the container as computed by the layout
    #: manager. This will be updated on every relayout pass and is
    #: used by the QtChildContainerItem to generate size constraints.
    min_size = Typed(QSize)

    #: The maximum size of the container as computed by the layout
    #: manager. This will be updated on every relayout pass and is
    #: used by the QtChildContainerItem to generate size constraints.
    max_size = Typed(QSize)

    #: A timer used to collapse relayout requests. The timer is created
    #: on an as needed basis and destroyed when it is no longer needed.
    _layout_timer = Typed(QTimer)

    #: The layout manager which handles the system of constraints.
    _layout_manager = Typed(LayoutManager)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor clears the layout timer and layout manager
        so that any potential reference cycles are broken.

        """
        del self._layout_timer
        del self._layout_manager
        super(QtContainer, self).destroy()

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the QContainer widget.

        """
        widget = QContainer(self.parent_widget())
        widget.setSizePolicy(CONTAINER_POLICY)
        self.widget = widget

    def init_layout(self):
        """ Initialize the layout of the widget.

        """
        super(QtContainer, self).init_layout()
        self._setup_manager()
        self._update_size_bounds()
        self._update_geometries()
        self.widget.resized.connect(self._update_geometries)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event.

        This handler will reparent the child if necessary.

        """
        super(QtContainer, self).child_added(child)
        cw = child.widget
        if cw is not None and cw.parent() != self.widget:
            cw.setParent(self.widget)

    def child_removed(self, child):
        """ Handle the child removed event.

        This handler will clear the layout_parent member is applicable.

        """
        super(QtContainer, self).child_removed(child)
        if isinstance(child, QtConstraintsWidget):
            del child.layout_container

    #--------------------------------------------------------------------------
    # Layout API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout of the container.

        """
        # If this container owns the layout, (re)start the timer. The
        # list of layout items is cleared to prevent an edge case where
        # a parent container layout occurs before the child container,
        # causing the child to resize potentially deleted widgets which
        # still have strong refs in the layout items list.
        manager = self._layout_manager
        if manager is not None:
            if self._layout_timer is None:
                manager.clear_items()
                self.widget.setUpdatesEnabled(False)
                timer = self._layout_timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(self._on_relayout_timer)
            self._layout_timer.start()
            return

        # If an ancestor container owns the layout, proxy the call.
        container = self.layout_container
        if container is not None:
            container.request_relayout()

    def geometry_updated(self, item=None):
        """ Notify the layout system that the geometry has changed.

        Parameters
        ----------
        item : QtConstraintsWidget, optional
            The constraints widget with the updated geometry. If this
            is None, it indicates that this container's geometry is
            the one which has changed.

        """
        # If this container's geometry has changed and it has an ancestor
        # layout container, notify that container since it cares about
        # this container's geometry. If the layout for this container is
        # shared, the layout item will take care of supplying the proper
        # list geometry constraints.
        container = self.layout_container
        if item is None:
            if container is not None:
                container.geometry_updated(self)
            return

        # If this container owns its layout, update the manager unless
        # a relayout is pending. A pending relayout means the manager
        # has already been reset and the layout indices are invalid.
        manager = self._layout_manager
        if manager is not None:
            if self._layout_timer is None:
                with self.geometry_guard():
                    manager.update_geometry(item.layout_index)
                    self._update_size_bounds()
                    self._update_geometries()
            return

        # If an ancestor container owns the layout, proxy the call.
        if container is not None:
            container.geometry_updated(item)

    @contextmanager
    def geometry_guard(self):
        """ A context manager for guarding the geometry of the widget.

        This is a reimplementation of the superclass method which uses
        the internally computed min and max size of the container.

        """
        old_hint = self.widget.sizeHint()
        old_min = self.min_size
        old_max = self.max_size
        yield
        if (old_hint != self.widget.sizeHint() or
            old_min != self.min_size or
            old_max != self.max_size):
            self.geometry_updated()

    @staticmethod
    def margins_func(widget_item):
        """ Get the margins for the given widget item.

        The container margins are added to the user provided padding
        to determine the final offset from a layout box boundary to
        the corresponding content line. The default container margins
        are zero. This method can be reimplemented by subclasses to
        supply different margins.

        Returns
        -------
        result : tuple
            A 4-tuple of margins (top, right, bottom, left).

        """
        return (0, 0, 0, 0)

    def margins_updated(self, item=None):
        """ Notify the layout system that the margins have changed.

        Parameters
        ----------
        item : QtContainer, optional
            The container widget with the updated margins. If this is
            None, it indicates that this container's margins are the
            ones which have changed.

        """
        # If this container owns its layout, update the manager unless
        # a relayout is pending. A pending relayout means the manager
        # has already been reset and the layout indices are invalid.
        manager = self._layout_manager
        if manager is not None:
            if self._layout_timer is None:
                index = item.layout_index if item else -1
                with self.geometry_guard():
                    manager.update_margins(index)
                    self._update_size_bounds()
                    self._update_geometries()
            return

        # If an ancestor container owns the layout, forward the call.
        container = self.layout_container
        if container is not None:
            container.margins_updated(item or self)

    #--------------------------------------------------------------------------
    # Private Signal Handlers
    #--------------------------------------------------------------------------
    def _on_relayout_timer(self):
        """ Rebuild the layout for the container.

        This method is invoked when the relayout timer is triggered. It
        will reset the manager and update the geometries of the children.

        """
        del self._layout_timer
        with self.geometry_guard():
            self._setup_manager()
            self._update_size_bounds()
            self._update_geometries()
        self.widget.setUpdatesEnabled(True)

    #--------------------------------------------------------------------------
    # Private Layout Handling
    #--------------------------------------------------------------------------
    def _setup_manager(self):
        """ Setup the layout manager.

        This method will create or reset the layout manager and update
        it with a new layout table.

        """
        # Layout ownership can only be transferred *after* the init
        # layout method is called, as layout occurs bottom up. The
        # manager is only created if ownership is unlikely to change.
        share_layout = self.declaration.share_layout
        if share_layout and isinstance(self.parent(), QtContainer):
            del self._layout_timer
            del self._layout_manager
            return

        manager = self._layout_manager
        if manager is None:
            item = QtContainerItem()
            item.declaration = self.declaration
            item.widget_item = QWidgetItem(self.widget)
            item.origin = LayoutPoint()
            item.offset = LayoutPoint()
            item.margins_func = self.margins_func
            manager = self._layout_manager = LayoutManager(item)
        manager.set_items(self._create_layout_items())

    def _update_geometries(self):
        """ Update the geometries of the layout children.

        This method will resize the layout manager to the container size.

        """
        manager = self._layout_manager
        if manager is not None:
            widget = self.widget
            manager.resize(widget.width(), widget.height())

    def _update_size_bounds(self):
        """ Update the sizes of the underlying container.

        This method will update the min, max, and best size of the
        container. It will not automatically trigger a geometry
        notification.

        """
        widget = self.widget
        manager = self._layout_manager
        if manager is None:
            best_size = DEFAULT_BEST_SIZE
            min_size = DEFAULT_MIN_SIZE
            max_size = DEFAULT_MAX_SIZE
        else:
            best_size = QSize(*manager.best_size())
            min_size = QSize(*manager.min_size())
            max_size = QSize(*manager.max_size())

        # Store the computed min and max size, which is used by the
        # QtChildContainerItem to provide min and max size constraints.
        self.min_size = min_size
        self.max_size = max_size

        # If this is a child container, min and max size are not applied
        # to the widget since the ancestor manager must be the ultimate
        # authority on layout size, not QWidgetItem.
        widget.setSizeHint(best_size)
        if isinstance(self.parent(), QtContainer):
            widget.setMinimumSize(DEFAULT_MIN_SIZE)
            widget.setMaximumSize(DEFAULT_MAX_SIZE)
        else:
            widget.setMinimumSize(min_size)
            widget.setMaximumSize(max_size)

    def _create_layout_items(self):
        """ Create a layout items for the container decendants.

        The layout items are created by traversing the decendants in
        breadth-first order and setting up a LayoutItem object for
        each decendant. The layout item is populated with an offset
        point which represents the offset of the widgets parent to
        the origin of the widget which owns the layout solver. This
        point is substracted from the solved origin of the widget.

        Returns
        -------
        result : list
            A list of LayoutItem objects which represent the flat
            layout traversal.

        """
        layout_items = []
        offset = LayoutPoint()
        queue = deque((offset, child) for child in self.children())
        while queue:
            offset, child = queue.popleft()
            if isinstance(child, QtConstraintsWidget):
                child.layout_container = self
                origin = LayoutPoint()
                if isinstance(child, QtContainer):
                    if child.declaration.share_layout:
                        item = QtSharedContainerItem()
                        item.margins_func = child.margins_func
                        for subchild in child.children():
                            queue.append((origin, subchild))
                    else:
                        item = QtChildContainerItem()
                else:
                    item = QtLayoutItem()
                item.declaration = child.declaration
                item.widget_item = QWidgetItem(child.widget)
                item.offset = offset
                item.origin = origin
                child.layout_index = len(layout_items)
                layout_items.append(item)
        return layout_items
