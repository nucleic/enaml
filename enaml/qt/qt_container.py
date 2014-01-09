#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque

from atom.api import Atom, Callable, ForwardTyped, Tuple, Typed

from enaml.layout.layout_manager import LayoutManager
from enaml.widgets.container import ProxyContainer

from .QtCore import QSize, QTimer, Signal
from .QtGui import QFrame

from .qt_constraints_widget import QtConstraintsWidget, QtLayoutItem, Point
from .qt_frame import QtFrame


class BaseLayoutHandler(Atom):
    """ A base class for creating container layout handlers.

    """
    #: The container which owns the layout for the handler.
    container = ForwardTyped(lambda: QtContainer)

    def __init__(self, container):
        """ Initialize a BaseLayoutHandler.

        Parameters
        ----------
        container : QtContainer
            The container which owns the layout for the handler.

        """
        self.container = container


class SizeHintHandler(BaseLayoutHandler):
    """ A layout handler which handles size hint updates.

    """
    def __call__(self, item):
        """ Notify the container of a size hint change.

        Parameters
        ----------
        item : QtLayoutItem
            The layout item of interest.

        """
        container = self.container
        if container is not None:
            container._on_size_hint_updated(item)


class MarginsHandler(BaseLayoutHandler):
    """ A layout handler which handles contents margins updates.

    """
    def __call__(self, item):
        """ Notify the container of a margin change.

        Parameters
        ----------
        item : QtLayoutItem
            The layout item of interest.

        """
        container = self.container
        if container is not None:
            container._on_margins_updated(item)


class RelayoutHandler(BaseLayoutHandler):
    """ A layout handler which handles relayout requests.

    """
    def __call__(self):
        """ Request a relayout of the container.

        """
        container = self.container
        if container is not None:
            container._on_request_relayout()


class QtContainerItem(QtLayoutItem):
    """ A QtLayoutItem subclass which handles container margins.

    """
    def margins(self):
        """ Get the margins for the underlying widget.

        Returns
        -------
        result : tuple
            A 4-tuple of ints representing the container margins.

        """
        a, b, c, d = self.owner.declaration.padding
        e, f, g, h = self.owner.contents_margins()
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

        A child container does not expose its user constraints.

        """
        return []


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

    #: The margins updated handler for the widget. This is assigned
    #: by an ancestor container during the layout building pass.
    margins_handler = Callable()

    #: A timer used to collapse relayout requests. The timer is created
    #: on an as needed basis and destroyed when it is no longer needed.
    _layout_timer = Typed(QTimer)

    #: The layout manager which handles the system of constraints.
    _layout_manager = Typed(LayoutManager)

    #: The tuple of layout_handlers installed on decendant widgets.
    _layout_handlers = Tuple()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor clears the layout timer, manager and handlers
        so that any potential reference cycles are broken.

        """
        del self._layout_timer
        del self._layout_manager
        self._clear_layout_handlers()
        super(QtContainer, self).destroy()

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the QContainer widget.

        """
        self.widget = QContainer(self.parent_widget())

    def init_layout(self):
        """ Initialize the layout of the widget.

        """
        super(QtContainer, self).init_layout()
        self._setup_manager()
        self._update_sizes()
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

    #--------------------------------------------------------------------------
    # Layout API
    #--------------------------------------------------------------------------
    def contents_margins(self):
        """ Get the contents margins for the container.

        The contents margins are added to the user provided padding
        to determine the final offset from a layout box boundary to
        the corresponding content line. The default content margins
        are zero. This method can be reimplemented by subclasses to
        supply different margins.

        Returns
        -------
        result : tuple
            A tuple of 'top', 'right', 'bottom', 'left' contents
            margins to use for computing the contents constraints.

        """
        return (0, 0, 0, 0)

    def contents_margins_updated(self):
        """ Notify the layout system that the margins have changed.

        This method forwards the update to the layout handler.

        """
        handler = self.margins_handler
        if handler is not None:
            item = self.layout_item
            if item is not None:
                handler(item)

    #--------------------------------------------------------------------------
    # Private Layout Handling
    #--------------------------------------------------------------------------
    def _on_size_hint_updated(self, item):
        """ Handle a size hint change on a child widget.

        Parameters
        ----------
        item : QtLayoutItem
            The layout item with the updated size hint.

        """
        print 'size hint', self, item.owner
        manager = self._layout_manager
        if manager is not None:
            with self.size_hint_guard():
                manager.update_size_hint(item)
                self._update_sizes()
                self._update_geometries()

    def _on_margins_updated(self, item):
        """ Handle a contents margins change on a child widget.

        Parameters
        ----------
        item : QtLayoutItem
            The layout item with the updated margins.

        """
        manager = self._layout_manager
        if manager is not None:
            with self.size_hint_guard():
                manager.update_margins(item)
                self._update_sizes()
                self._update_geometries()

    def _on_request_relayout(self):
        """ Handle a relayout request.

        """
        if self._layout_timer is None:
            # Drop the reference to the layout table. This prevents an
            # edge case scenario where a parent container layout occurs
            # before the child container, causing the child to resize
            # potentially deleted widgets which still have strong refs
            # in the table.
            del self._layout_table
            manager = self._layout_manager
            if manager is not None:
                manager.set_table([])
            self.widget.setUpdatesEnabled(False)
            timer = self._layout_timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(self._on_relayout_timer)
        self._layout_timer.start()

    def _on_relayout_timer(self):
        """ Rebuild the layout for the container.

        This method is invoked when the relayout timer is triggered. It
        will reset the solver and update the geometries of the children.

        """
        del self._layout_timer
        with self.size_hint_guard():
            self._setup_manager()
            self._update_sizes()
            self._update_geometries()
        self.widget.setUpdatesEnabled(True)

    def _setup_manager(self):
        """ Setup the layout manager.

        This method will create or reset the layout manager and update
        it with a new layout table.

        """
        # Layout ownership can only be transferred *after* the init
        # layout method is called, as layout occurs bottom up. The
        # manager is only created if ownership is unlikely to change.
        #
        # XXX should an old manager be deleted here? This only
        # matters when share_layout is changed dynamically.
        share_layout = self.declaration.share_layout
        if share_layout and isinstance(self.parent(), QtContainer):
            return

        this_item = QtContainerItem()
        this_item.owner = self
        this_item.origin = Point()
        this_item.offset = Point()
        self.layout_item = this_item

        table = self._create_layout_table()
        self._setup_layout_handlers(table)

        manager = self._layout_manager
        if manager is None:
            manager = self._layout_manager = LayoutManager(this_item)
        manager.set_table(table)

    def _update_geometries(self):
        """ Update the geometries of the layout children.

        This method will resize the layout manager to the container size.

        """
        manager = self._layout_manager
        if manager is not None:
            widget = self.widget
            manager.resize(widget.width(), widget.height())

    def _update_sizes(self):
        """ Update the sizes of the underlying container.

        This method will update the min, max, and best size of the
        container. It will not automatically trigger a size hint
        notification.

        """
        widget = self.widget
        manager = self._layout_manager
        if manager is None:
            widget.setSizeHint(QSize(-1, -1))
            widget.setMinimumSize(QSize(0, 0))
            widget.setMaximumSize(QSize(16777215, 16777215))
            return
        widget.setSizeHint(QSize(*manager.best_size()))
        if not isinstance(widget.parent(), QContainer):
            # Only set min and max size if the parent is not a container.
            # The manager needs to be the ultimate authority when dealing
            # with nested containers, since QWidgetItem respects min and
            # max size when calling setGeometry().
            widget.setMinimumSize(QSize(*manager.min_size()))
            widget.setMaximumSize(QSize(*manager.max_size()))

    def _create_layout_table(self):
        """ Create a layout table for container decendants.

        The layout table is created by traversing the decendants in
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
        table = []
        offset = Point()
        queue = deque((offset, child) for child in self.children())
        while queue:
            offset, child = queue.popleft()
            if isinstance(child, QtConstraintsWidget):
                origin = Point()
                if isinstance(child, QtContainer):
                    if child.declaration.share_layout:
                        item = QtSharedContainerItem()
                        for s_child in child.children():
                            queue.append((origin, s_child))
                    else:
                        item = QtChildContainerItem()
                else:
                    item = QtLayoutItem()
                item.owner = child
                item.offset = offset
                item.origin = origin
                table.append(item)
        return table

    def _clear_layout_handlers(self):
        """ Clear the layout handlers for this container.

        This will reset all layout handlers which have this container
        as its owner object, thus preventing any further notifications
        from those handlers, as well as breaking the reference cycle.

        """
        handler = self.relayout_handler
        if handler is not None and handler.container is self:
            handler.container = None
            self.relayout_handler = None
        handler = self.size_hint_handler
        if handler is not None and handler.container is self:
            handler.container = None
            self.size_hint_handler = None
        handler = self.margins_handler
        if handler is not None and handler.container is self:
            handler.container = None
            self.margins_handler = None
        for handler in self._layout_handlers:
            handler.container = None
        del self._layout_handlers

    def _setup_layout_handlers(self, table):
        """ Setup the layout handlers for the current layout table.

        This method will first clear the old handlers and then make a
        pass over the current layout table, installing the new handlers
        as needed.

        """
        self._clear_layout_handlers()
        rl_handler = RelayoutHandler(self)
        sh_handler = SizeHintHandler(self)
        mg_handler = MarginsHandler(self)
        self._layout_handlers = (rl_handler, sh_handler, mg_handler)

        # A container which owns its layout handles its own
        # relayout requests and contents margin changes.
        self.relayout_handler = rl_handler
        self.margins_handler = mg_handler

        # Assign the handlers to the child constraint widgets. If a
        # container can share its layout, its size hint is ignored.
        # If a container does not share its layout, this container
        # only cares about its size hint.
        for layout_item in table:
            child = layout_item.owner
            if isinstance(child, QtContainer):
                if child.declaration.share_layout:
                    child.relayout_handler = rl_handler
                    child.margins_handler = mg_handler
                else:
                    child.size_hint_handler = sh_handler
            else:
                child.relayout_handler = rl_handler
                child.size_hint_handler = sh_handler
