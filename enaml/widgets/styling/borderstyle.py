#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, Coerced


#: A tuple of the allowed border style values.
BorderStyle = (
    'none',
    'dot-dash',
    'dot-dot-dash',
    'dotted',
    'double',
    'groove',
    'inset',
    'outset',
    'ridge',
    'solid',
)


class BorderStyle(Atom):
    """ An Atom class for defining a border style.

    Once a border style is created it should be treated as read only.
    User code should create a new border style object if the parameters
    need to be changed.

    """
    #: The top border style.
    top = Enum(BorderStyle)

    #: The right border style.
    right = Enum(BorderStyle)

    #: The bottom border style.
    bottom = Enum(BorderStyle)

    #: The left border style.
    left = Enum(BorderStyle)

    @classmethod
    def create(cls, *values):
        """ An alternate constructor which accepts variadic parameters.

        Parameters
        ----------
        *values
            The string values from which to construct a border style.
            There must between 1 and 4 values, inclusive. The order of
            the values follows the CSS conventions for border style.

        Returns
        -------
        result : BorderStyle
            The border style object for the given values.

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
        style = cls()
        style.top = t
        style.right = r
        style.bottom = b
        style.left = l
        return style


def coerce_border_style(value):
    """ The coercing function for the BorderStyleMember.

    """
    try:
        if isinstance(value, basestring):
            return BorderStyle.create(value)
        return BorderStyle.create(*value)
    except (ValueError, TypeError):
        pass


class BorderStyleMember(Coerced):
    """ An Atom member class which coerces a value to a border style.

    A border style member can be set to a string, a sequence of strings,
    a BorderStyle, or None. If the coercing fails, the value will be
    None.

    If a sequence of strings is provided, it must have a length between
    1 and 4, inclusive. The order of the sequence, and the fill order
    for missing values follows the CSS conventions for border style.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a BorderStyleMember.

        default : BorderStyle, string, seq of strings, or None, optional
            The default border style to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        """
        if factory is None:
            factory = lambda: default
        kind = (BorderStyle, type(None))
        sup = super(BorderStyleMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_border_style)
