#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Coerced, Enum, Range, Tuple

from .box_helper import BoxHelper
from .constrainable import Constrainable
from .constraint_helper import ConstraintHelper
from .geometry import Box
from .linear_symbolic import LinearSymbolic
from .sequence_helper import SequenceHelper
from .spacers import Spacer, EqSpacer, FlexSpacer


ORIENT_MAP = {
    'horizontal': ('left', 'right'),
    'vertical': ('top', 'bottom'),
}


ORTHO_MAP = {
    'horizontal': 'vertical',
    'vertical': 'horizontal',
}


class LinearBoxHelper(BoxHelper):
    """ A box helper for creating traditional linear box layouts.

    """
    #: The layout orientation of the items in the box.
    orientation = Enum('vertical', 'horizontal')

    #: The tuple of items which will be used to generate the constraints.
    items = Tuple()

    #: The spacing to use between items if not explicitly provided.
    spacing = Range(low=0)

    #: The margins to use around the edges of the box.
    margins = Coerced(Box)

    def __init__(self, orientation, items, spacing=10, margins=0):
        """ Initialize a LinearBoxHelper.

        Parameters
        ----------
        orientation : str
            The orientation of the layout box, either 'horizontal'
            or 'vertical'.

        items : iterable
            The iterable of items which should be constrained.

        spacing : int, optional
            The spacing to use between items if not specifically given
            in the sequence of items. The default value is 10 pixels.

        margins : int, tuple, or Box, optional
            The margins to use around the edges of the box. The default
            value is 0 pixels on all sides.

        """
        self.orientation = orientation
        self.items = self.validate(items)
        self.spacing = spacing
        self.margins = margins

    @staticmethod
    def validate(items):
        """ Validate an iterable of constrainable box items.

        This method asserts that a sequence of items is appropriate for
        generating box constraints. The following conditions are verified
        of the sequence of items after they are filtered for None:

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

        if len(items) == 0:
            return items

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
        """ Generate the box constraints for the given component.

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
        items = self.items
        if len(items) == 0:
            return []

        # Create the outer boundary box constraints.
        cns = self.box_constraints(component)

        first, last = ORIENT_MAP[self.orientation]
        first_ortho, last_ortho = ORIENT_MAP[ORTHO_MAP[self.orientation]]
        first_boundary = getattr(self, first)
        last_boundary = getattr(self, last)
        first_ortho_boundary = getattr(self, first_ortho)
        last_ortho_boundary = getattr(self, last_ortho)

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
        spacer_types = (Spacer, int)
        if not isinstance(items[0], spacer_types):
            pre_items = (first_boundary, first_spacer)
        else:
            pre_items = (first_boundary,)
        if not isinstance(items[-1], spacer_types):
            post_items = (last_spacer, last_boundary)
        else:
            post_items = (last_boundary,)

        # Create the helper for the primary orientation. The helper
        # validation is bypassed since the sequence is known-valid.
        spacing = self.spacing
        helper = SequenceHelper(last, first, (), spacing)
        helper.items = pre_items + items + post_items
        helpers = [helper]

        # Add the ortho orientation and nested helpers. The helper
        # validation is bypassed since the sequence is known-valid.
        for item in items:
            if isinstance(item, Constrainable):
                helper = SequenceHelper(last_ortho, first_ortho, (), spacing)
                helper.items = (first_ortho_boundary, first_ortho_spacer,
                                item, last_ortho_spacer, last_ortho_boundary)
                helpers.append(helper)
            if isinstance(item, ConstraintHelper):
                helpers.append(item)

        # Add in the helper constraints.
        for helper in helpers:
            cns.extend(helper.create_constraints(None))

        return cns
