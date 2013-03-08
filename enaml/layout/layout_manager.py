#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from casuarius import Solver, medium


class LayoutManager(object):
    """ A class which uses a casuarius solver to manage a system
    of constraints.

    """
    def __init__(self):
        self._solver = Solver(autosolve=False)
        self._initialized = False
        self._running = False

    def initialize(self, constraints):
        """ Initialize the solver with the given constraints.

        Parameters
        ----------
        constraints : Iterable
            An iterable that yields the constraints to add to the
            solvers.

        """
        if self._initialized:
            raise RuntimeError('Solver already initialized')
        solver = self._solver
        solver.autosolve = False
        for cn in constraints:
            solver.add_constraint(cn)
        solver.autosolve = True
        self._initialized = True

    def replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the solver.

        Parameters
        ----------
        old_cns : list
            The list of casuarius constraints to remove from the
            solver.

        new_cns : list
            The list of casuarius constraints to add to the solver.

        """
        if not self._initialized:
            raise RuntimeError('Solver not yet initialized')
        solver = self._solver
        solver.autosolve = False
        for cn in old_cns:
            solver.remove_constraint(cn)
        for cn in new_cns:
            solver.add_constraint(cn)
        solver.autosolve = True

    def layout(self, cb, width, height, size, strength=medium, weight=1.0):
        """ Perform an iteration of the solver for the new width and
        height constraint variables.

        Parameters
        ----------
        cb : callable
            A callback which will be called when new values from the
            solver are available. This will be called from within a
            solver context while the solved values are valid. Thus
            the new values should be consumed before the callback
            returns.

        width : Constraint Variable
            The constraint variable representing the width of the
            main layout container.

        height : Constraint Variable
            The constraint variable representing the height of the
            main layout container.

        size : (int, int)
            The (width, height) size tuple which is the current size
            of the main layout container.

        strength : casuarius strength, optional
            The strength with which to perform the layout using the
            current size of the container. i.e. the strength of the
            resize. The default is casuarius.medium.

        weight : float, optional
            The weight to apply to the strength. The default is 1.0

        """
        if not self._initialized:
            raise RuntimeError('Layout with uninitialized solver')
        if self._running:
            return
        try:
            self._running = True
            w, h = size
            values = [(width, w), (height, h)]
            with self._solver.suggest_values(values, strength, weight):
                cb()
        finally:
            self._running = False

    def get_min_size(self, width, height, strength=medium, weight=0.1):
        """ Run an iteration of the solver with the suggested size of the
        component set to (0, 0). This will cause the solver to effectively
        compute the minimum size that the window can be to solve the
        system.

        Parameters
        ----------
        width : Constraint Variable
            The constraint variable representing the width of the
            main layout container.

        height : Constraint Variable
            The constraint variable representing the height of the
            main layout container.

        strength : casuarius strength, optional
            The strength with which to perform the layout using the
            current size of the container. i.e. the strength of the
            resize. The default is casuarius.medium.

        weight : float, optional
            The weight to apply to the strength. The default is 0.1
            so that constraints of medium strength but default weight
            have a higher precedence than the minimum size.

        Returns
        -------
        result : (float, float)
            The floating point (min_width, min_height) size of the
            container which would best satisfy the set of constraints.

        """
        if not self._initialized:
            raise RuntimeError('Get min size on uninitialized solver')
        values = [(width, 0.0), (height, 0.0)]
        with self._solver.suggest_values(values, strength, weight):
            min_width = width.value
            min_height = height.value
        return (min_width, min_height)

    def get_max_size(self, width, height, strength=medium, weight=0.1):
        """ Run an iteration of the solver with the suggested size of
        the component set to a very large value. This will cause the
        solver to effectively compute the maximum size that the window
        can be to solve the system. The return value is a tuple numbers.
        If one of the numbers is -1, it indicates there is no maximum in
        that direction.

        Parameters
        ----------
        width : Constraint Variable
            The constraint variable representing the width of the
            main layout container.

        height : Constraint Variable
            The constraint variable representing the height of the
            main layout container.

        strength : casuarius strength, optional
            The strength with which to perform the layout using the
            current size of the container. i.e. the strength of the
            resize. The default is casuarius.medium.

        weight : float, optional
            The weight to apply to the strength. The default is 0.1
            so that constraints of medium strength but default weight
            have a higher precedence than the minimum size.

        Returns
        -------
        result : (float or -1, float or -1)
            The floating point (max_width, max_height) size of the
            container which would best satisfy the set of constraints.

        """
        if not self._initialized:
            raise RuntimeError('Get max size on uninitialized solver')
        max_val = 2**24 - 1 # Arbitrary, but the max allowed by Qt.
        values = [(width, max_val), (height, max_val)]
        with self._solver.suggest_values(values, strength, weight):
            max_width = width.value
            max_height = height.value
        width_diff = abs(max_val - int(round(max_width)))
        height_diff = abs(max_val - int(round(max_height)))
        if width_diff <= 1:
            max_width = -1
        if height_diff <= 1:
            max_height = -1
        return (max_width, max_height)

