#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque

from atom.api import Atom, List, Typed, Float

import kiwisolver as kiwi

from enaml.layout.layout_helpers import expand_constraints
from enaml.widgets.container import ProxyContainer

from .QtCore import QSize, QTimer, Signal
from .QtGui import QFrame

from .qt_constraints_widget import QtConstraintsWidget, ConstraintCache
from .qt_frame import QtFrame


def hard_constraints(o):
    """ Generate hard constraints for a constraints object.

    """
    d = o.declaration
    return [d.left >= 0, d.top >= 0, d.width >= 0, d.height >= 0]


def size_hint_constraints(o):
    """ Generate the size hint constraints for a constraints object.

    """
    cns = []
    hint = o.widget_item.sizeHint()
    if hint.isValid():
        d = o.declaration
        width_hint = hint.width()
        height_hint = hint.height()
        if width_hint >= 0:
            if d.hug_width != 'ignore':
                cns.append((d.width == width_hint) | d.hug_width)
            if d.resist_width != 'ignore':
                cns.append((d.width >= width_hint) | d.resist_width)
            if d.limit_width != 'ignore':
                cns.append((d.width <= width_hint) | d.limit_width)
        if height_hint >= 0:
            if d.hug_height != 'ignore':
                cns.append((d.height == height_hint) | d.hug_height)
            if d.resist_height != 'ignore':
                cns.append((d.height >= height_hint) | d.resist_height)
            if d.limit_height != 'ignore':
                cns.append((d.height <= height_hint) | d.limit_height)
    o.constraint_cache.size_hint = cns
    return cns


def contents_margins_constraints(o):
    """ Generate the contents constraints for a container object.

    """
    d = o.declaration
    margins = o.contents_margins()
    top, right, bottom, left = map(sum, zip(d.padding, margins))
    cns = [d.contents_top == (d.top + top),
           d.contents_left == (d.left + left),
           d.contents_right == (d.right - right),
           d.contents_bottom == (d.bottom - bottom)]
    o.constraint_cache.contents_margins = cns
    return cns


def can_shrink_in_width(d):
    """ Get whether a declarative container can shrink in width.

    """
    shrink = ('ignore', 'weak')
    return d.resist_width in shrink and d.hug_width in shrink


def can_shrink_in_height(d):
    """ Get whether a declarative container can shrink in height.

    """
    shrink = ('ignore', 'weak')
    return d.resist_height in shrink and d.hug_height in shrink


def can_expand_in_width(d):
    """ Get whether a declarative container can expand in width.

    """
    expand = ('ignore', 'weak')
    return d.hug_width in expand and d.limit_width in expand


def can_expand_in_height(d):
    """ Get whether a declarative container can expand in height.

    """
    expand = ('ignore', 'weak')
    return d.hug_height in expand and d.limit_height in expand


class ContainerConstraintCache(ConstraintCache):
    """ A constraint cached extended for use by containers.

    """
    #: The list of cached contents margins constraints.
    contents_margins = List()


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

    def update(self):
        """ Update the underlying constraint widget.

        """
        offset = self.offset
        origin = self.origin
        origin.x, origin.y = self.item.update_geometry(offset.x, offset.y)


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

    #: The constraint cache for this container.
    constraint_cache = Typed(ContainerConstraintCache, ())

    #: A timer used to collapse relayout requests. The timer is created
    #: on an as needed basis and destroyed when it is no longer needed.
    _layout_timer = Typed(QTimer)

    #: The list of LayoutItems to update during a layout resize pass.
    _layout_items = List()

    #: The constraint solver for this container. This will be None if
    #: the container has transfered layout ownership to an ancestor.
    _solver = Typed(kiwi.Solver)

    def destroy(self):
        """ An overridden destructor method.

        This drops the reference to the layout items.

        """
        del self._layout_items
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
        self.widget.resized.connect(self._update_geometries)
        self._setup_solver()  # XXX should this be before resized connect?

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
    def request_relayout(self):
        """ Request a relayout of the container.

        This method will collapse the relayout request on a timer, or
        forward the request to the ancestor container if ownership of
        the layout has been transfered.

        """
        container = self.layout_container
        if container is not None:
            container.request_relayout()
        else:
            # Drop the reference to the layout items. This prevents an
            # edge case scenario where a parent container layout occurs
            # before the child container, causing the child to resize
            # potentially deleted widgets still held as item refs.
            del self._layout_items
            if self._layout_timer is None:
                self.widget.setUpdatesEnabled(False)
                timer = self._layout_timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(self._on_layout_timer)
            self._layout_timer.start()

    def relayout(self):
        """ Rebuild the constraints layout for the container.

        """
        container = self.layout_container
        if container is not None:
            container.relayout()
        else:
            with self.size_hint_guard():
                self._setup_solver()
                self._update_geometries()

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

        This call will inform the relevant container of the change.

        """
        container = self.layout_container
        if container is not None:
            container.contents_margins_changed(self)
        else:
            self.contents_margins_changed(self)

    def contents_margins_changed(self, item):
        """ Notify the container the items margins have changed.

        This should not be called by user code. User code should
        instead invoke 'contents_margins_updated' on the desired
        item, and let the item invoke this method its associated
        container.

        Parameters
        ----------
        item : QtContainer
            The item which contains the new margins.

        """
        cache = item.constraint_cache
        old_cns = cache.contents_margins
        new_cns = contents_margins_constraints(item)
        cache.contents_margins = new_cns
        self._replace_constraints(old_cns, new_cns)

    def size_hint_changed(self, item):
        """ Notify the container the items size hint has changed.

        This should not be called by user code. User code should
        instead invoke 'size_hint_updated' on the desired item, and
        let the item invoke this method its associated container.

        Parameters
        ----------
        item : QtConstraintsWidget
            The item which contains the widget the new size hint.

        """
        cache = item.constraint_cache
        old_cns = cache.size_hint
        new_cns = size_hint_constraints(item)
        cache.size_hint = new_cns
        self._replace_constraints(old_cns, new_cns)

    def release_layout(self):
        """ Release the layout resources held by the container.

        This should not be called directly by user code. It is called
        by the framework at the appropriate times.

        """
        del self._layout_timer
        del self._layout_items
        del self._solver

    #--------------------------------------------------------------------------
    # Private Signal Handlers
    #--------------------------------------------------------------------------
    def _on_layout_timer(self):
        """ Handle the timeout event from the layout timer.

        This handler will drop the reference to the timer, invoke the
        'relayout' method, and reenable the updates on the widget.

        """
        del self._layout_timer
        self.relayout()
        self.widget.setUpdatesEnabled(True)

    def size_hint_updated(self):
        if self.layout_container is None:
            if isinstance(self.parent(), QtContainer):
                self.parent().size_hint_changed(self)

    #--------------------------------------------------------------------------
    # Private Layout Handling
    #--------------------------------------------------------------------------
    def _setup_solver(self):
        """ Setup and populate the layout solver and layout table.

        """
        # Layout ownership can only be transferred *after* the init
        # layout method is called, as layout occurs bottom up. A solver
        # is only initialized if ownership is unlikely to change.
        d = self.declaration
        if d.share_layout and isinstance(self.parent(), QtContainer):
            return

        solver = self._solver
        if solver is None:
            solver = self._solver = kiwi.Solver()
        else:
            solver.reset()

        self._build_layout_items()
        for cn in self._create_constraints():
            solver.addConstraint(cn)

        d = self.declaration
        solver.addEditVariable(d.width, kiwi.strength.medium)
        solver.addEditVariable(d.height, kiwi.strength.medium)

        self._update_sizes()

    def _update_geometries(self):
        """ Update the geometries of the layout items.

        """
        solver = self._solver
        if solver is not None:
            d = self.declaration
            widget = self.widget
            solver.suggestValue(d.width, widget.width())
            solver.suggestValue(d.height, widget.height())
            solver.updateVariables()
            for item in self._layout_items:
                item.update()

    def _replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the solver.

        This method can be used to add, remove, or replace constraints
        in the solver, when it is more efficient than a full relayout.

        Parameters
        ----------
        old_cns : list
            The list of constraints to remove from the solver.

        new_cns : list
            The list of constraints to add to the solver.

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
                #self._update_geometries()

    def _update_sizes(self):
        """ Update the min, max, and best sizes for the container.

        """
        widget = self.widget
        widget.setSizeHint(self._compute_best_size())
        if not isinstance(widget.parent(), QContainer):
            # Only set min and max size if the parent is not a container.
            # The layout manager needs to be the ultimate authority when
            # dealing with nested containers.
            widget.setMinimumSize(self._compute_min_size())
            widget.setMaximumSize(self._compute_max_size())

    def _compute_best_size(self):
        """ Calculates the best constraint size of the container.

        The best size of the container is obtained by computing the min
        size of the layout using a strength which is much weaker than a
        normal resize. This takes into account the size of any widgets
        which have their resist clip property set to 'weak' while still
        allowing the window to be resized smaller by the user. If the
        container does not own its layout, the returned size will be
        invalid.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the best size that
            will satisfy all constraints.

        """
        solver = self._solver
        if solver is None:
            return QSize()

        d = self.declaration
        w = d.width
        h = d.height

        # XXX this could be prettier by maintaining an edit context.

        if solver.hasEditVariable(w):
            solver.removeEditVariable(w)
        solver.addEditVariable(w, 0.1 * kiwi.strength.weak)

        if solver.hasEditVariable(h):
            solver.removeEditVariable(h)
        solver.addEditVariable(h, 0.1 * kiwi.strength.weak)

        solver.suggestValue(w, 0.0)
        solver.suggestValue(h, 0.0)
        solver.updateVariables()
        result = QSize(w.value(), h.value())

        solver.removeEditVariable(w)
        solver.removeEditVariable(h)
        solver.addEditVariable(w, kiwi.strength.medium)
        solver.addEditVariable(h, kiwi.strength.medium)

        return result

    def _compute_min_size(self):
        """ Calculates the minimum constraint size of the container.

        If the container's resist properties have a strength less than
        'medium', the returned size will be zero. If the container does
        not have a solver, the returned size will be invalid.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the minimum size
            required to satisfy all constraints.

        """
        solver = self._solver
        if solver is None:
            return QSize()
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
        """ Calculates the maximum constraint size of the container.

        If the container's hug properties have a strength less than
        'medium', or if the container does not own its layout, the
        returned size will be the Qt maximum.

        Returns
        -------
        result : QSize
            A QSize which is the maximum size allowable while still
            satisfying all constraints.

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

    def _build_layout_items(self):
        """ Build the layout items for this container.

        """
        layout_items = []
        offset = LayoutPoint()
        queue = deque((offset, child) for child in self.children())
        while queue:
            offset, item = queue.popleft()
            if isinstance(item, QtConstraintsWidget):
                layout_item = LayoutItem()
                layout_item.item = item
                layout_item.offset = offset
                layout_item.origin = LayoutPoint()
                layout_items.append(layout_item)
                if isinstance(item, QtContainer):
                    if item.declaration.share_layout:
                        item.release_layout()
                        item.layout_container = self
                        child_offset = layout_item.origin
                        for child in item.children():
                            queue.append((child_offset, child))
                    else:
                        item.layout_container = None
                else:
                    item.layout_container = self
        self._layout_items = layout_items

    def _create_constraints(self):
        """ Creates the list of Constraint objects for container items.

        This method walks over the items in the layout table and creates
        a single list of Constraint objects for the solver

        Returns
        -------
        result : list
            The list of Constraints instances to add to the solver.

        """
        d = self.declaration
        cns = hard_constraints(self)
        cns.extend(contents_margins_constraints(self))
        cns.extend(expand_constraints(d, d.layout_constraints()))
        for layout_item in self._layout_items:
            item = layout_item.item
            d = item.declaration
            cns.extend(hard_constraints(item))
            if isinstance(item, QtContainer):
                if d.share_layout:
                    cns.extend(contents_margins_constraints(item))
                    cns.extend(expand_constraints(d, d.layout_constraints()))
                else:
                    cns.extend(size_hint_constraints(item))
            else:
                cns.extend(size_hint_constraints(item))
                cns.extend(expand_constraints(d, d.layout_constraints()))
        return cns
