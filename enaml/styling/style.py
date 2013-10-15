#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.core.declarative import Declarative

from .property import Property


class Style(Declarative):
    """ A declarative class for defining Enaml style sheet styles.

    """
    def properties(self):
        """ Get the properties comprising the style.

        Returns
        -------
        result : list
            The list of Property objects declared for the style.

        """
        return [c for c in self.children if isinstance(c, Property)]
