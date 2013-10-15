#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Enum

from enaml.colors import ColorMember
from enaml.core.declarative import d_

from .property import Property


BorderStyles = (
    '', 'dot-dash', 'dot-dot-dash', 'dotted', 'double', 'groove', 'inset',
    'outset', 'ridge', 'solid', 'none'
)


class Border(Property):
    """ A style sheet property for defining a widget's border.

    """
    #: The value to apply to all border widths. The default is -1.
    width = d_(Int(-1))

    #: The width to apply to the left border. This will override the
    #: value set by the 'width' attribute. The default is -1.
    left = d_(Int(-1))

    #: The width to apply to the right border. This will override the
    #: value set by the 'width' attribute. The default is -1.
    right = d_(Int(-1))

    #: The width to apply to the top border. This will override the
    #: value set by the 'width' attribute. The default is -1.
    top = d_(Int(-1))

    #: The width to apply to the bottom border. This will override the
    #: value set by the 'width' attribute. The default is -1.
    bottom = d_(Int(-1))

    #: The value to apply to all border radii. The default is -1.
    radius = d_(Int(-1))

    #: The radius to apply to the top left corner. This will override
    #: the value set by the 'radius' attribute. The default is -1.
    top_left_radius = d_(Int(-1))

    #: The radius to apply to the top right corner. This will override
    #: the value set by the 'radius' attribute. The default is -1.
    top_right_radius = d_(Int(-1))

    #: The radius to apply to the bottom left corner. This will override
    #: the value set by the 'radius' attribute. The default is -1.
    bottom_left_radius = d_(Int(-1))

    #: The radius to apply to the bottom right corner. This will override
    #: the value set by the 'radius' attribute. The default is -1.
    bottom_right_radius = d_(Int(-1))

    #: The color to apply to the entire border.
    color = d_(ColorMember())

    #: The color to apply to the left border. This will override the
    #: value set by the 'color' attribute.
    left_color = d_(ColorMember())

    #: The color to apply to the right border. This will override the
    #: value set by the 'color' attribute.
    right_color = d_(ColorMember())

    #: The color to apply to the top border. This will override the
    #: value set by the 'color' attribute.
    top_color = d_(ColorMember())

    #: The color to apply to the bottom border. This will override the
    #: value set by the 'color' attribute.
    bottom_color = d_(ColorMember())

    #: The style for the border. The default is the empty string.
    style = d_(Enum(BorderStyles))

    #: The style to apply to the left border. This will override the
    #: value set by the 'style' attribute.
    left_style = d_(Enum(BorderStyles))

    #: The style to apply to the right border. This will override the
    #: value set by the 'style' attribute.
    right_style = d_(Enum(BorderStyles))

    #: The style to apply to the top border. This will override the
    #: value set by the 'style' attribute.
    top_style = d_(Enum(BorderStyles))

    #: The style to apply to the bottom border. This will override the
    #: value set by the 'style' attribute.
    bottom_style = d_(Enum(BorderStyles))
