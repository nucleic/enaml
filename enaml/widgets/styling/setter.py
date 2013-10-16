#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Value

from enaml.core.declarative import Declarative, d_


class Setter(Declarative):
    """ A declarative class for defining a style property setter.

    """
    #: The name of the style property to apply with this setter. Dotted
    #: attribute notation is allowed.
    name = d_(Str())

    #: The value to apply to the style property. The type of the value
    #: must be compatible with the specified style property. A value of
    #: None indicates that the style property should be reverted to the
    #: the default. This value will be overridden by any child defined
    #: on the setter.
    value = d_(Value())

    def child_added(self, child):
        """ A child added event handler.

        This handler will assign the child as the value for the setter.

        """
        super(Setter, self).child_added(child)
        self.value = child

    def child_removed(self, child):
        """ A child removed event handler.

        This handler will update the value for the setter if needed.

        """
        super(Setter, self).child_removed(child)
        if child is self.value:
            children = self.children
            self.value = children[-1] if children else None
