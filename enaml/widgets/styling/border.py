#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom

from .bordercolor import BorderColorMember
from .borderstyle import BorderStyleMember
from .cornerradius import CornerRadiusMember
from .thickness import ThicknessMember


class Border(Atom):
    """ An atom object for defining a border.

    Once a border is created it should be treated as read only. User
    code should create a new border object if the parameters need to
    be changed.

    """
    #: The thickness to apply to the border. It can be an int, a
    #: sequence of ints, a Thickness object, or None.
    thickness = ThicknessMember()

    #: The radius to apply to the border. It can be an int, a sequence
    #: of ints, a CornerRadius object, or None.
    radius = CornerRadiusMember()

    #: The color to apply to the border. It can be a string, a Color
    #: object, a Gradient object, a sequence of the previous types,
    #: a BorderColor object, or None.
    color = BorderColorMember()

    #: The style to apply to the border. It can be a string, a tuple of
    #: strings, a BorderStyle object, or None.
    style = BorderStyleMember()
