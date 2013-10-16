#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from .border import Border
from .margin import Margin
from .padding import Padding


class StyleData(Atom):
    """ A class for storing a widget's style data.

    A style data object defines the available properties which can be
    set by style sheet setters. The object is managed internally by a
    widget and will not typically be used directly by user code.

    """
    #: The resolved margin definition for the widget.
    margin = Typed(Margin)

    #: The resolved padding definition for the widget.
    padding = Typed(Padding)

    #: The resolved border definition for the widget.
    border = Typed(Border)

    def apply(self, setter):
        print 'apply', setter
