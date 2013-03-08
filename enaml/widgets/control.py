#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .constraints_widget import ConstraintsWidget


class Control(ConstraintsWidget):
    """ A widget which represents a leaf node in the hierarchy.

    A Control is conceptually the same as a ConstraintsWidget, except
    that it does not have widget children. This base class serves as
    a placeholder for potential future functionality.

    """
    pass

