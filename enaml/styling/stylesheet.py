#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.core.declarative import Declarative

from .rule import Rule


class StyleSheet(Declarative):
    """ A declarative class for defining Enaml style sheets.

    """
    def rules(self):
        """ Get the rules comprising this style sheet.

        Returns
        -------
        result : list
            The list of Rule objects declared for the style sheet.

        """
        return [c for c in self.children if isinstance(c, Rule)]
