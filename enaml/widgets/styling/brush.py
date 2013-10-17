#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Coerced

from enaml.colors import Color, parse_color

from .gradient import Gradient, parse_gradient


def coerce_brush(value):
    """ The coercing function for the BrushMember.

    """
    if isinstance(value, basestring):
        color = parse_color(value)
        if color is not None:
            return color
        gradient = parse_gradient(value)
        if gradient is not None:
            return gradient


class BrushMember(Coerced):
    """ An Atom member class which coerces a value to a brush.

    A brush can be a color or a gradient. This member can be set to a
    string, Color, Gradient, or None. If set to a string, it will be
    coerced to an appropriate Color or Gradient. If the coercing fails,
    the value will be None.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a BrushMember.

        default : string, Color, Gradient, or None, optional
            The default value to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        """
        if factory is None:
            factory = lambda: default
        kind = (Color, Gradient, type(None))
        sup = super(BrushMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_brush)
