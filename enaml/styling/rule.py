#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Typed, Unicode

from enaml.core.declarative import Declarative, d_

from .style import Style


class Rule(Declarative):
    """ A declarative class for defining a style sheet rule.

    """
    #: The name of the widget type which will match this rule. This
    #: can be a comma-separated string to match more than one type.
    #: An empty string will match all widget types.
    kind = d_(Str())

    #: The name of the widget group which will match this rule. This
    #: can be a comma-separated string to match more than one group.
    #: An empty string will match all widget groups.
    group = d_(Unicode())

    #: The object name of the widget which will match this rule. This
    #: can be a comma-separated string to match more than one name.
    #: An empty string will match all widget names.
    name = d_(Unicode())

    #: The style to apply to the widgets which match this rule. If
    #: this is not provided, the style will be created based on the
    #: children defined on the rule.
    style = d_(Typed(Style))

    def get_style(self):
        """ Get the effective style object for this rule.

        If a style is not defined for the 'style' attribute, then the
        last Style object defined as a child will be used for the rule.

        Returns
        -------
        result : Style or None
            The effective style for the rule, or None if not defined.

        """
        if self.style is not None:
            return self.style
        for child in reversed(self.children):
            if isinstance(child, Style):
                return child
