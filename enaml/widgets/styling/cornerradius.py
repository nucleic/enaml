#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Int, Coerced


class CornerRadius(Atom):
    """ An Atom class for defining a corner radius.

    Once a corner radius is created it should be treated as read only.
    User code should create a new corner radius object if the parameters
    need to be changed.

    """
    #: The top left radius.
    top_left = Int(0)

    #: The top right radius.
    top_right = Int(0)

    #: The bottom right radius.
    bottom_right = Int(0)

    #: The bottom left radius.
    bottom_left = Int(0)

    @classmethod
    def create(cls, *values):
        """ An alternate constructor which accepts variadic parameters.

        Parameters
        ----------
        *values
            The integer values from which to construct a corner radius.
            There must between 1 and 4 values, inclusive. The order of
            the values follows the CSS conventions for border radius.

        Returns
        -------
        result : CornerRadius
            The corner radius object for the given values.

        """
        n = len(values)
        if n == 1:
            a = b = c = d = values[0]
        elif n == 2:
            a = c = values[0]
            b = d = values[1]
        elif n == 3:
            a = values[0]
            b = d = values[1]
            c = values[2]
        elif n == 4:
            a, b, c, d = values
        elif n == 0:
            raise ValueError('need more than zero values to unpack')
        else:
            raise ValueError('too many values to unpack')
        radius = cls()
        radius.top_left = a
        radius.top_right = b
        radius.bottom_right = c
        radius.bottom_left = d
        return radius


def coerce_corner_radius(value):
    """ The coercing function for the CornerRadiusMember.

    """
    try:
        if isinstance(value, int):
            return CornerRadius.create(value)
        return CornerRadius.create(*value)
    except (ValueError, TypeError):
        pass


class CornerRadiusMember(Coerced):
    """ An Atom member class which coerces a value to a corner radius.

    A corner radius member can be set to an int, a sequence of ints, a
    CornerRadius, or None. If the coercing fails, the value will be
    None.

    If a sequence of ints is provided, it must have a length between 1
    and 4, inclusive. The order of the sequence, and the fill order for
    missing values follows the CSS conventions for border radius.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a CornerRadiusMember.

        default : CornerRadius, int, sequence of ints, or None, optional
            The default corner radius to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        """
        if factory is None:
            factory = lambda: default
        kind = (CornerRadius, type(None))
        sup = super(CornerRadiusMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_corner_radius)
