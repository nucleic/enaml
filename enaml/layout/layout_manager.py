#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, List, Typed

import kiwisolver as kiwi

from .layout_helpers import expand_constraints


class LayoutItem(Atom):
    """ A base class used for creating layout items.

    This class is intended to be subclassed by a toolkit backend to
    implement the necessary toolkit specific layout functionality.

    """
    #: The list of cached geometry constraints. This is used for storage
    #: by the layout manager.
    _geometry_cache = List()

    #: The list of cached margin constraints. This is used for storage
    #: by the layout manager.
    _margin_cache = List()

    def __call__(self):
        """ Update the geometry of the underlying toolkit widget.

        This should not be called directly by user code.

        """
        d = self.constrainable()
        x = d.left.value()
        y = d.top.value()
        w = d.width.value()
        h = d.height.value()
        self.set_geometry(x, y, w, h)

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
        if not margins:
            return []
        top, right, bottom, left = margins
        d = self.constrainable()
        c_t = d.contents_top == (d.top + top)
        c_r = d.contents_right == (d.right - right)
        c_b = d.contents_bottom == (d.bottom - bottom)
        c_l = d.contents_left == (d.left + left)
        return [c_t, c_r, c_b, c_l]

    def geometry_constraints(self):
        """ Generate a list of geometry constraints for the item.

        Returns
        -------
        result : list
            A list of geometry constraints for the item.

        """
        cns = []
        d = self.constrainable()

        width_hint, height_hint = self.size_hint()
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

        strength = 0.1 * kiwi.strength.strong

        min_width, min_height = self.min_size()
        if min_width >= 0:
            cns.append((d.width >= min_width) | strength)
        if min_height >= 0:
            cns.append((d.height >= min_height) | strength)

        max_width, max_height = self.max_size()
        if max_width >= 0:
            cns.append((d.width <= max_width) | strength)
        if max_height >= 0:
            cns.append((d.height <= max_height) | strength)

        return cns

    def layout_constraints(self):
        """ Get the list of layout constraints for the item.

        Returns
        -------
        result : list
            The list of layout constraints for the item.

        """
        return expand_constraints(self.constrainable(), self.constraints())

    def constrainable(self):
        """ Get a reference to the underlying constrainable object.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : Contrainable or ContentsContrainable
            An object which implements the Constrainable interface.
            If the 'margins' method returns a non-empty tuple, then
            the object must also implement the ContentsConstrainable
            interface.

        """
        raise NotImplementedError

    def constraints(self):
        """ Get the user-defined constraints for the item.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : list
            The list of user-defined constraints and constraint helpers.

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
            not support margins, an empty tuple should be returned.

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

    def min_size(self):
        """ Get the minimum size for the underlying widget.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            min size of the widget. If any value is less than zero,
            constraints will not be generated for that dimension.

        """
        raise NotImplementedError

    def max_size(self):
        """ Get the maximum size for the underlying widget.

        This abstract method must be implemented by subclasses.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            max size of the widget. If any value is less than zero,
            constraints will not be generated for that dimension.

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

    #: The list of layout items handled by the manager.
    _layout_items = List()

    def __init__(self, item):
        """ Initialize a LayoutManager.

        Parameters
        ----------
        item : LayoutItem
            The layout item which contains the widget which is the
            root of the layout system. This item is the conceptual
            owner of the system. It is not resized by the manager,
            rather the size of this item is used as input to the
            manager via the 'resize' method.

        """
        self._root_item = item

    def set_items(self, items):
        """ Set the layout items for this layout manager.

        This method will reset the internal solver state and build a
        new system of constraints using the new list of items.

        Parameters
        ----------
        items : list
            A list of LayoutItem instances for the system. The root
            item should *not* be included in this list.

        """
        # Reset the state of the solver.
        del self._edit_stack
        del self._layout_items
        solver = self._solver
        solver.reset()

        # Setup the standard edit variables.
        root = self._root_item
        d = root.constrainable()
        strength = kiwi.strength.medium
        pairs = ((d.width, strength), (d.height, strength))
        self._push_edit_vars(pairs)

        # Generate the constraints for the layout system. The size hint
        # and bounds of the root item are ignored since the input to the
        # solver is the suggested size of the root item and the output
        # of the solver is used to compute the bounds of the item.
        cns = []
        hc = root.hard_constraints()
        mc = root.margin_constraints()
        lc = root.layout_constraints()
        root._margin_cache = mc
        cns.extend(hc)
        cns.extend(mc)
        cns.extend(lc)
        for child in items:
            hc = child.hard_constraints()
            gc = child.geometry_constraints()
            mc = child.margin_constraints()
            lc = child.layout_constraints()
            child._geometry_cache = gc
            child._margin_cache = mc
            cns.extend(hc)
            cns.extend(gc)
            cns.extend(mc)
            cns.extend(lc)

        # Add the new constraints to the solver.
        for cn in cns:
            solver.addConstraint(cn)

        # Store the layout items for resize updates.
        self._layout_items = items

    def clear_items(self):
        """ Clear the child layout items in the layout.

        """
        del self._layout_items

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
        for item in self._layout_items:
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
        d = self._root_item.constrainable()
        width = d.width
        height = d.height
        solver = self._solver
        solver.suggestValue(width, 16777215.0)  # max allowed by Qt
        solver.suggestValue(height, 16777215.0)
        solver.updateVariables()
        return (width.value(), height.value())

    def update_geometry(self, index):
        """ Update the geometry for the given layout item.

        The solver will be updated to reflect the item's new geometry.
        This may change the computed min/max/best size of the system.

        Parameters
        ----------
        index : int
            The index of the item in the list of layout items which
            was provided in the call to 'set_items'.

        """
        item = self._layout_items[index]
        old = item._geometry_cache
        new = item.geometry_constraints()
        item._geometry_cache = new
        self._replace(old, new)

    def update_margins(self, index):
        """ Update the margins for the given layout item.

        The solver will be updated to reflect the item's new margins.
        This may change the computed min/max/best size of the system.

        Parameters
        ----------
        index : int
            The index of the item in the list of layout items which
            was provided in the call to 'set_items'. A value of -1
            can be given to indicate the root item.

        """
        item = self._root_item if index < 0 else self._layout_items[index]
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
            solver.removeConstraint(cn)
        for cn in new:
            solver.addConstraint(cn)

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
        if stack:
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
        if stack:
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
