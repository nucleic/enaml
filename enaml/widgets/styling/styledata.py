#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.core.declarative import Declarative, d_

from .border import Border
from .margin import Margin
from .padding import Padding


class StyleData(Declarative):
    """ A declarative class for defining Enaml style data objects.

    A style data object is used to store the fully resolved values for
    the style properties.

    """
    #: The margin definition for the widget. This will be overridden by
    #: any Margin child defined on the style.
    margin = d_(Typed(Margin))

    #: The padding for the widget. This will be overridden by any
    #: Padding child defined on the style.
    padding = d_(Typed(Padding))

    #: The border definition for the widget. This will be overridden by
    #: any Border child defined on the style.
    border = d_(Typed(Border))
