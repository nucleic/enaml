#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque
from contextlib import contextmanager

from atom.api import Atom, Callable, Float, ForwardTyped, List, Tuple, Typed

import kiwisolver as kiwi

from enaml.layout.layout_helpers import expand_constraints
from enaml.widgets.container import ProxyContainer

from .QtCore import QSize, QTimer, Signal
from .QtGui import QFrame

from .qt_constraints_widget import QtConstraintsWidget, ConstraintCache
from .qt_frame import QtFrame


def hard_constraints(d):
    """ Generate hard constraints for a constraints object.

    The hard constraints restrict the object so that its origin
    and size are both greater than or equal to zero.

    Parameters
    ----------
    d : Constrainable
        The constrainable declaration object which owns the
        constraint variables.

    Returns
    -------
    result : list
        A list of Constraint objects.

    """
    return [d.left >= 0, d.top >= 0, d.width >= 0, d.height >= 0]


def size_hint_constraints(d, hint):
    """ Generate the size hint constraints for a constraints object.

    The size hint constraints are generated based on the values of the
    component's resist_*, hug_*, and limit_* attributes. If the value
    of the hint is less than zero in a dimension, that dimension is
    ignored.

    Parameters
    ----------
    d : Constrainable
        The constrainable declaration object which owns the
        constraint variables.

    hint : tuple
        A 2-tuple of ints representing the width and height hint.

    Returns
    -------
    result : list
        A list of Constraint objects.

    """
    cns = []
    w, h = hint
    if w >= 0:
        if d.hug_width != 'ignore':
            cns.append((d.width == w) | d.hug_width)
        if d.resist_width != 'ignore':
            cns.append((d.width >= w) | d.resist_width)
        if d.limit_width != 'ignore':
            cns.append((d.width <= w) | d.limit_width)
    if h >= 0:
        if d.hug_height != 'ignore':
            cns.append((d.height == h) | d.hug_height)
        if d.resist_height != 'ignore':
            cns.append((d.height >= h) | d.resist_height)
        if d.limit_height != 'ignore':
            cns.append((d.height <= h) | d.limit_height)
    return cns


def margins_constraints(d, margins):
    """ Generate the margin constraints for a container object.

    The margin constraints establish the relationships between the
    boundary box of a container and its contents box.

    Parameters
    ----------
    d : Container
        The container declaration object which owns the constraint
        variables.

    margins : tuple
        A 4-tuple of ints representing the top, right, bottom, and
        left contents margins of the widget.

    Returns
    -------
    result : list
        A list of Constraint objects.

    """
    top, right, bottom, left = map(sum, zip(d.padding, margins))
    cns = [d.contents_top == (d.top + top),
           d.contents_left == (d.left + left),
           d.contents_right == (d.right - right),
           d.contents_bottom == (d.bottom - bottom)]
    return cns


def can_shrink_in_width(d):
    """ Test whether a declarative container can shrink in width.

    """
    shrink = ('ignore', 'weak')
    return d.resist_width in shrink and d.hug_width in shrink


def can_shrink_in_height(d):
    """ Test whether a declarative container can shrink in height.

    """
    shrink = ('ignore', 'weak')
    return d.resist_height in shrink and d.hug_height in shrink


def can_expand_in_width(d):
    """ Test whether a declarative container can expand in width.

    """
    expand = ('ignore', 'weak')
    return d.hug_width in expand and d.limit_width in expand


def can_expand_in_height(d):
    """ Test whether a declarative container can expand in height.

    """
    expand = ('ignore', 'weak')
    return d.hug_height in expand and d.limit_height in expand


class ContainerConstraintCache(ConstraintCache):
    """ A constraint cached extended for use by containers.

    """
    #: The list of cached margins constraints.
    margins = List()


class LayoutPoint(Atom):
    """ A class which represents a point in the layout space.

    """
    #: The x-coordinate of the point.
    x = Float(0.0)

    #: The y-coordinate of the point.
    y = Float(0.0)


class LayoutItem(Atom):
    """ An item used to assemble the layout table for the container.

    """
    #: The constraint widget which will be updated by this item.
    #: The instance will be assigned by the container when it
    #: builds the layout table.
    item = Typed(QtConstraintsWidget)

    #: The offset to apply to the widget when updating. This point
    #: may be shared among multiple layout items. The instance will
    #: be assigned by the container when it builds the layout table.
    offset = Typed(LayoutPoint)

    #: The origin point to update with the origin data. This point
    #: may be used as the offset point for other layout items. The
    #: instance will be assigned by the container when it builds the
    #: layout table.
    origin = Typed(LayoutPoint)

    def update_geometry(self):
        """ Update the underlying constraint widget geometry.

        """
        offset = self.offset
        origin = self.origin
        origin.x, origin.y = self.item.update_geometry(offset.x, offset.y)


class BaseHandler(Atom):
    """ A base class for creating container layout handlers.

    """
    #: The container which owns the layout for the handler.
    owner = ForwardTyped(lambda: QtContainer)

    def __init__(self, owner):
        """ Initialize a BaseHandler.

        Parameters
        ----------
        owner : QtContainer
            The container which owns the layout for the handler.

        """
        self.owner = owner


class SizeHintHandler(BaseHandler):
    """ A layout handler which handles size hint updates.

    """
    def __call__(self, item):
        """ Notify the owner container of a size hint change.

        Parameters
        ----------
        item : QtConstraintsWidget
            The constraints widget of interest.

        """
        owner = self.owner
        if owner is not None:
            owner._on_size_hint_updated(item)


class MarginsHandler(BaseHandler):
    """ A layout handler which handles contents margins updates.

    """
    def __call__(self, item):
        """ Notify the owner container of a margin change.

        Parameters
        ----------
        item : QtContainer
            The container widget of interest.

        """
        owner = self.owner
        if owner is not None:
            owner._on_margins_updated(item)


class RelayoutHandler(BaseHandler):
    """ A layout handler which handles relayout requests.

    """
    def __call__(self):
        """ Request a relayout of the owner container.

        """
        owner = self.owner
        if owner is not None:
            owner._on_request_relayout()


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

    #: The constraint cache for this container.
    constraint_cache = Typed(ContainerConstraintCache, ())

    #: A timer used to collapse relayout requests. The timer is created
    #: on an as needed basis and destroyed when it is no longer needed.
    _layout_timer = Typed(QTimer)

    #: The list of LayoutItems to update during a layout resize pass.
    _layout_table = List()

    #: The tuple of layout_handlers installed on decendant widgets.
    _layout_handlers = Tuple()

    #: The constraint solver for this container. This will be None if
    #: the container has transfered layout ownership to an ancestor.
    _solver = Typed(kiwi.Solver)

    #: The stack of edit variables added to the solver.
    _edit_stack = List()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor clears the layout timer, handlers and table
        so that any potential reference cycles are broken.

        """
        del self._layout_timer
        del self._layout_table
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
        self._setup_solver()
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

        This method forwards the update to the layout notifier.

        """
        handler = self.margins_handler
        if handler is not None:
            handler(self)

    #--------------------------------------------------------------------------
    # Private LayoutHandling
    #--------------------------------------------------------------------------
    def _on_size_hint_updated(self, item):
        """ Handle a size hint change on a child widget.

        This method will replace the size hint constraints for the item.

        Parameters
        ----------
        item : QtConstraintsWidget
            The constraints widget of interest.

        """
        cache = item.constraint_cache
        old_cns = cache.size_hint
        hint = item.widget_item.sizeHint()
        hint = (hint.width(), hint.height())
        new_cns = size_hint_constraints(item.declaration, hint)
        cache.size_hint = new_cns
        self._replace_constraints(old_cns, new_cns)

    def _on_margins_updated(self, item):
        """ Handle a contents margins change on a child widget.

        This method will replace the margin constraints for the item.

        Parameters
        ----------
        item : QtContainer
            The container widget of interest.

        """
        cache = item.constraint_cache
        old_cns = cache.margins
        margins = item.contents_margins()
        new_cns = margins_constraints(item.declaration, margins)
        cache.margins = new_cns
        self._replace_constraints(old_cns, new_cns)

    def _on_request_relayout(self):
        """ Handle a relayout request.

        This method will (re)start a single shot timer which will
        rebuild the layout when triggered.

        """
        # Drop the reference to the layout table. This prevents an edge
        # case scenario where a parent container layout occurs before
        # the child container, causing the child to resize potentially
        # deleted widgets which still have strong refs in the table.
        del self._layout_table
        if self._layout_timer is None:
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
            self._setup_solver()
            self._update_sizes()
            self._update_geometries()
        self.widget.setUpdatesEnabled(True)

    def _push_edit_vars(self, pairs):
        """ Push edit variables into the solver.

        The current edit variables will be removed and the new edit
        variables will be added.

        Parameters
        ----------
        pairs : sequence
            A sequence of 2-tuples of (var, strength) which should be
            added as edit variables to the solver.

        """
        solver = self._solver
        stack = self._edit_stack
        if len(stack) > 0:
            for v, strength in stack[-1]:
                solver.removeEditVariable(v)
        stack.append(pairs)
        for v, strength in pairs:
            solver.addEditVariable(v, strength)

    def _pop_edit_vars(self):
        """ Restore the previous edit variables in the solver.

        The current edit variables will be removed and the previous
        edit variables will be re-added.

        """
        solver = self._solver
        stack = self._edit_stack
        for v, strength in stack.pop():
            solver.removeEditVariable(v)
        if len(stack) > 0:
            for v, strength in stack[-1]:
                solver.addEditVariable(v, strength)

    @contextmanager
    def _edit_context(self, pairs):
        """ A context manager for temporary solver edits.

        This manager will push the edit vars into the solver and pop
        them when the context exits.

        Parameters
        ----------
        pairs : list
            A list of 2-tuple of (var, strength) which should be added
            as temporary edit variables to the solver.

        """
        self._push_edit_vars(pairs)
        yield
        self._pop_edit_vars()

    def _setup_solver(self):
        """ Setup the layout solver.

        This method will create or reset the layout solver and populate
        it with the constraints for the system. After this method is
        called the container will be ready to effectively respond to
        resize events.

        """
        # Layout ownership can only be transferred *after* the init
        # layout method is called, as layout occurs bottom up. A solver
        # is only initialized if ownership is unlikely to change.
        d = self.declaration
        if d.share_layout and isinstance(self.parent(), QtContainer):
            # XXX should an old solver be deleted here? This only
            # matters when share_layout is changed dynamically.
            return

        # Resetting is faster than creating from scratch.
        solver = self._solver
        if solver is None:
            solver = self._solver = kiwi.Solver()
        else:
            solver.reset()

        # Create a new layout table and layout handlers, and populate
        # the solver with the constraints for the system.
        self._layout_table = self._create_layout_table()
        self._setup_layout_handlers()
        for cn in self._create_constraints():
            solver.addConstraint(cn)

        # Add the edit variables which are used during resizes.
        d = self.declaration
        s = kiwi.strength.medium
        pairs = ((d.width, s), (d.height, s))
        self._push_edit_vars(pairs)

    def _update_geometries(self):
        """ Update the geometries of the layout children.

        This method will suggest the current container size to the
        solver and then pass over the layout table to update the
        layout children.

        """
        solver = self._solver
        if solver is not None:
            d = self.declaration
            widget = self.widget
            solver.suggestValue(d.width, widget.width())
            solver.suggestValue(d.height, widget.height())
            solver.updateVariables()
            for layout_item in self._layout_table:
                layout_item.update_geometry()

    def _update_sizes(self):
        """ Update the sizes of the underlying container.

        This method will update the min, max, and best size of the
        container. It will not automatically trigger a size hint
        notification.

        """
        widget = self.widget
        widget.setSizeHint(self._compute_best_size())
        if not isinstance(widget.parent(), QContainer):
            # Only set min and max size if the parent is not a container.
            # The solver needs to be the ultimate authority when dealing
            # with nested containers, since QWidgetItem respects min and
            # max size when calling setGeometry().
            widget.setMinimumSize(self._compute_min_size())
            widget.setMaximumSize(self._compute_max_size())

    def _compute_best_size(self):
        """ Compute the best size for the container.

        The best size is computed by invoking the solver with a zero
        size suggestion at a strength of 0.1 * weak. The resulting
        values for width and height are taken as the best size.

        Returns
        -------
        result : QSize
            The best size for the container.

        """
        solver = self._solver
        if solver is None:
            return QSize()
        d = self.declaration
        w = d.width
        h = d.height
        s = 0.1 * kiwi.strength.weak
        pairs = ((w, s), (h, s))
        with self._edit_context(pairs):
            solver.suggestValue(w, 0.0)
            solver.suggestValue(h, 0.0)
            solver.updateVariables()
            result = QSize(w.value(), h.value())
        return result

    def _compute_min_size(self):
        """ Compute the minimum size for the container.

        The minimum size is computed by invoking the solver with a
        zero size suggestion at a strength of medium. The resulting
        values for width and height are taken as the minimum size.

        If the size hint constraints for the container indicate that
        it can shrink in width and height, then the solver step is
        skipped and a zero size is returned.

        Returns
        -------
        result : QSize
            The minimum size for the container.

        """
        solver = self._solver
        if solver is None:
            return QSize(0, 0)
        d = self.declaration
        shrink_w = can_shrink_in_width(d)
        shrink_h = can_shrink_in_height(d)
        if shrink_w and shrink_h:
            return QSize(0, 0)
        w = d.width
        h = d.height
        solver.suggestValue(w, 0.0)
        solver.suggestValue(h, 0.0)
        solver.updateVariables()
        return QSize(w.value(), h.value())

    def _compute_max_size(self):
        """ Compute the maximum size for the container.

        The maximum size is computed by invoking the solver with a
        max size suggestion at a strength of medium. The resulting
        values for width and height are taken as the maximum size.

        If the size hint constraints for the container indicate that
        it can expand in width and height, then the solver stop is
        passed and a max size is returned.

        Returns
        -------
        result : QSize
            The maximum size for the container.

        """
        max_v = 16777215
        solver = self._solver
        if solver is None:
            return QSize(max_v, max_v)
        d = self.declaration
        expand_w = can_expand_in_width(d)
        expand_h = can_expand_in_height(d)
        if expand_w and expand_h:
            return QSize(max_v, max_v)
        w = d.width
        h = d.height
        solver.suggestValue(w, max_v)
        solver.suggestValue(h, max_v)
        solver.updateVariables()
        return QSize(w.value(), h.value())

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
        # The layout table is created by traversing the decendants in
        # breadth-first order and setting up a LayoutItem object for
        # each decendant. The layout item is populated with an offset
        # point which represents the offset of the widgets parent to
        # the origin of the widget which owns the layout solver. This
        # point is substracted from the solved origin of the widget.
        table = []
        offset = LayoutPoint()
        queue = deque((offset, child) for child in self.children())
        while queue:
            offset, child = queue.popleft()
            if isinstance(child, QtConstraintsWidget):
                item = LayoutItem()
                item.item = child
                item.offset = offset
                item.origin = LayoutPoint()
                table.append(item)
                if isinstance(child, QtContainer):
                    if child.declaration.share_layout:
                        s_offset = item.origin
                        for s_child in child.children():
                            queue.append((s_offset, s_child))
        return table

    def _clear_layout_handlers(self):
        """ Clear the layout handlers for this container.

        This will reset all layout handlers which have this container
        as its owner object, thus preventing any further notifications
        from those handlers, as well as breaking the reference cycle.

        """
        handler = self.relayout_handler
        if handler is not None and handler.owner is self:
            handler.owner = None
            self.relayout_handler = None
        handler = self.size_hint_handler
        if handler is not None and handler.owner is self:
            handler.owner = None
            self.size_hint_handler = None
        handler = self.margins_handler
        if handler is not None and handler.owner is self:
            handler.owner = None
            self.margins_handler = None
        for handler in self._layout_handlers:
            handler.owner = None
        del self._layout_handlers

    def _setup_layout_handlers(self):
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
        for layout_item in self._layout_table:
            child = layout_item.item
            if isinstance(child, QtContainer):
                if child.declaration.share_layout:
                    child.relayout_handler = rl_handler
                    child.margins_handler = mg_handler
                else:
                    child.size_hint_handler = sh_handler
            else:
                child.relayout_handler = rl_handler
                child.size_hint_handler = sh_handler

    def _create_constraints(self):
        """ Create the constraints for the current layout table.

        This method will make a pass over the current items in the
        layout table and generate a complete list of constraints
        for the total layout system.

        Returns
        -------
        result : list
            A list of kiwi Constraint objects.

        """
        d = self.declaration
        cns = []

        # Start with the constraints for this container. The size hint
        # constraints of the container are irrelevant. Only ancestor
        # containers will care about those.
        hc = hard_constraints(d)
        mc = margins_constraints(d, self.contents_margins())
        lc = expand_constraints(d, d.layout_constraints())
        self.constraint_cache.margins = mc
        cns.extend(hc)
        cns.extend(mc)
        cns.extend(lc)

        # Do the same for each item in the layout table. Containers
        # are handled specially based on whether they share layout.
        for layout_item in self._layout_table:
            child = layout_item.item
            d = child.declaration
            if isinstance(child, QtContainer):
                if d.share_layout:
                    hc = hard_constraints(d)
                    mc = margins_constraints(d, child.contents_margins())
                    lc = expand_constraints(d, d.layout_constraints())
                    child.constraint_cache.margins = mc
                    cns.extend(hc)
                    cns.extend(mc)
                    cns.extend(lc)
                else:
                    hc = hard_constraints(d)
                    hint = child.widget_item.sizeHint()
                    hint = (hint.width(), hint.height())
                    sc = size_hint_constraints(d, hint)
                    child.constraint_cache.size_hint = sc
                    cns.extend(hc)
                    cns.extend(sc)
            else:
                hc = hard_constraints(d)
                hint = child.widget_item.sizeHint()
                hint = (hint.width(), hint.height())
                sc = size_hint_constraints(d, hint)
                lc = expand_constraints(d, d.layout_constraints())
                child.constraint_cache.size_hint = sc
                cns.extend(hc)
                cns.extend(sc)
                cns.extend(lc)

        return cns

    def _replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the layout solver.

        This method will swap the old constraints with the new ones,
        and update the sizes of the container and the geometries of
        the layout children.

        """
        solver = self._solver
        if solver is not None:
            with self.size_hint_guard():
                for cn in old_cns:
                    solver.removeConstraint(cn)
                for cn in new_cns:
                    solver.addConstraint(cn)
                self._update_sizes()
                self._update_geometries()
