#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.core.declarative import Declarative

from .style import Style


class StyleSheet(Declarative):
    """ A declarative class for defining Enaml widget style sheets.

    """
    def styles(self):
        """ Get the styles declared for the style sheet.

        Returns
        -------
        result : list
            The list of Style objects declared for the style sheet.

        """
        return [c for c in self.children if isinstance(c, Style)]
