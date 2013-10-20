#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Coerced, Str, Value, observe

from enaml.core.declarative import Declarative, d_


class Rule(Declarative):
    """ A declarative class for defining a rule in a style.

    The supported style properties and the types of values supported
    for the style depend upon the implementation of a given toolkit
    backend. In all cases, empty names and values are ignored.

    """
    #: The name of the rule's style property.
    name = d_(Str())

    #: The value to apply to the rule's style property.
    value = d_(Str())

    #: Private storage for the toolkit backend. This value is cleared
    #: when the name or the value of the property is changed.
    _tkdata = Value()

    @observe('name', 'value')
    def _invalidate_tkdata(self, change):
        """ An observer which clears the tkdata when needed.

        """
        self._tkdata = None


def coerce_tuple(item):
    """ The coercing function for the style selectors.

    """
    if isinstance(item, tuple):
        return item
    if isinstance(item, list):
        return tuple(item)
    return (item,)


class Style(Declarative):
    """ A declarative class for defining a style in a style sheet

    """
    #: The name of the widget type which will match this style. This
    #: can be a string or tuple|list of strings to match more than one
    #: type. An empty string or tuple|list will match all widget types.
    typename = d_(Coerced(tuple, coercer=coerce_tuple))

    #: The name of the widget style class which will match this style.
    #: This can be a string or tuple|list of strings to match more than
    #: one style class. An empty string or tuple|list will match all
    #: style classes.
    styleclass = d_(Coerced(tuple, coercer=coerce_tuple))

    #: The object name of the widget which will match this style. This
    #: can be a string or tuple|list of strings to match more than one
    #: name. An empty string or tuple|list will match all widget names.
    name = d_(Coerced(tuple, coercer=coerce_tuple))

    #: The object state to which the style applies. The default state
    #: is an empty string and applies to all states of a widget unless
    #: overridden by a more specific state. The states supported by a
    #: widget are toolkit dependent.
    state = d_(Str())

    #: The subcontrol to which the style applies. The default is an
    #: empty string and indicates that the style does not apply to a
    #: subcontrol. The subcontrols supported by a widget are toolkit
    #: dependent.
    subcontrol = d_(Str())

    def rules(self):
        """ Get the rules declared for the style.

        Returns
        -------
        result : list
            The list of Rule objects declared for the style.

        """
        return [c for c in self.children if isinstance(c, Rule)]

    def match(self, item):
        """ Get the whether or not an item matches this style.

        Parameters
        ----------
        item : Widget
            The enaml widget to test for a style match.

        Returns
        -------
        result : int
            An integer indicating the match for the given item. A value
            less than zero indicates no match. A value greater than or
            equal to zero indicates a match and the specificity of that
            match.

        """
        specificity = 0

        names = self.name
        if names:
            name = item.name
            if name and name in names:
                specificity += 4
            else:
                return -1

        classes = self.styleclass
        if classes:
            styleclass = item.styleclass
            if styleclass and styleclass in classes:
                specificity += 2
            else:
                return -1

        types = self.typename
        if types:
            for t in type(item).__mro__:
                if t.__name__ in types:
                    specificity += 1
                    break
            else:
                return -1

        return specificity


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
