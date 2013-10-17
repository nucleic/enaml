#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Unicode

from enaml.core.declarative import Declarative, d_

from .property import Property


class Style(Declarative):
    """ A declarative class for defining a style in a style sheet

    """
    #: The name of the widget type which will match this style. This
    #: can be a comma-separated string to match more than one type.
    #: An empty string will match all widget types.
    typename = d_(Str())

    #: The name of the widget group which will match this style. This
    #: can be a comma-separated string to match more than one group.
    #: An empty string will match all widget groups.
    group = d_(Unicode())

    #: The object name of the widget which will match this style. This
    #: can be a comma-separated string to match more than one name.
    #: An empty string will match all widget names.
    name = d_(Unicode())

    def properties(self):
        """ Get the properties declared for the style.

        Returns
        -------
        result : list
            The list of Property objects declared for the style.

        """
        return [c for c in self.children if isinstance(c, Property)]
