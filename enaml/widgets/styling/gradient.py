#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Coerced, Float, List

from enaml.colors import ColorMember
from enaml.layout.geometry import PosF


class GradientStop(Atom):
    """ A class for defining gradient color stops.

    """
    #: The percentage offset from the start for the given color.
    offset = Float(0.0)

    #: The color to apply for this gradient stop.
    color = ColorMember()


class Gradient(Atom):
    """ A base class for defining color gradients.

    This class should not be used directly by user code. Use one of the
    concrete gradient subclasses instead.

    """
    #: The list of color stops for the gradient.
    stops = List(GradientStop)


class LinearGradient(Gradient):
    """ A gradient class for defining linear gradients.

    """
    #: The starting point of the gradient, in logical coordinates.
    start = Coerced(PosF, (0.0, 0.0))

    #: The ending point of the gradient, in logical coordinates.
    end = Coerced(PosF, (1.0, 1.0))


class RadialGradient(Gradient):
    """ A gradient class for defining radial gradients.

    """
    #: The center point of the gradient, in logical coordinates.
    center = Coerced(PosF, (0.0, 0.0))

    #: The focal point of the gradient, in logical coordinates.
    focal_point = Coerced(PosF, (0.0, 0.0))

    #: The radius of the gradient, in logical coordinates.
    radius = Float(1.0)
