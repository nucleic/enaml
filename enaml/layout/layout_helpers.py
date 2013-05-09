#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from uuid import uuid4

from atom.api import Atom, Range, Coerced
from casuarius import ConstraintVariable, LinearSymbolic, STRENGTH_MAP

from .ab_constrainable import ABConstrainable
from .box_model import BoxModel
from .geometry import Box


#------------------------------------------------------------------------------
# Default Spacing
#------------------------------------------------------------------------------
class DefaultSpacing(Atom):
    """ A class which encapsulates the default spacing parameters for
    the various layout helper objects.

    """
    #: The space between abutted components
    ABUTMENT = Range(low=0, value=10)

    #: The space between aligned anchors
    ALIGNMENT = Range(low=0, value=0)

    #: The margins for box helpers
    BOX_MARGINS = Coerced(Box, factory=lambda: Box(0, 0, 0, 0))


# We only require a singleton of DefaultSpacing
DefaultSpacing = DefaultSpacing()


#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------
def expand_constraints(component, constraints):
    """ A function which expands any DeferredConstraints in the provided
    list. This is a generator function which yields the flattened stream
    of constraints.

    Paramters
    ---------
    component : Constrainable
        The constrainable component with which the constraints are
        associated. This will be passed to the .get_constraints()
        method of any DeferredConstraint instance.

    constraints : list
        The list of constraints.

    Yields
    ------
    constraints
        The stream of expanded constraints.

    """
    for cn in constraints:
        if isinstance(cn, DeferredConstraints):
            for item in cn.get_constraints(component):
                if item is not None:
                    yield item
        else:
            if cn is not None:
                yield cn


def is_spacer(item):
    """ Returns True if the given item can be considered a spacer, False
    other otherwise.

    """
    return isinstance(item, (Spacer, int))


#------------------------------------------------------------------------------
# Deferred Constraints
#------------------------------------------------------------------------------
class DeferredConstraints(object):
    """ Abstract base class for objects that will yield lists of
    constraints upon request.

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """ Initialize a DeferredConstraints instance.

        """
        # __or__() will set these default strength and weight. If
        # provided, they will be combined with the constraints created
        # by this instance.
        self.default_strength = None
        self.default_weight = None

    def __or__(self, other):
        """ Set the strength of all of the constraints to a common
        strength.

        """
        if isinstance(other, (float, int, long)):
            self.default_weight = float(other)
        elif isinstance(other, basestring):
            if other not in STRENGTH_MAP:
                raise ValueError('Invalid strength %r' % other)
            self.default_strength = other
        else:
            msg = 'Strength must be a string. Got %s instead.'
            raise TypeError(msg % type(other))
        return self

    def when(self, switch):
        """ A simple method that can be used to switch off the generated
        constraints depending on a boolean value.

        """
        if switch:
            return self

    def get_constraints(self, component):
        """ Returns a list of weighted LinearConstraints.

        Parameters
        ----------
        component : Component or None
            The component that owns this DeferredConstraints. It can
            be None for contexts in which there is not a containing
            component, such as in certain nested DeferredConstraints.

        Returns
        -------
        result : list of LinearConstraints
            The list of LinearConstraint objects which have been
            weighted by any provided strengths and weights.

        """
        cn_list = self._get_constraints(component)
        strength = self.default_strength
        if strength is not None:
            cn_list = [cn | strength for cn in cn_list]
        weight = self.default_weight
        if weight is not None:
            cn_list = [cn | weight for cn in cn_list]
        return cn_list

    @abstractmethod
    def _get_constraints(self, component):
        """ Returns a list of LinearConstraint objects.

        Subclasses must implement this method to actually yield their
        constraints. Users of instances should instead call the
        `get_constraints()` method which will combine these
        constraints with the `default_strength` and/or the
        `default_weight` if one or both are provided.

        Parameters
        ----------
        component : Component or None
            The component that owns this DeferredConstraints. It can
            be None for contexts in which there is not a containing
            component, such as in certain nested DeferredConstraints.

        Returns
        -------
        result : list of LinearConstraints
            The list of LinearConstraint objects for this deferred
            instance.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Deferred Constraints Implementations
#------------------------------------------------------------------------------
class DeferredConstraintsFunction(DeferredConstraints):
    """ A concrete implementation of DeferredConstraints which will
    call a function to get the constraint list upon request.

    """
    def __init__(self, func, *args, **kwds):
        """ Initialize a DeferredConstraintsFunction.

        Parameters
        ----------
        func : callable
            A callable object which will return the list of constraints.

        *args
            The arguments to pass to 'func'.

        **kwds
            The keyword arguments to pass to 'func'.

        """
        super(DeferredConstraintsFunction, self).__init__()
        self.func = func
        self.args = args
        self.kwds = kwds

    def _get_constraints(self, component):
        """ Abstract method implementation which calls the underlying
        function to generate the list of constraints.

        """
        return self.func(*self.args, **self.kwds)


class AbutmentHelper(DeferredConstraints):
    """ A concrete implementation of DeferredConstraints which will
    lay out its components by abutting them in a given orientation.

    """
    def __init__(self, orientation, *items, **config):
        """ Initialize an AbutmentHelper.

        Parameters
        ----------
        orientation
            A string which is either 'horizontal' or 'vertical' which
            indicates the abutment orientation.

        *items
            The components to abut in the given orientation.

        **config
            Configuration options for how this helper should behave.
            The following options are currently supported:

            spacing
                An integer >= 0 which indicates how many pixels of
                inter-element spacing to use during abutment. The
                default is the value of DefaultSpacing.ABUTMENT.

        """
        super(AbutmentHelper, self).__init__()
        self.orientation = orientation
        self.items = items
        self.spacing = config.get('spacing', DefaultSpacing.ABUTMENT)

    def __repr__(self):
        """ A pretty string representation of the helper.

        """
        items = ', '.join(map(repr, self.items))
        return '{0}({1})'.format(self.orientation, items)

    def _get_constraints(self, component):
        """ Abstract method implementation which applies the constraints
        to the given items, after filtering them for None values.

        """
        items = [item for item in self.items if item is not None]
        factories = AbutmentConstraintFactory.from_items(
            items, self.orientation, self.spacing,
        )
        cn_lists = (f.constraints() for f in factories)
        return list(cn for cns in cn_lists for cn in cns)


class AlignmentHelper(DeferredConstraints):
    """ A deferred constraints helper class that lays out with a given
    anchor to align.

    """
    def __init__(self, anchor, *items, **config):
        """ Initialize an AlignmentHelper.

        Parameters
        ----------
        anchor
            A string which is either 'left', 'right', 'top', 'bottom',
            'v_center', or 'h_center'.

        *items
            The components to align on the given anchor.

        **config
            Configuration options for how this helper should behave.
            The following options are currently supported:

            spacing
                An integer >= 0 which indicates how many pixels of
                inter-element spacing to use during alignement. The
                default is the value of DefaultSpacing.ALIGNMENT.

        """
        super(AlignmentHelper, self).__init__()
        self.anchor = anchor
        self.items = items
        self.spacing = config.get('spacing', DefaultSpacing.ALIGNMENT)

    def __repr__(self):
        """ A pretty string representation of the layout helper.

        """
        items = ', '.join(map(repr, self.items))
        return 'align({0!r}, {1})'.format(self.anchor, items)

    def _get_constraints(self, component):
        """ Abstract method implementation which applies the constraints
        to the given items, after filtering them for None values.

        """
        items = [item for item in self.items if item is not None]
        # If there are less than two items, no alignment needs to
        # happen, so return no constraints.
        if len(items) < 2:
            return []
        factories = AlignmentConstraintFactory.from_items(
            items, self.anchor, self.spacing,
        )
        cn_lists = (f.constraints() for f in factories)
        return list(cn for cns in cn_lists for cn in cns)


class BoxHelper(DeferredConstraints):
    """ A DeferredConstraints helper class which adds a box model to
    the helper.

    The addition of the box model allows the helper to be registered
    as ABConstrainable which has the effect of allowing box helper
    instances to be nested.

    """
    def __init__(self, name):
        """ Initialize a BoxHelper.

        Parameters
        ----------
        name : string
            A string name to prepend to a unique owner id generated
            for this box helper, to aid in debugging.

        """
        super(BoxHelper, self).__init__()
        self.constraints_id = name + '|' + uuid4().hex
        self._box_model = BoxModel(self.constraints_id)

    left = property(lambda self: self._box_model.left)
    top = property(lambda self: self._box_model.top)
    right = property(lambda self: self._box_model.right)
    bottom = property(lambda self: self._box_model.bottom)
    width = property(lambda self: self._box_model.width)
    height = property(lambda self: self._box_model.height)
    v_center = property(lambda self: self._box_model.v_center)
    h_center = property(lambda self: self._box_model.h_center)


ABConstrainable.register(BoxHelper)


class LinearBoxHelper(BoxHelper):
    """ A layout helper which arranges items in a linear box.

    """
    #: A mapping orientation to the anchor names needed to make the
    #: constraints on the containing component.
    orientation_map = {
        'horizontal': ('left', 'right'),
        'vertical': ('top', 'bottom'),
    }

    #: A mapping of ortho orientations
    ortho_map = {
        'horizontal': 'vertical',
        'vertical': 'horizontal',
    }

    def __init__(self, orientation, *items, **config):
        """ Initialize a LinearBoxHelper.

        Parameters
        ----------
        orientation : string
            The layout orientation of the box. This must be either
            'horizontal' or 'vertical'.

        *items
            The components to align on the given anchor.

        **config
            Configuration options for how this helper should behave.
            The following options are currently supported:

            spacing
                An integer >= 0 which indicates how many pixels of
                inter-element spacing to use during abutment. The
                default is the value of DefaultSpacing.ABUTMENT.

            margins
                A int, tuple of ints, or Box of ints >= 0 which
                indicate how many pixels of margin to add around
                the bounds of the box. The default is the value of
                DefaultSpacing.BOX_MARGIN.

        """
        super(LinearBoxHelper, self).__init__(orientation[0] + 'box')
        self.items = items
        self.orientation = orientation
        self.ortho_orientation = self.ortho_map[orientation]
        self.spacing = config.get('spacing', DefaultSpacing.ABUTMENT)
        self.margins = Box(config.get('margins', DefaultSpacing.BOX_MARGINS))

    def __repr__(self):
        """ A pretty string representation of the layout helper.

        """
        items = ', '.join(map(repr, self.items))
        return '{0}box({1})'.format(self.orientation[0], items)

    def _get_constraints(self, component):
        """ Generate the linear box constraints.

        This is an abstractmethod implementation which will use the
        space available on the provided component to layout the items.

        """
        items = [item for item in self.items if item is not None]
        if len(items) == 0:
            return items

        first, last = self.orientation_map[self.orientation]
        first_boundary = getattr(self, first)
        last_boundary = getattr(self, last)
        first_ortho, last_ortho = self.orientation_map[self.ortho_orientation]
        first_ortho_boundary = getattr(self, first_ortho)
        last_ortho_boundary = getattr(self, last_ortho)

        # Setup the initial outer constraints of the box
        if component is not None:
            # This box helper is inside a real component, not just nested
            # inside of another box helper. Check if the component is a
            # PaddingConstraints object and use it's contents anchors.
            attrs = ['top', 'bottom', 'left', 'right']
            # XXX hack!
            if hasattr(component, 'contents_top'):
                other_attrs = ['contents_' + attr for attr in attrs]
            else:
                other_attrs = attrs[:]
            constraints = [
                getattr(self, attr) == getattr(component, other)
                for (attr, other) in zip(attrs, other_attrs)
            ]
        else:
            constraints = []

        # Create the margin spacers that will be used.
        margins = self.margins
        if self.orientation == 'vertical':
            first_spacer = EqSpacer(margins.top)
            last_spacer = EqSpacer(margins.bottom)
            first_ortho_spacer = FlexSpacer(margins.left)
            last_ortho_spacer = FlexSpacer(margins.right)
        else:
            first_spacer = EqSpacer(margins.left)
            last_spacer = EqSpacer(margins.right)
            first_ortho_spacer = FlexSpacer(margins.top)
            last_ortho_spacer = FlexSpacer(margins.bottom)

        # Add a pre and post padding spacer if the user hasn't specified
        # their own spacer as the first/last element of the box items.
        if not is_spacer(items[0]):
            pre_along_args = [first_boundary, first_spacer]
        else:
            pre_along_args = [first_boundary]
        if not is_spacer(items[-1]):
            post_along_args = [last_spacer, last_boundary]
        else:
            post_along_args = [last_boundary]

        # Accummulate the constraints in the direction of the layout
        along_args = pre_along_args + items + post_along_args
        kwds = dict(spacing=self.spacing)
        helpers = [AbutmentHelper(self.orientation, *along_args, **kwds)]
        ortho = self.ortho_orientation
        for item in items:
            # Add the helpers for the ortho constraints
            if isinstance(item, ABConstrainable):
                abutment_items = (
                    first_ortho_boundary, first_ortho_spacer,
                    item, last_ortho_spacer, last_ortho_boundary,
                )
                helpers.append(AbutmentHelper(ortho, *abutment_items, **kwds))
            # Pull out nested helpers so that their constraints get
            # generated during the pass over the helpers list.
            if isinstance(item, DeferredConstraints):
                helpers.append(item)

        # Pass over the list of child helpers and generate the
        # flattened list of constraints.
        for helper in helpers:
            constraints.extend(helper.get_constraints(None))

        return constraints


class _GridCell(object):
    """ A private class used by a GridHelper to track item cells.

    """
    def __init__(self, item, row, col):
        """ Initialize a _GridCell.

        Parameters
        ----------
        item : object
            The item contained in the cell.

        row : int
            The row index of the cell.

        col : int
            The column index of the cell.

        """
        self.item = item
        self.start_row = row
        self.start_col = col
        self.end_row = row
        self.end_col = col

    def expand_to(self, row, col):
        """ Expand the cell to enclose the given row and column.

        """
        self.start_row = min(row, self.start_row)
        self.end_row = max(row, self.end_row)
        self.start_col = min(col, self.start_col)
        self.end_col = max(col, self.end_col)


class GridHelper(BoxHelper):
    """ A layout helper which arranges items in a grid.

    """
    def __init__(self, *rows, **config):
        """ Initialize a GridHelper.

        Parameters
        ----------
        *rows: iterable of lists
            The rows to layout in the grid. A row must be composed of
            constrainable objects and None. An item will be expanded
            to span all of the cells in which it appears.

        **config
            Configuration options for how this helper should behave.
            The following options are currently supported:

            row_align
                A string which is the name of a constraint variable on
                a item. If given, it is used to add constraints on the
                alignment of items in a row. The constraints will only
                be applied to items that do not span rows.

            row_spacing
                An integer >= 0 which indicates how many pixels of
                space should be placed between rows in the grid. The
                default is the value of DefaultSpacing.ABUTMENT.

            column_align
                A string which is the name of a constraint variable on
                a item. If given, it is used to add constraints on the
                alignment of items in a column. The constraints will
                only be applied to items that do not span columns.

            column_spacing
                An integer >= 0 which indicates how many pixels of
                space should be placed between columns in the grid.
                The default is the value of DefaultSpacing.ABUTMENT.

            margins
                A int, tuple of ints, or Box of ints >= 0 which
                indicate how many pixels of margin to add around
                the bounds of the grid. The default is the value of
                DefaultSpacing.BOX_MARGIN.

        """
        super(GridHelper, self).__init__('grid')
        self.grid_rows = rows
        self.row_align = config.get('row_align', '')
        self.col_align = config.get('col_align', '')
        self.row_spacing = config.get('row_spacing', DefaultSpacing.ABUTMENT)
        self.col_spacing = config.get('column_spacing', DefaultSpacing.ABUTMENT)
        self.margins = Box(config.get('margins', DefaultSpacing.BOX_MARGINS))

    def __repr__(self):
        """ A pretty string representation of the layout helper.

        """
        items = ', '.join(map(repr, self.grid_rows))
        return 'grid({0})'.format(items)

    def _get_constraints(self, component):
        """ Generate the grid constraints.

        This is an abstractmethod implementation which will use the
        space available on the provided component to layout the items.

        """
        grid_rows = self.grid_rows
        if not grid_rows:
            return []

        # Validate and compute the cell span for the items in the grid.
        cells = []
        cell_map = {}
        num_cols = 0
        num_rows = len(grid_rows)
        for row_idx, row in enumerate(grid_rows):
            for col_idx, item in enumerate(row):
                if item is None:
                    continue
                elif isinstance(item, ABConstrainable):
                    if item in cell_map:
                        cell_map[item].expand_to(row_idx, col_idx)
                    else:
                        cell = _GridCell(item, row_idx, col_idx)
                        cell_map[item] = cell
                        cells.append(cell)
                else:
                    m = ('Grid cells must be constrainable objects or None. '
                         'Got object of type `%s` instead.')
                    raise TypeError(m % type(item).__name__)
            num_cols = max(num_cols, col_idx + 1)

        # Setup the initial outer constraints of the grid
        if component is not None:
            # This box helper is inside a real component, not just nested
            # inside of another box helper. Check if the component is a
            # PaddingConstraints object and use it's contents anchors.
            attrs = ['top', 'bottom', 'left', 'right']
            # XXX hack!
            if hasattr(component, 'contents_top'):
                other_attrs = ['contents_' + attr for attr in attrs]
            else:
                other_attrs = attrs[:]
            constraints = [
                getattr(self, attr) == getattr(component, other)
                for (attr, other) in zip(attrs, other_attrs)
            ]
        else:
            constraints = []

        # Create the row and column constraint variables along with
        # some default limits
        row_vars = []
        col_vars = []
        for idx in xrange(num_rows + 1):
            name = 'row' + str(idx)
            var = ConstraintVariable(name)
            row_vars.append(var)
            constraints.append(var >= 0)
        for idx in xrange(num_cols + 1):
            name = 'col' + str(idx)
            var = ConstraintVariable(name)
            col_vars.append(var)
            constraints.append(var >= 0)

        # Add some neighbor relations to the row and column vars.
        for r1, r2 in zip(row_vars[:-1], row_vars[1:]):
            constraints.append(r1 <= r2)
        for c1, c2 in zip(col_vars[:-1], col_vars[1:]):
            constraints.append(c1 <= c2)

        # Setup the initial interior bounding box for the grid.
        margins = self.margins
        top_items = (self.top, EqSpacer(margins.top), row_vars[0])
        bottom_items = (row_vars[-1], EqSpacer(margins.bottom), self.bottom)
        left_items = (self.left, EqSpacer(margins.left), col_vars[0])
        right_items = (col_vars[-1], EqSpacer(margins.right), self.right)
        helpers = [
            AbutmentHelper('vertical', *top_items),
            AbutmentHelper('vertical', *bottom_items),
            AbutmentHelper('horizontal', *left_items),
            AbutmentHelper('horizontal', *right_items),
        ]

        # Setup the spacer list for constraining the cell items
        row_spacer = FlexSpacer(self.row_spacing / 2.)
        col_spacer = FlexSpacer(self.col_spacing / 2.)
        rspace = [row_spacer] * len(row_vars)
        rspace[0] = 0
        rspace[-1] = 0
        cspace = [col_spacer] * len(col_vars)
        cspace[0] = 0
        cspace[-1] = 0

        # Setup the constraints for each constrainable grid cell.
        for cell in cells:
            sr = cell.start_row
            er = cell.end_row + 1
            sc = cell.start_col
            ec = cell.end_col + 1
            item = cell.item
            row_item = (
                row_vars[sr], rspace[sr], item, rspace[er], row_vars[er]
            )
            col_item = (
                col_vars[sc], cspace[sc], item, cspace[ec], col_vars[ec]
            )
            helpers.append(AbutmentHelper('vertical', *row_item))
            helpers.append(AbutmentHelper('horizontal', *col_item))
            if isinstance(item, DeferredConstraints):
                helpers.append(item)

        # Add the row alignment constraints if given. This will only
        # apply the alignment constraint to items which do not span
        # multiple rows.
        if self.row_align:
            row_map = defaultdict(list)
            for cell in cells:
                if cell.start_row == cell.end_row:
                    row_map[cell.start_row].append(cell.item)
            for items in row_map.itervalues():
                if len(items) > 1:
                    helpers.append(AlignmentHelper(self.row_align, *items))

        # Add the column alignment constraints if given. This will only
        # apply the alignment constraint to items which do not span
        # multiple columns.
        if self.col_align:
            col_map = defaultdict(list)
            for cell in cells:
                if cell.start_col == cell.end_col:
                    col_map[cell.start_col].append(cell.item)
            for items in col_map.itervalues():
                if len(items) > 1:
                    helpers.append(AlignmentHelper(self.col_align, *items))

        # Add the child helpers constraints to the constraints list.
        for helper in helpers:
            constraints.extend(helper.get_constraints(None))

        return constraints


#------------------------------------------------------------------------------
# Abstract Constraint Factory
#------------------------------------------------------------------------------
class AbstractConstraintFactory(object):
    """ An abstract constraint factory class. Subclasses must implement
    the 'constraints' method implement which returns a LinearConstraint
    instance.

    """
    __metaclass__ = ABCMeta

    @staticmethod
    def validate(items):
        """ A validator staticmethod that insures a sequence of items is
        appropriate for generating a sequence of linear constraints. The
        following conditions are verified of the sequence of given items:

            * The number of items in the sequence is 0 or >= 2.

            * The first and last items are instances of either
              LinearSymbolic or Constrainable.

            * All of the items in the sequence are instances of
              LinearSymbolic, Constrainable, Spacer, or int.

        If any of the above conditions do not hold, an exception is
        raised with a (hopefully) useful error message.

        """
        if len(items) == 0:
            return

        if len(items) < 2:
            msg = 'Two or more items required to setup abutment constraints.'
            raise ValueError(msg)

        extrema_types = (LinearSymbolic, ABConstrainable)
        def extrema_test(item):
            return isinstance(item, extrema_types)

        item_types = (LinearSymbolic, ABConstrainable, Spacer, int)
        def item_test(item):
            return isinstance(item, item_types)

        if not all(extrema_test(item) for item in (items[0], items[-1])):
            msg = ('The first and last items of a constraint sequence '
                   'must be anchors or Components. Got %s instead.')
            args = [type(items[0]), type(items[1])]
            raise TypeError(msg % args)

        if not all(map(item_test, items)):
            msg = ('The allowed items for a constraint sequence are'
                   'anchors, Components, Spacers, and ints. '
                   'Got %s instead.')
            args = [type(item) for item in items]
            raise TypeError(msg % args)

    @abstractmethod
    def constraints(self):
        """ An abstract method which must be implemented by subclasses.
        It should return a list of LinearConstraint instances.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Abstract Constraint Factory Implementations
#------------------------------------------------------------------------------
class BaseConstraintFactory(AbstractConstraintFactory):
    """ A base constraint factory class that implements basic common
    logic. It is not meant to be used directly but should rather be
    subclassed to be useful.

    """
    def __init__(self, first_anchor, spacer, second_anchor):
        """ Create an base constraint instance.

        Parameters
        ----------
        first_anchor : LinearSymbolic
            A symbolic object that can be used in a constraint expression.

        spacer : Spacer
            A spacer instance to put space between the items.

        second_anchor : LinearSymbolic
            The second anchor for the constraint expression.

        """
        self.first_anchor = first_anchor
        self.spacer = spacer
        self.second_anchor = second_anchor

    def constraints(self):
        """ Returns LinearConstraint instance which is formed through
        an appropriate linear expression for the given space between
        the anchors.

        """
        first = self.first_anchor
        second = self.second_anchor
        spacer = self.spacer
        return spacer.constrain(first, second)


class SequenceConstraintFactory(BaseConstraintFactory):
    """ A BaseConstraintFactory subclass that represents a constraint
    between two anchors of different components separated by some amount
    of space. It has a '_make_cns' classmethod which will create a list
    of constraint factory instances from a sequence of items, the two
    anchor names, and a default spacing.

    """
    @classmethod
    def _make_cns(cls, items, first_anchor_name, second_anchor_name, spacing):
        """ A classmethod that generates a list of constraints factories
        given a sequence of items, two anchor names, and default spacing.

        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.

        first_anchor_name : string
            The name of the anchor on the first item in a constraint
            pair.

        second_anchor_name : string
            The name of the anchor on the second item in a constraint
            pair.

        spacing : int
            The spacing to use between items if no spacing is explicitly
            provided by in the sequence of items.

        Returns
        -------
        result : list
            A list of constraint factory instance.

        """
        # Make sure the items we'll be dealing with are valid for the
        # algorithm. This is a basic validation. Further error handling
        # is performed as needed.
        cls.validate(items)

        # The list of constraints we'll be creating for the given
        # sequence of items.
        cns = []

        # The list of items is treated as a stack. So we want to first
        # reverse it so the first items are at the top of the stack.
        items = list(reversed(items))

        while items:

            # Grab the item that will provide the first anchor
            first_item = items.pop()

            # first_item will be a Constrainable or a LinearSymbolic.
            # For the first iteration, this is enforced by 'validate'.
            # For subsequent iterations, this condition is enforced by
            # the fact that this loop only pushes those types back onto
            # the stack.
            if isinstance(first_item, ABConstrainable):
                first_anchor = getattr(first_item, first_anchor_name)
            elif isinstance(first_item, LinearSymbolic):
                first_anchor = first_item
            else:
                raise TypeError('This should never happen')

            # Grab the next item off the stack. It will be an instance
            # of Constrainable, LinearSymbolic, Spacer, or int. If it
            # can't provide an anchor, we grab the item after it which
            # *should* be able to provide one. If no space is given, we
            # use the provided default space.
            next_item = items.pop()
            if isinstance(next_item, Spacer):
                spacer = next_item
                second_item = items.pop()
            elif isinstance(next_item, int):
                spacer = EqSpacer(next_item)
                second_item = items.pop()
            elif isinstance(next_item, (ABConstrainable, LinearSymbolic)):
                spacer = EqSpacer(spacing)
                second_item = next_item
            else:
                raise ValueError('This should never happen')

            # If the second_item can't provide an anchor, such as two
            # spacers next to each other, then this is an error and we
            # raise an appropriate exception.
            if isinstance(second_item, ABConstrainable):
                second_anchor = getattr(second_item, second_anchor_name)
            elif isinstance(second_item, LinearSymbolic):
                second_anchor = second_item
            else:
                msg = 'Expected anchor or Constrainable. Got %r instead.'
                raise TypeError(msg % second_item)

            # Create the class instance for this constraint
            factory = cls(first_anchor, spacer, second_anchor)

            # If there are still items on the stack, then the second_item
            # will be used as the first_item in the next iteration.
            # Otherwise, we have exhausted all constraints and can exit.
            if items:
                items.append(second_item)

            # Finally, store away the created factory for returning.
            cns.append(factory)

        return cns


class AbutmentConstraintFactory(SequenceConstraintFactory):
    """ A SequenceConstraintFactory subclass that represents an abutment
    constraint, which is a constraint between two anchors of different
    components separated by some amount of space. It has a 'from_items'
    classmethod which will create a sequence of abutment constraints
    from a sequence of items, a direction, and default spacing.

    """
    #: A mapping from orientation to the order of anchor names to
    #: lookup for a pair of items in order to make the constraint.
    orientation_map = {
        'horizontal': ('right', 'left'),
        'vertical': ('bottom', 'top'),
    }

    @classmethod
    def from_items(cls, items, orientation, spacing):
        """ A classmethod that generates a list of abutment constraints
        given a sequence of items, an orientation, and default spacing.

        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.

        orientation : string
            Either 'vertical' or 'horizontal', which represents the
            orientation in which to abut the items.

        spacing : int
            The spacing to use between items if no spacing is explicitly
            provided by in the sequence of items.

        Returns
        -------
        result : list
            A list of AbutmentConstraint instances.

        Notes
        ------
        The order of abutment is left-to-right for horizontal direction
        and top-to-bottom for vertical direction.

        """
        # Grab the tuple of anchor names to lookup for each pair of
        # items in order to make the connection.
        orient = cls.orientation_map.get(orientation)
        if orient is None:
            msg = ("Valid orientations for abutment are 'vertical' or "
                   "'horizontal'. Got %r instead.")
            raise ValueError(msg % orientation)
        first_name, second_name = orient
        return cls._make_cns(items, first_name, second_name, spacing)


class AlignmentConstraintFactory(SequenceConstraintFactory):
    """ A SequenceConstraintFactory subclass which represents an
    alignmnent constraint, which is a constraint between two anchors of
    different components which are aligned but may be separated by some
    amount of space. It provides a 'from_items' classmethod which will
    create a  list of alignment constraints from a sequence of items an
    anchor name, and a default spacing.

    """
    @classmethod
    def from_items(cls, items, anchor_name, spacing):
        """ A classmethod that will create a seqence of alignment
        constraints given a sequence of items, an anchor name, and
        a default spacing.

        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.

        anchor_name : string
            The name of the anchor on the components which should be
            aligned. Either 'left', 'right', 'top', 'bottom', 'v_center',
            or 'h_center'.

        spacing : int
            The spacing to use between items if no spacing is explicitly
            provided by in the sequence of items.

        Returns
        -------
        result : list
            A list of AbutmentConstraint instances.

        Notes
        -----
        For every item in the sequence, if the item is a component, then
        anchor for the given anchor_name on that component will be used.
        If a LinearSymbolic is given, then that symbolic will be used and
        the anchor_name will be ignored. Specifying space between items
        via integers or spacers is allowed.

        """
        return cls._make_cns(items, anchor_name, anchor_name, spacing)


#------------------------------------------------------------------------------
# Spacers
#------------------------------------------------------------------------------
class Spacer(object):
    """ An abstract base class for spacers. Subclasses must implement
    the 'constrain' method.

    """
    __metaclass__ = ABCMeta

    def __init__(self, amt, strength=None, weight=None):
        self.amt = max(0, amt)
        self.strength = strength
        self.weight = weight

    def when(self, switch):
        """ A simple method that can be used to switch off the generated
        space depending on a boolean value.

        """
        if switch:
            return self

    def constrain(self, first_anchor, second_anchor):
        """ Returns the list of generated constraints appropriately
        weighted by the default strength and weight, if provided.

        """
        constraints = self._constrain(first_anchor, second_anchor)
        strength = self.strength
        if strength is not None:
            constraints = [cn | strength for cn in constraints]
        weight = self.weight
        if weight is not None:
            constraints = [cn | weight for cn in constraints]
        return constraints

    @abstractmethod
    def _constrain(self, first_anchor, second_anchor):
        """ An abstract method. Subclasses should implement this method
        to return a list of LinearConstraint instances which separate
        the two anchors according to the amount of space represented
        by the spacer.

        """
        raise NotImplementedError


class EqSpacer(Spacer):
    """ A spacer which represents a fixed amount of space.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space == anchor_2)

        """
        return [(first_anchor + self.amt) == second_anchor]


class LeSpacer(Spacer):
    """ A spacer which represents a flexible space with a maximum value.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space >= anchor_2)
        That is, the visible space must be less than or equal to the
        given amount. An additional constraint is applied which
        constrains (anchor_1 <= anchor_2) to prevent negative space.

        """
        return [(first_anchor + self.amt) >= second_anchor,
                first_anchor <= second_anchor]


class GeSpacer(Spacer):
    """ A spacer which represents a flexible space with a minimum value.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space <= anchor_2)
        That is, the visible space must be greater than or equal to
        the given amount.

        """
        return [(first_anchor + self.amt) <= second_anchor]


class FlexSpacer(Spacer):
    """ A spacer which represents a space with a hard minimum, but also
    a weaker preference for being that minimum.

    """
    def __init__(self, amt, min_strength='required', min_weight=1.0, eq_strength='medium', eq_weight=1.25):
        self.amt = max(0, amt)
        self.min_strength = min_strength
        self.min_weight = min_weight
        self.eq_strength = eq_strength
        self.eq_weight = eq_weight

    def constrain(self, first_anchor, second_anchor):
        """ Return list of LinearConstraint objects that are appropriate to
        separate the two anchors according to the amount of space represented by
        the spacer.

        """
        return self._constrain(first_anchor, second_anchor)

    def _constrain(self, first_anchor, second_anchor):
        """ Constraints of the form (anchor_1 + space <= anchor_2) and
        (anchor_1 + space == anchor_2)

        """
        return [
            ((first_anchor + self.amt) <= second_anchor) | self.min_strength | self.min_weight,
            ((first_anchor + self.amt) == second_anchor) | self.eq_strength | self.eq_weight,
        ]


class LayoutSpacer(Spacer):
    """ A Spacer instance which supplies convenience symbolic and normal
    methods to facilitate specifying spacers in layouts.

    """
    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return EqSpacer(other, self.strength, self.weight)

    def __le__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return LeSpacer(other, self.strength, self.weight)

    def __ge__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return GeSpacer(other, self.strength, self.weight)

    def _constrain(self, first_anchor, second_anchor):
        """ Returns a greater than or equal to spacing constraint.

        """
        spacer = GeSpacer(self.amt, self.strength, self.weight)
        return spacer._constrain(first_anchor, second_anchor)

    def flex(self, **kwargs):
        """ Returns a flex spacer for the current amount.

        """
        return FlexSpacer(self.amt, **kwargs)


#------------------------------------------------------------------------------
# Layout Helper Functions and Objects
#------------------------------------------------------------------------------
def horizontal(*items, **config):
    """ Create a DeferredConstraints object composed of horizontal
    abutments for the given sequence of items.

    """
    return AbutmentHelper('horizontal', *items, **config)


def vertical(*items, **config):
    """ Create a DeferredConstraints object composed of vertical
    abutments for the given sequence of items.

    """
    return AbutmentHelper('vertical', *items, **config)


def hbox(*items, **config):
    """ Create a DeferredConstraints object composed of horizontal
    abutments for a given sequence of items.

    """
    return LinearBoxHelper('horizontal', *items, **config)


def vbox(*items, **config):
    """ Create a DeferredConstraints object composed of vertical abutments
    for a given sequence of items.

    """
    return LinearBoxHelper('vertical', *items, **config)


def align(anchor, *items, **config):
    """ Align the given anchors of the given components. Inter-component
    spacing is allowed.

    """
    return AlignmentHelper(anchor, *items, **config)


def grid(*rows, **config):
    """ Create a DeferredConstraints object which lays out items in a
    grid.

    """
    return GridHelper(*rows, **config)


spacer = LayoutSpacer(DefaultSpacing.ABUTMENT)

