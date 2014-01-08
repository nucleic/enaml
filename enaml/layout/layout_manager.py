#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, Float, List, Typed

import kiwisolver as kiwi


class LayoutPoint(Atom):
    """ A class which represents a point in the layout space.

    """
    #: The x-coordinate of the point.
    x = Float(0.0)

    #: The y-coordinate of the point.
    y = Float(0.0)


class LayoutItem(Atom):
    """ A base class used for generating layout items.

    This class is intended to be subclassed by a toolkit backend to
    implement the necessary toolkit-specific widget functionality.

    """
    #: The layout point which represents the offset of the parent item
    #: from the origin of the root item.
    offset = Typed(LayoutPoint)

    #: The layout point which represents the offset of this item from
    #: the offset of the root item.
    origin = Typed(LayoutPoint)

    #: The list of cached size hint constraints. This is a framework
    #: value used for storage by the layout manager.
    _size_hint_cache = List()

    #: The list of cached margin constraints. This is a framework
    #: value used for storage by the layout manager.
    _margin_cache = List()

    def __call__(self):
        """ Update the geometry of the underlying toolkit widget.

        This is a framework method and should not be called directly
        by user code.

        """
        origin = self.origin
        d = self.constrainable()
        x = origin.x = d.left.value()
        y = origin.y = d.top.value()
        w = d.width.value()
        h = d.height.value()
        offset = self.offset
        self.set_geometry(x - offset.x, y - offset.y, w, h)

    def hard_constraints(self):
        """ Generate a list of hard constraints for the item.

        Returns
        -------
        result : list
            A list of hard constraints for the item.

        """
        d = self.constrainable()
        return [d.left >= 0, d.top >= 0, d.width >= 0, d.height >= 0]

    def margin_constraints(self):
        """ Generate a list of margin constraints for the item.

        Returns
        -------
        result : list
            A list of margin constraints for the item. The list will
            be empty if the item does not support margins.

        """
        margins = self.margins()
        if len(margins) == 0:
            return []
        top, right, bottom, left = margins
        d = self.contents_constrainable()
        c_t = d.contents_top == (d.top + top)
        c_r = d.contents_right == (d.right - right)
        c_b = d.contents_bottom == (d.bottom - bottom)
        c_l = d.contents_left == (d.left + left)
        return [c_t, c_r, c_b, c_l]

    def size_hint_constraints(self):
        """ Generate a list of size hint constraints for the item.

        Returns
        -------
        result : list
            A list of size hint constraints for the item.

        """
        cns = []
        d = self.constrainable()
        s = self.strength_object()
        width, height = self.size_hint()
        if width >= 0:
            if s.hug_width != 'ignore':
                cns.append((d.width == width) | s.hug_width)
            if s.resist_width != 'ignore':
                cns.append((d.width >= width) | s.resist_width)
            if s.limit_width != 'ignore':
                cns.append((d.width <= width) | s.limit_width)
        if height >= 0:
            if s.hug_height != 'ignore':
                cns.append((d.height == height) | s.hug_height)
            if s.resist_height != 'ignore':
                cns.append((d.height >= height) | s.resist_height)
            if s.limit_height != 'ignore':
                cns.append((d.height <= height) | s.limit_height)
        return cns

    def constrainable(self):
        """ Get a reference to the underlying constrainable object.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : Contrainable
            An object which implements the Constrainable interface.

        """
        raise NotImplementedError

    def margins(self):
        """ Get the margins for the underlying widget.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : tuple
            A 4-tuple of numbers representing the margins of the widget
            in the order (top, right, bottom, left). If the widget does
            not support margins, an empty tuple should be returned. If
            valid margins are given, the 'contents_constrainable'
            method must be implemented.

        """
        raise NotImplementedError

    def contents_constrainable(self):
        """ Get a reference to the contents constrainable object.

        This abstract method must be implemented by subclasses if the
        'margins' method returns a non-empty tuple.

        Returns
        -------
        result : ContentsContrainable
            An object which implements the ContentsConstrainable
            interface.

        """
        raise NotImplementedError

    def size_hint(self):
        """ Get the size hint for the underlying widget.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            size hint of the widget.

        """
        raise NotImplementedError

    def strength_object(self):
        """ Get a reference to an object which holds strength strings.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : object
            An object with attributes which hold the strength strings
            for the widget size hint. It must have the attributes:

                resist_width
                resist_height
                hug_width
                hug_height
                limit_width
                limit_height

        """
        raise NotImplementedError

    def layout_constraints(self):
        """ Get the user-defined layout constraints for the item.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : list
            The list of user-defined layout constraints.

        """
        raise NotImplementedError

    def set_geometry(self, x, y, width, height):
        """ Set the geometry of the underlying widget.

        This abstract method must be implemented by subclasses.

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
        raise NotImplementedError


class LayoutManager(Atom):
    """ A class which manages the layout for a system of items.

    This class is used by the various in-process backends to simplify
    the task of implementing constraint layout management.

    """
    #: The primary layout item which owns the layout.
    _root_item = Typed(LayoutItem)

    #: The solver used by the layout manager.
    _solver = Typed(kiwi.Solver, ())

    #: The stack of edit variables added to the solver.
    _edit_stack = List()

    #: The list of layout items forming the layout table.
    _layout_table = List()

    def __init__(self, item):
        """ Initialize a LayoutManager.

        Parameters
        ----------
        item : LayoutItem
            The layout item which contains the widget which is the
            root of the layout system. This item is the conceptual
            owner of the system.

        """
        self._root_item = item
        self.set_table([])

    def set_table(self, table):
        """ Set the layout table for this layout manager.

        This method will reset the internal solver state and build a
        new system of constraints using the items in the new table.

        Parameters
        ----------
        table : list
            A list of LayoutItem instances comprising the layout table.

        """
        # Reset the state of the solver.
        del self._edit_stack
        del self._layout_table
        solver = self._solver
        solver.reset()

        # Setup the standard edit variables.
        root = self._root_item
        d = root.constrainable()
        strength = kiwi.strength.medium
        pairs = ((d.width, strength), (d.height, strength))
        self._push_edit_vars(pairs)

        # If there are not items in the table, bail early.
        if len(table) == 0:
            return

        # Generate the constraints for the layout system.
        cns = []

        # Start with the root item. The size hint is irrelevant since
        # the input to the solver is the suggested size of the root.
        hc = root.hard_constraints()
        mc = root.margin_constraints()
        lc = root.layout_constraints()
        root._margin_cache = mc
        cns.extend(hc)
        cns.extend(mc)
        cns.extend(lc)

        # Continue with each child item in the layout table. The size
        # hint of these items is taken into account. If the hint of an
        # item should be ignored, the item can return an empty list.
        for child in table:
            hc = child.hard_constraints()
            sc = child.size_hint_constraints()
            mc = child.margin_constraints()
            lc = child.layout_constraints()
            child._size_hint_cache = sc
            child._margin_cache = mc
            cns.extend(hc)
            cns.extend(sc)
            cns.extend(mc)
            cns.extend(lc)

        # Add the new constraints to the solver.
        for cn in cns:
            solver.addConstraint(cn)

        # Store the layout table for resize updates.
        self._layout_table = table

    def resize(self, width, height):
        """ Update the size of target size of the layout.

        This method will update the solver and make a pass over
        the layout table to update the item layout geometries.

        Parameters
        ----------
        width : number
            The desired width of the layout owner.

        height : number
            The desired height of the layout owner.

        """
        solver = self._solver
        d = self._root_item.constrainable()
        solver.suggestValue(d.width, width)
        solver.suggestValue(d.height, height)
        solver.updateVariables()
        for item in self._layout_table:
            item()

    def best_size(self):
        """ Get the best size for the layout owner.

        The best size is computed by invoking the solver with a zero
        size suggestion at a strength of 0.1 * weak. The resulting
        values for width and height are taken as the best size.

        Returns
        -------
        result : tuple
            The 2-tuple of (width, height) best size values.

        """
        d = self._root_item.constrainable()
        width = d.width
        height = d.height
        solver = self._solver
        strength = 0.1 * kiwi.strength.weak
        pairs = ((width, strength), (height, strength))
        with self._edit_context(pairs):
            solver.suggestValue(width, 0.0)
            solver.suggestValue(height, 0.0)
            solver.updateVariables()
            result = (width.value(), height.value())
        return result

    def min_size(self):
        """ Compute the minimum size for the layout owner.

        The minimum size is computed by invoking the solver with a
        zero size suggestion at a strength of medium. The resulting
        values for width and height are taken as the minimum size.

        Returns
        -------
        result : tuple
            The 2-tuple of (width, height) min size values.

        """
        d = self._root_item.constrainable()
        width = d.width
        height = d.height
        solver = self._solver
        solver.suggestValue(width, 0.0)
        solver.suggestValue(height, 0.0)
        solver.updateVariables()
        return (width.value(), height.value())

    def max_size(self):
        """ Compute the maximum size for the container.

        The maximum size is computed by invoking the solver with a
        max size suggestion at a strength of medium. The resulting
        values for width and height are taken as the maximum size.

        Returns
        -------
        result : tuple
            The 2-tuple of (width, height) max size values.

        """
        max_v = 16777215  # max allowed by Qt
        d = self._root_item.constrainable()
        width = d.width
        height = d.height
        solver = self._solver
        solver.suggestValue(width, max_v)
        solver.suggestValue(height, max_v)
        solver.updateVariables()
        return (width.value(), height.value())

    def size_hint_changed(self, item):
        """ Notify the layout that an item's size hint has changed.

        The solver will be updated to reflect the item's new size hint.
        This may change the computed min/max/best size of the system.

        Parameters
        ----------
        item : LayoutItem
            The layout item with the updated size hint.

        """
        old = item._size_hint_cache
        new = item.size_hint_constraints()
        item._size_hint_cache = new
        self._replace(old, new)

    def margins_changed(self, item):
        """ Notify the layout that an item's margins have changed.

        The solver will be updated to reflect the item's new margins.
        This may change the computed min/max/best size of the system.

        Parameters
        ----------
        item : LayoutItem
            The layout item with the updated marings.

        """
        old = item._margin_cache
        new = item.margin_constraints()
        item._margin_cache = new
        self._replace(old, new)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _replace(self, old, new):
        """ Replace constraints in the solver.

        Parameters
        ----------
        old : list
            The list of constraints to remove from the solver.

        new : list
            The list of constraints to add to the solver.

        """
        solver = self._solver
        for cn in old:
            solver.removeConstraint(old)
        for cn in new:
            solver.addConstraint(new)

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
