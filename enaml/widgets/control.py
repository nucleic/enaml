#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget


class ProxyControl(ProxyConstraintsWidget):
    """ The abstract definition of a proxy Control object.

    """
    #: A reference to the Control declaration.
    declaration = ForwardTyped(lambda: Control)


class Control(ConstraintsWidget):
    """ A widget which represents a leaf node in the hierarchy.

    A Control is conceptually the same as a ConstraintsWidget, except
    that it does not have widget children. This base class serves as
    a placeholder for potential future functionality.

    """
    #: A reference to the proxy Control object.
    proxy = Typed(ProxyControl)
