#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int

from enaml.core.declarative import Declarative, d_


class Margin(Declarative):
    """ A style sheet property for defining a widget's margin.

    """
    #: The value to apply to all margin widths. The default is -1.
    width = d_(Int(-1))

    #: The width to apply to the left margin. This will override the
    #: value set by the 'width' attribute. The default is -1.
    left = d_(Int(-1))

    #: The width to apply to the right margin. This will override the
    #: value set by the 'width' attribute. The default is -1.
    right = d_(Int(-1))

    #: The width to apply to the top margin. This will override the
    #: value set by the 'width' attribute. The default is -1.
    top = d_(Int(-1))

    #: The width to apply to the bottom margin. This will override the
    #: value set by the 'width' attribute. The default is -1.
    bottom = d_(Int(-1))
