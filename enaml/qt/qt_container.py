#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque

from casuarius import weak
from enaml.layout.layout_manager import LayoutManager

from .qt.QtCore import QSize, Signal
from .qt.QtGui import QFrame
from .qt_constraints_widget import (
    QtConstraintsWidget, LayoutBox, size_hint_guard,
)


def _convert_cn_info(info, owners):
    """ Converts the lhs or rhs of a linear constraint info dict into
    its corresponding casuarius object.

    """
    cn_type = info['type']
    if cn_type == 'linear_expression':
        const = info['constant']
        terms = info['terms']
        convert = _convert_cn_info
        res = sum(convert(t, owners) for t in terms) + const
    elif cn_type == 'term':
        coeff = info['coeff']
        var = info['var']
        res = coeff * _convert_cn_info(var, owners)
    elif cn_type == 'linear_symbolic':
        sym_name = info['name']
        owner_id = info['owner']
        owner = owners.get(owner_id, None)
        if owner is None:
            owner = owners[owner_id] = LayoutBox('_virtual', owner_id)
        res = owner.primitive(sym_name)
    else:
        msg = 'Unhandled constraint info type `%s`' % cn_type
        raise ValueError(msg)
    return res


def as_linear_constraint(info, owners):
    """ Converts a constraint info dict into a casuarius linear
    constraint.

    For constraints specified in the info dict which do not have a
    corresponding owner (e.g. those created by box helpers) a
    constraint variable will be synthesized.

    Parameters
    ----------
    info : dict
        A dictionary sent from an Enaml widget which specifies the
        information for a linear constraint.

    owners : dict
        A mapping from constraint id to an owner object which holds
        the actual casuarius constraint variables as attributes.

    Returns
    -------
    result : LinearConstraint
        A casuarius linear constraint for the given dict.

    """
    if info['type'] != 'linear_constraint':
        msg = 'The info dict does not specify a linear constraint.'
        raise ValueError(msg)
    convert = _convert_cn_info
    lhs = convert(info['lhs'], owners)
    rhs = convert(info['rhs'], owners)
    op = info['op']
    if op == '==':
        cn = lhs == rhs
    elif op == '<=':
        cn = lhs <= rhs
    elif op == '>=':
        cn = lhs >= rhs
    else:
        msg = 'Unhandled constraint operator `%s`' % op
        raise ValueError(msg)
    return cn | info['strength'] | info['weight']


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


class QtContainer(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Container.

    """
    #: Whether or not this container should share its layout with a
    #: parent container.
    _share_layout = False

    #: The padding to use when constraining the layout.
    _padding = (10, 10, 10, 10)

    #: Whether or not this container owns its layout. A container which
    #: does not own its layout is not responsible for laying out its
    #: children on a resize event, and will proxy the call to its owner.
    _owns_layout = True

    #: The object which has taken ownership of the layout for this
    #: container, if any.
    _layout_owner = None

    #: The LayoutManager instance to use for solving the layout system
    #: for this container.
    _layout_manager = None

    #: The function to use for refreshing the layout on a resize event.
    _refresh = lambda *args, **kwargs: None

    #: The table of offsets to use during a layout pass.
    _offset_table = []

    #: The table of (index, updater) pairs to use during a layout pass.
    _layout_table = []

    #: A dict mapping constraint owner id to associated LayoutBox
    _cn_owners = {}

    #: A list of the current contents constraints for the widget.
    _contents_cns = []

    #: A list of the current size hint constraints for the widget.
    _size_hint_cns = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QContainer widget.

        """
        return QContainer(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtContainer, self).create(tree)
        layout = tree['layout']
        self._share_layout = layout['share_layout']
        self._padding = layout['padding']
        # The resized signal is connected directly to the refresh
        # method to save the overhead of the extra function call.
        self.widget().resized.connect(self.refresh)

    def init_layout(self):
        """ Initializes the layout for the container.

        """
        super(QtContainer, self).init_layout()
        # Layout ownership can only be transferred *after* this init
        # layout method is called, since layout occurs bottom up. So,
        # we only initialize a layout manager if we are not going to
        # transfer ownership at some point.
        if not self.will_transfer():
            offset_table, layout_table = self._build_layout_table()
            cns = self._generate_constraints(layout_table)
            # Initializing the layout manager can fail if the objective
            # function is unbounded. We let that failure occur so it can
            # be logged. Nothing is stored until it succeeds.
            manager = LayoutManager()
            manager.initialize(cns)
            self._offset_table = offset_table
            self._layout_table = layout_table
            self._layout_manager = manager
            self._refresh = self._build_refresher(manager)
            self.refresh_sizes()

    #--------------------------------------------------------------------------
    # Public Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ Rebuilds the constraints layout for this widget if it owns
        the responsibility for laying out its descendents.

        """
        if self._owns_layout:
            item = self.widget_item()
            old_hint = item.sizeHint()
            self.init_layout()
            self.refresh()
            new_hint = item.sizeHint()
            # If the size hint constraints are empty, it indicates that
            # they were previously cleared. In this case, the layout
            # system must be notified to rebuild its constraints, even
            # if the numeric size hint hasn't changed.
            if old_hint != new_hint or not self._size_hint_cns:
                self.size_hint_updated()
        else:
            self._layout_owner.relayout()

    def refresh(self):
        """ Makes a layout pass over the descendents if this widget owns
        the responsibility for their layout.

        """
        # The _refresh function is generated on every relayout and has
        # already taken into account whether or not the container owns
        # the layout.
        self._refresh()

    def refresh_sizes(self):
        """ Refresh the min/max/best sizes for the underlying widget.

        This method is normally called automatically at the proper
        times. It should not normally need to be called by user code.

        """
        widget = self.widget()
        widget.setSizeHint(self.compute_best_size())
        widget.setMinimumSize(self.compute_min_size())
        widget.setMaximumSize(self.compute_max_size())

    def replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the given layout.

        This method can be used to selectively add/remove/replace
        constraints in the layout system, when it is more efficient
        than performing a full relayout.

        Parameters
        ----------
        old_cns : list
            The list of casuarius constraints to remove from the
            the current layout system.

        new_cns : list
            The list of casuarius constraints to add to the
            current layout system.

        """
        if self._owns_layout:
            manager = self._layout_manager
            if manager is not None:
                with size_hint_guard(self):
                    manager.replace_constraints(old_cns, new_cns)
                    self.refresh_sizes()
                    self.refresh()
        else:
            self._layout_owner.replace_constraints(old_cns, new_cns)

    def clear_constraints(self, cns):
        """ Clear the given constraints from the current layout.

        Parameters
        ----------
        cns : list
            The list of casuarius constraints to remove from the
            current layout system.

        """
        if self._owns_layout:
            manager = self._layout_manager
            if manager is not None:
                manager.replace_constraints(cns, [])
        else:
            self._layout_owner.clear_constraints(cns)

    def layout(self):
        """ The callback invoked by the layout manager when there are
        new layout values available.

        This iterates over the layout table and calls the geometry
        updater functions.

        """
        # We explicitly don't use enumerate() to generate the running
        # index because this method is on the code path of the resize
        # event and hence called *often*. The entire code path for a
        # resize event is micro optimized and justified with profiling.
        offset_table = self._offset_table
        layout_table = self._layout_table
        running_index = 1
        for offset_index, updater in layout_table:
            dx, dy = offset_table[offset_index]
            new_offset = updater(dx, dy)
            offset_table[running_index] = new_offset
            running_index += 1

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
        """ Notify the layout system that the contents margins of this
        widget have been updated.

        """
        old_cns = self._contents_cns
        self._contents_cns = []
        new_cns = self.contents_constraints()
        self.replace_constraints(old_cns, new_cns)

    def contents_constraints(self):
        """ Create the contents constraints for the container.

        The contents contraints are generated by combining the user
        padding with the margins returned by 'contents_margins' method.

        Returns
        -------
        result : list
            The list of casuarius constraints for the content.

        """
        cns = self._contents_cns
        if not cns:
            padding = self._padding
            margins = self.contents_margins()
            tval, rval, bval, lval = map(sum, zip(padding, margins))
            primitive = self.layout_box.primitive
            top = primitive('top')
            left = primitive('left')
            width = primitive('width')
            height = primitive('height')
            contents_top = primitive('contents_top')
            contents_left = primitive('contents_left')
            contents_right = primitive('contents_right')
            contents_bottom = primitive('contents_bottom')
            cns = [
                contents_top == (top + tval),
                contents_left == (left + lval),
                contents_right == (left + width - rval),
                contents_bottom == (top + height - bval),
            ]
            self._contents_cns = cns
        return cns

    #--------------------------------------------------------------------------
    # Private Layout Handling
    #--------------------------------------------------------------------------
    def _build_refresher(self, manager):
        """ A private method which will build a function which, when
        called, will refresh the layout for the container.

        Parameters
        ----------
        manager : LayoutManager
            The layout manager to use when refreshing the layout.

        """
        # The return function is a hyper optimized (for Python) closure
        # in order minimize the amount of work which is performed on the
        # code path of the resize event. This is explicitly not idiomatic
        # Python code. It exists purely for the sake of efficiency,
        # justified with profiling.
        mgr_layout = manager.layout
        layout = self.layout
        primitive = self.layout_box.primitive
        width_var = primitive('width')
        height_var = primitive('height')
        widget = self._widget
        width = widget.width
        height = widget.height
        def refresher():
            mgr_layout(layout, width_var, height_var, (width(), height()))
        return refresher

    def _build_layout_table(self):
        """ A private method which will build the layout table for
        this container.

        A layout table is a pair of flat lists which hold the required
        objects for laying out the child widgets of this container.
        The flat table is built in advance (and rebuilt if and when
        the tree structure changes) so that it's not necessary to
        perform an expensive tree traversal to layout the children
        on every resize event.

        Returns
        -------
        result : (list, list)
            The offset table and layout table to use during a resize
            event.

        """
        # The offset table is a list of (dx, dy) tuples which are the
        # x, y offsets of children expressed in the coordinates of the
        # layout owner container. This owner container may be different
        # from the parent of the widget, and so the delta offset must
        # be subtracted from the computed geometry values during layout.
        # The offset table is updated during a layout pass in breadth
        # first order.
        #
        # The layout table is a flat list of (idx, updater) tuples. The
        # idx is an index into the offset table where the given child
        # can find the offset to use for its layout. The updater is a
        # callable provided by the widget which accepts the dx, dy
        # offset and will update the layout geometry of the widget.
        zero_offset = (0, 0)
        offset_table = [zero_offset]
        layout_table = []
        queue = deque((0, child) for child in self.children())

        # Micro-optimization: pre-fetch bound methods and store globals
        # as locals. This method is not on the code path of a resize
        # event, but it is on the code path of a relayout. If there
        # are many children, the queue could potentially grow large.
        push_offset = offset_table.append
        push_item = layout_table.append
        push = queue.append
        pop = queue.popleft
        QtConstraintsWidget_ = QtConstraintsWidget
        QtContainer_ = QtContainer
        isinst = isinstance

        # The queue yields the items in the tree in breadth-first order
        # starting with the immediate children of this container. If a
        # given child is a container that will share its layout, then
        # the children of that container are added to the queue to be
        # added to the layout table.
        running_index = 0
        while queue:
            offset_index, item = pop()
            if isinst(item, QtConstraintsWidget_):
                push_item((offset_index, item.geometry_updater()))
                push_offset(zero_offset)
                running_index += 1
                if isinst(item, QtContainer_):
                    if item.transfer_layout_ownership(self):
                        for child in item.children():
                            push((running_index, child))

        return offset_table, layout_table

    def _generate_constraints(self, layout_table):
        """ Creates the list of casuarius LinearConstraint objects for
        the widgets for which this container owns the layout.

        This method walks over the items in the given layout table and
        aggregates their constraints into a single list of casuarius
        LinearConstraint objects which can be given to the layout
        manager.

        Parameters
        ----------
        layout_table : list
            The layout table created by a call to _build_layout_table.

        Returns
        -------
        result : list
            The list of casuarius LinearConstraints instances to pass to
            the layout manager.

        """
        # The mapping of constraint owners and the list of constraint
        # info dictionaries provided by the Enaml widgets.
        box = self.layout_box
        cn_owners = {self.object_id(): box}
        cn_dicts = list(self.user_constraints())
        cn_dicts_extend = cn_dicts.extend

        # The list of raw casuarius constraints which will be returned
        # from this method to be added to the casuarius solver.
        raw_cns = self.hard_constraints() + self.contents_constraints()
        raw_cns_extend = raw_cns.extend

        # The first element in a layout table item is its offset index
        # which is not relevant to constraints generation.
        isinst = isinstance
        QtContainer_ = QtContainer
        for _, updater in layout_table:
            child = updater.item
            cn_owners[child.object_id()] = child.layout_box
            raw_cns_extend(child.hard_constraints())
            if isinst(child, QtContainer_):
                if child.transfer_layout_ownership(self):
                    cn_dicts_extend(child.user_constraints())
                    raw_cns_extend(child.contents_constraints())
                else:
                    raw_cns_extend(child.size_hint_constraints())
            else:
                raw_cns_extend(child.size_hint_constraints())
                cn_dicts_extend(child.user_constraints())

        # Convert the list of Enaml constraints info dicts to actual
        # casuarius LinearConstraint objects for the solver.
        add_cn = raw_cns.append
        as_cn = as_linear_constraint
        for info in cn_dicts:
            add_cn(as_cn(info, cn_owners))

        # We keep a strong reference to the constraint owners dict,
        # since it may include instances of LayoutBox which were
        # created on-the-fly and hold constraint variables which
        # should not be deleted.
        self._cn_owners = cn_owners

        return raw_cns

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def transfer_layout_ownership(self, owner):
        """ A method which can be called by other components in the
        hierarchy to gain ownership responsibility for the layout
        of the children of this container. By default, the transfer
        is allowed and is the mechanism which allows constraints to
        cross widget boundaries. Subclasses should reimplement this
        method if different behavior is desired.

        Parameters
        ----------
        owner : Declarative
            The component which has taken ownership responsibility
            for laying out the children of this component. All
            relayout and refresh requests will be forwarded to this
            component.

        Returns
        -------
        results : bool
            True if the transfer was allowed, False otherwise.

        """
        if not self._share_layout:
            return False
        self._owns_layout = False
        self._layout_owner = owner
        self._layout_manager = None
        self._refresh = owner.refresh
        self._offset_table = []
        self._layout_table = []
        self._cn_owners = {}
        return True

    def will_transfer(self):
        """ Whether or not the container expects to transfer its layout
        ownership to its parent.

        This method is predictive in nature and exists so that layout
        managers are not senslessly created during the bottom-up layout
        initialization pass. It is declared public so that subclasses
        can override the behavior if necessary.

        """
        if self._share_layout:
            if isinstance(self.parent(), QtContainer):
                return True
        return False

    def compute_min_size(self):
        """ Calculates the minimum size of the container which would
        allow all constraints to be satisfied.

        If the container's resist properties have a strength less than
        'medium', the returned size will be zero. If the container does
        not own its layout, the returned size will be invalid.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the minimum size
            required to satisfy all constraints.

        """
        resist_width, resist_height = self._resist
        shrink = ('ignore', 'weak')
        if resist_width in shrink and resist_height in shrink:
            return QSize(0, 0)
        if self._owns_layout and self._layout_manager is not None:
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            w, h = self._layout_manager.get_min_size(width, height)
            if resist_width in shrink:
                w = 0
            if resist_height in shrink:
                h = 0
            return QSize(w, h)
        return QSize()

    def compute_best_size(self):
        """ Calculates the best size of the container.

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
        if self._owns_layout and self._layout_manager is not None:
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            w, h = self._layout_manager.get_min_size(width, height, weak)
            return QSize(w, h)
        return QSize()

    def compute_max_size(self):
        """ Calculates the maximum size of the container which would
        allow all constraints to be satisfied.

        If the container's hug properties have a strength less than
        'medium', or if the container does not own its layout, the
        returned size will be the Qt maximum.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the maximum size
            allowable while still satisfying all constraints.

        """
        hug_width, hug_height = self._hug
        expanding = ('ignore', 'weak')
        if hug_width in expanding and hug_height in expanding:
            return QSize(16777215, 16777215)
        if self._owns_layout and self._layout_manager is not None:
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            w, h = self._layout_manager.get_max_size(width, height)
            if w < 0 or hug_width in expanding:
                w = 16777215
            if h < 0 or hug_height in expanding:
                h = 16777215
            return QSize(w, h)
        return QSize(16777215, 16777215)

