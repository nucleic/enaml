#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Int, Coerced


class Thickness(Atom):
    """ An Atom class for defining a thickness.

    Once a thickness is created it should be treated as read only. User
    code should create a new thickness object if the parameters need to
    be changed.

    """
    #: The top side thickness.
    top = Int(0)

    #: The right side thickness.
    right = Int(0)

    #: The bottom side thickness.
    bottom = Int(0)

    #: The left side thickness.
    left = Int(0)

    @classmethod
    def create(cls, *values):
        """ An alternate constructor which accepts variadic parameters.

        Parameters
        ----------
        *values
            The integer values from which to construct a thickness.
            There must between 1 and 4 values, inclusive. The order of
            the values follows the CSS conventions for margin.

        Returns
        -------
        result : Thickness
            The thickness object for the given values.

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
        thickness = cls()
        thickness.top = t
        thickness.right = r
        thickness.bottom = b
        thickness.left = l
        return thickness


def coerce_thickness(value):
    """ The coercing function for the ThicknessMember.

    """
    try:
        if isinstance(value, int):
            return Thickness.create(value)
        return Thickness.create(*value)
    except (ValueError, TypeError):
        pass


class ThicknessMember(Coerced):
    """ An Atom member class which coerces a value to a thickness.

    A thickness member can be set to a int, a sequence of ints, a
    Thickness, or None. If the coercing fails, the value will be None.

    If a sequence of ints is provided, it must have a length between 1
    and 4, inclusive. The order of the sequence, and the fill order for
    missing values follows the CSS conventions for margin.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a ThicknessMember.

        default : Thickness, int, sequence of ints, or None, optional
            The default thickness to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        """
        if factory is None:
            factory = lambda: default
        kind = (Thickness, type(None))
        sup = super(ThicknessMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_thickness)
