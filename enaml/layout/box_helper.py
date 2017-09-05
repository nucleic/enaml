#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .constrainable import ContentsConstrainable, ConstrainableMixin
from .constraint_helper import ConstraintHelper


BOUNDARY_ATTRS = (
    'top',
    'bottom',
    'left',
    'right',
)


CONTENT_BOUNDARY_ATTRS = (
    'contents_top',
    'contents_bottom',
    'contents_left',
    'contents_right',
)


class BoxHelper(ConstraintHelper, ConstrainableMixin):
    """ A constraint helper for creating a box layouts.

    Instances of BoxHelper are Constrainable and can be nested in other
    box helpers to build up complex layouts. This is a base class which
    should be subclassed to implement the desired functionality.

    """
    def box_constraints(self, component):
        """ Generate the boundary constraints for the box.

        """
        cns = []
        if component is not None:
            a_attrs = b_attrs = BOUNDARY_ATTRS
            if isinstance(component, ContentsConstrainable):
                b_attrs = CONTENT_BOUNDARY_ATTRS
            f = lambda a, b: getattr(self, a) == getattr(component, b)
            cns.extend(f(a, b) for a, b in zip(a_attrs, b_attrs))
        return cns
