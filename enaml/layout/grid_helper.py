#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import Atom, Coerced, Int, Range, Str, Tuple, Value

import kiwisolver as kiwi

from .box_helper import BoxHelper
from .constrainable import Constrainable
from .constraint_helper import ConstraintHelper
from .geometry import Box
from .spacers import EqSpacer, FlexSpacer
from .sequence_helper import SequenceHelper


class GridHelper(BoxHelper):
    """ A box helper for creating a traditional grid layout.

    A grid helper is constrainable and can be nested in other grid
    and box helpers to build up complex layouts.

    """
    #: The tuple of row items for the grid.
    rows = Tuple()

    #: The name of constraint variable to align items in a row.
    row_align = Str()

    #: The spacing between consecutive rows in the grid.
    row_spacing = Range(low=0)

    #: The name of constraint variable to align items in a column.
    column_align = Str()

    #: The spacing between consecutive columns in the grid.
    column_spacing = Range(low=0)

    #: The margins to add around boundary of the grid.
    margins = Coerced(Box)

    class _Cell(Atom):
        """ A private class used by a GridHelper to track item cells.

        """
        #: The item contained in the cell.
        item = Value()

        #: The starting row of the cell, inclusive.
        start_row = Int()

        #: The starting column of the cell, inclusive.
        start_column = Int()

        #: The ending row of the cell, inclusive.
        end_row = Int()

        #: The ending column of the cell, inclusive.
        end_column = Int()

        def __init__(self, item, row, column):
            """ Initialize a Cell.

            Parameters
            ----------
            item : object
                The item contained in the cell.

            row : int
                The row index of the cell.

            column : int
                The column index of the cell.

            """
            self.item = item
            self.start_row = row
            self.start_column = column
            self.end_row = row
            self.end_column = column

        def expand_to(self, row, column):
            """ Expand the cell to enclose the given row and column.

            """
            self.start_row = min(row, self.start_row)
            self.end_row = max(row, self.end_row)
            self.start_column = min(column, self.start_column)
            self.end_column = max(column, self.end_column)

    def __init__(self, rows, **config):
        """ Initialize a GridHelper.

        Parameters
        ----------
        rows: iterable of iterable
            The rows to layout in the grid. A row must be composed of
            constrainable objects and None. An item will be expanded
            to span all of the cells in which it appears.

        **config
            Configuration options for how this helper should behave.
            The following options are currently supported:

            row_align
                A string which is the name of a constraint variable on
                an item. If given, it is used to add constraints on the
                alignment of items in a row. The constraints will only
                be applied to items that do not span rows.

            row_spacing
                An integer >= 0 which indicates how many pixels of
                space should be placed between rows in the grid. The
                default value is 10 pixels.

            column_align
                A string which is the name of a constraint variable on
                a item. If given, it is used to add constraints on the
                alignment of items in a column. The constraints will
                only be applied to items that do not span columns.

            column_spacing
                An integer >= 0 which indicates how many pixels of
                space should be placed between columns in the grid.
                The default is the value is 10 pixels.

            margins
                A int, tuple of ints, or Box of ints >= 0 which
                indicate how many pixels of margin to add around
                the bounds of the grid. The default value is 0
                pixels on all sides.

        """
        self.rows = self.validate(rows)
        self.row_align = config.get('row_align', '')
        self.column_align = config.get('col_align', '')  # backwards compat
        self.column_align = config.get('column_align', '')
        self.row_spacing = config.get('row_spacing', 10)
        self.column_spacing = config.get('column_spacing', 10)
        self.margins = config.get('margins', 0)

    @staticmethod
    def validate(rows):
        """ Validate the rows for the grid helper.

        This method asserts that the rows are composed entirely of
        Constrainable objects and None.

        Parameters
        ----------
        rows : iterable of iterable
            The iterable of row items to validate.

        Returns
        -------
        result : tuple of tuple
            The tuple of validated rows.

        """
        valid_rows = []
        for row in rows:
            for item in row:
                if item is not None and not isinstance(item, Constrainable):
                    msg = 'Grid items must be Constrainable or None. '
                    msg += 'Got %r instead.'
                    raise TypeError(msg % item)
            valid_rows.append(tuple(row))
        return tuple(valid_rows)

    def constraints(self, component):
        """ Generate the grid constraints for the given component.

        Parameters
        ----------
        component : Constrainable or None
            The constrainable object which represents the conceptual
            owner of the generated constraints.

        Returns
        -------
        result : list
            The list of Constraint objects for the given component.

        """
        # Create the outer boundary box constraints.
        cns = self.box_constraints(component)

        # Compute the cell spans for the items in the grid.
        cells = []
        cell_map = {}
        num_cols = 0
        num_rows = len(self.rows)
        for row_idx, row in enumerate(self.rows):
            num_cols = max(num_cols, len(row))
            for col_idx, item in enumerate(row):
                if item is None:
                    continue
                elif item in cell_map:
                    cell_map[item].expand_to(row_idx, col_idx)
                else:
                    cell = self._Cell(item, row_idx, col_idx)
                    cell_map[item] = cell
                    cells.append(cell)

        # Create the row and column variables and their default limits.
        row_vars = []
        col_vars = []
        for idx in range(num_rows + 1):
            var = kiwi.Variable('row%d' % idx)
            row_vars.append(var)
            cns.append(var >= 0)
        for idx in range(num_cols + 1):
            var = kiwi.Variable('col%d' % idx)
            col_vars.append(var)
            cns.append(var >= 0)

        # Add the neighbor constraints for the row and column vars.
        for r1, r2 in zip(row_vars[:-1], row_vars[1:]):
            cns.append(r1 <= r2)
        for c1, c2 in zip(col_vars[:-1], col_vars[1:]):
            cns.append(c1 <= c2)

        # Setup the initial interior bounding box for the grid.
        firsts = (self.top, col_vars[-1], row_vars[-1], self.left)
        seconds = (row_vars[0], self.right, self.bottom, col_vars[0])
        for size, first, second in zip(self.margins, firsts, seconds):
            cns.extend(EqSpacer(size).create_constraints(first, second))

        # Setup the spacer lists for constraining the cell items
        row_spacer = FlexSpacer(self.row_spacing // 2)  # floor division
        col_spacer = FlexSpacer(self.column_spacing // 2)
        rspace = [row_spacer] * len(row_vars)
        cspace = [col_spacer] * len(col_vars)
        rspace[0] = rspace[-1] = cspace[0] = cspace[-1] = 0

        # Create the helpers for each constrainable grid cell item. The
        # helper validation is bypassed since the items are known-valid.
        helpers = []
        for cell in cells:
            sr = cell.start_row
            er = cell.end_row + 1
            sc = cell.start_column
            ec = cell.end_column + 1
            item = cell.item
            ritems = (row_vars[sr], rspace[sr], item, rspace[er], row_vars[er])
            citems = (col_vars[sc], cspace[sc], item, cspace[ec], col_vars[ec])
            rhelper = SequenceHelper('bottom', 'top', ())
            chelper = SequenceHelper('right', 'left', ())
            rhelper.items = ritems
            chelper.items = citems
            helpers.extend((rhelper, chelper))
            if isinstance(item, ConstraintHelper):
                helpers.append(item)

        # Add the row alignment helpers if needed. This will only create
        # the helpers for items which do not span multiple rows.
        anchor = self.row_align
        if anchor:
            row_map = defaultdict(list)
            for cell in cells:
                if cell.start_row == cell.end_row:
                    row_map[cell.start_row].append(cell.item)
            for items in row_map.values():
                if len(items) > 1:
                    helper = SequenceHelper(anchor, anchor, (), 0)
                    helper.items = tuple(items)
                    helpers.append(helper)

        # Add the column alignment helpers if needed. This will only
        # create the helpers for items which do not span multiple rows.
        anchor = self.column_align
        if anchor:
            col_map = defaultdict(list)
            for cell in cells:
                if cell.start_column == cell.end_column:
                    col_map[cell.start_column].append(cell.item)
            for items in col_map.values():
                if len(items) > 1:
                    helper = SequenceHelper(anchor, anchor, (), 0)
                    helper.items = tuple(items)
                    helpers.append(helper)

        # Generate the constraints from the helpers.
        for helper in helpers:
            cns.extend(helper.create_constraints(None))

        return cns
