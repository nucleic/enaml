#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Value, observe

from enaml.core.declarative import Declarative, d_


class Property(Declarative):
    """ A declarative class for defining a property in a style.

    The supported style properties and the types of values supported
    for the style depend upon the implementation of a given toolkit
    backend. In all cases, empty names and None values are ignored.

    """
    #: The name of the style property.
    name = d_(Str())

    #: The value to apply to the style property. The value type must
    #: be compatible with the specified property name.
    value = d_(Value())

    #: Private storage for the toolkit backend. This value is cleared
    #: when the name or the value of the property is changed.
    _tkdata = Value()

    @observe('name', 'value')
    def _invalidate_tkdata(self, change):
        """ An observer which clears the tkdata when needed.

        """
        self._tkdata = None
