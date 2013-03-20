#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Bool, observe

from enaml.core.declarative import d_

from .widget import Widget
from .toolkit_object import ToolkitObject, ProxyToolkitObject

class ProxyTransientStatusWidgets(ProxyToolkitObject):
    """ The abstract definition of a proxy TransientStatusWidgets object

    """
    # A reference to the StatusBar declaration
    declaration = ForwardTyped(lambda: TransientStatusWidgets)


class TransientStatusWidgets(ToolkitObject):
    """ A non-visible goruping  used to contain the permanent members of a StatusBar

    """
 
    #: A reference to the ProxyTransientStatusWidgets
    proxy = Typed(ProxyTransientStatusWidgets)

    def items(self):
        """ Get the items on this widget

        Returns
        -------
        result : tuple
            The tuple of Widgets defined as children of this TransientStatusWidget.

        """
        isinst = isinstance
        widgets = (child for child in self.children if isinst(child, Widget))
        return tuple(widgets)


