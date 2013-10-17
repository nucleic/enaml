#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Coerced

from enaml.colors import Color

from .brush import BrushMember
from .gradient import Gradient


class BorderColor(Atom):
    """ An Atom class for defining a border color.

    Once a border color is created it should be treated as read only.
    User code should create a new border color object if the parameters
    need to be changed.

    """
    #: The top border color.
    top = BrushMember()

    #: The right border color.
    right = BrushMember()

    #: The bottom border color.
    bottom = BrushMember()

    #: The left border color.
    left = BrushMember()

    @classmethod
    def create(cls, *values):
        """ An alternate constructor which accepts variadic parameters.

        Parameters
        ----------
        *values
            The values from which to construct a border color. There
            must between 1 and 4 values, inclusive. The order of the
            values follows the CSS conventions for border color. They
            can be any type which can be coerced by a BrushMember.

        Returns
        -------
        result : BorderColor
            The border color object for the given values.

        """
        n = len(values)
        if n == 1:
            t = r = b = l = values[0]
        elif n == 2:
            t = b = values[0]
            l = r = values[1]
        elif n == 3:
            t = values[0]
            l = r = values[1]
            b = values[2]
        elif n == 4:
            t, r, b, l = values
        elif n == 0:
            raise ValueError('need more than zero values to unpack')
        else:
            raise ValueError('too many values to unpack')
        color = cls()
        color.top = t
        color.right = r
        color.bottom = b
        color.left = l
        return color


def coerce_border_color(value):
    """ The coercing function for the BorderColorMember.

    """
    try:
        if isinstance(value, (basestring, Color, Gradient)):
            return BorderColor.create(value)
        return BorderColor.create(*value)
    except (ValueError, TypeError):
        pass


class BorderColorMember(Coerced):
    """ An Atom member class which coerces a value to a border color.

    A border color member can be set to a value or sequence of values
    which can be coerced by a BrushMember, a BorderColor, or None. If
    the coercing fails, the value will be None.

    If a sequence is provided, it must have a length between 1 and 4,
    inclusive. The order of the sequence, and the fill order for missing
    values follows the CSS conventions for border color.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a BorderColorMember.

        default : object or None, optional
            The compatible default border color to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        """
        if factory is None:
            factory = lambda: default
        kind = (BorderColor, type(None))
        sup = super(BorderColorMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_border_color)
