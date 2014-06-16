#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Range, Str, Tuple

from .constrainable import Constrainable
from .constraint_helper import ConstraintHelper
from .linear_symbolic import LinearSymbolic
from .spacers import Spacer, EqSpacer


class SequenceHelper(ConstraintHelper):
    """ A constraint helper for constraining sequences of items.

    """
    #: The name of the anchor on the first item of a constraint pair.
    first_name = Str()

    #: The name of the anchor on the second item of a constraint pair.
    second_name = Str()

    #: The tuple of items which will be used to generate the constraints.
    items = Tuple()

    #: The spacing to use between items if not explicitly provided.
    spacing = Range(low=0)

    def __init__(self, first_name, second_name, items, spacing=10):
        """ Initialize a SequenceHelper.

        Parameters
        ----------
        first_name : str
            The name of the constraint anchor attribute of the first
            item of a constraint pair, if that item is Constrainable.

        second_name : str
            The name of the constraint anchor attribute of the second
            item of a constraint pair, if that item is Constrainable.

        items : iterable
            The iterable of items which should be constrained.

        spacing : int, optional
            The spacing to use between items if not specifically given
            in the sequence of items. The default value is 10 pixels.

        """
        self.first_name = first_name
        self.second_name = second_name
        self.items = self.validate(items)
        self.spacing = spacing

    @staticmethod
    def validate(items):
        """ Validate an iterable of constrainable items.

        This method asserts that a sequence of items is appropriate for
        generating a sequence of constraints. The following conditions
        are verified of the sequence of items after they are filtered
        for None:

        * The first and last items are instances of LinearSymbolic or
          Constrainable.

        * All of the items in the sequence are instances of Spacer, int,
          LinearSymbolic, Constrainable.

        * There are never two adjacent ints or spacers.

        Parameters
        ----------
        items : iterable
            The iterable of constrainable items to validate.

        Returns
        -------
        result : tuple
            A tuple of validated items, with any None values removed.

        """
        items = tuple(item for item in items if item is not None)
        if len(items) < 2:
            return items

        types = (LinearSymbolic, Constrainable)
        for item in (items[0], items[-1]):
            if not isinstance(item, types):
                msg = 'The first and last item of a constraint sequence must '
                msg += 'be LinearSymbolic or Constrainable. Got %s instead.'
                raise TypeError(msg % type(item).__name__)

        was_spacer = False
        spacers = (int, Spacer)
        types = (LinearSymbolic, Constrainable, Spacer, int)
        for item in items:
            if not isinstance(item, types):
                msg = 'The allowed item types for a constraint sequence are '
                msg += 'LinearSymbolic, Constrainable, Spacer, and int. '
                msg += 'Got %s instead.'
                raise TypeError(msg % type(item).__name__)
            is_spacer = isinstance(item, spacers)
            if is_spacer and was_spacer:
                msg = 'Expected LinearSymbolic or Constrainable after a '
                msg += 'spacer. Got %s instead.'
                raise TypeError(msg % type(item).__name__)
            was_spacer = is_spacer

        return items

    def constraints(self, component):
        """ Generate the constraints for the sequence.

        The component parameter is ignored for sequence constraints.

        Returns
        -------
        result : list
            The list of Constraint objects for the sequence.

        """
        cns = []

        # If there are less than 2 items in the sequence, it is not
        # possible to generate meaningful constraints. However, it
        # should not raise an error so that constructs such as
        # align('h_center', foo, bar.when(bar.visible)) will work.
        if len(self.items) < 2:
            return cns

        # The list of items is treated as a stack. So a reversed copy
        # is made before items are pushed and popped.
        items = list(self.items[::-1])
        first_name = self.first_name
        second_name = self.second_name

        while items:
            # `first_item` will be a Constrainable or a LinearSymbolic.
            # For the first iteration, this is enforced by 'validate'.
            # For subsequent iterations, this condition is enforced by
            # the fact that only those types are pushed onto the stack.
            first_item = items.pop()
            if isinstance(first_item, Constrainable):
                first_anchor = getattr(first_item, first_name)
            else:  # LinearSymbolic
                first_anchor = first_item

            # Grab the next item off the stack. It will be an instance
            # of Constrainable, LinearSymbolic, Spacer, or int (this is
            # enforced by 'validate'). If it can't provide an anchor,
            # grab the one after it which can. If no space is given, use
            # the default spacing.
            next_item = items.pop()
            if isinstance(next_item, Spacer):
                spacer = next_item
                second_item = items.pop()
            elif isinstance(next_item, int):
                spacer = EqSpacer(next_item)
                second_item = items.pop()
            else:  # Constrainable or LinearSymbolic
                spacer = EqSpacer(self.spacing)
                second_item = next_item

            # Grab the anchor for the second item in the pair.
            if isinstance(second_item, Constrainable):
                second_anchor = getattr(second_item, second_name)
            else:  # LinearSymbolic
                second_anchor = second_item

            # Use the spacer to generate the constraint for the pair.
            cns.extend(spacer.create_constraints(first_anchor, second_anchor))

            # If the stack is not empty, the second_item will be used as
            # the first_item in the next iteration.
            if items:
                items.append(second_item)

        return cns
