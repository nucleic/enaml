#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Enum, null

from .validator import Validator


class IntValidator(Validator):
    """ A concrete Validator which handles integer input.

    This validator ensures that the text represents an integer within a
    specified range in a specified base.

    """
    #: The minimum value allowed for the int, inclusive, or null if
    #: there is no lower bound.
    minimum = Typed(int)

    #: The maximum value allowed for the int, inclusive, or null if
    #: there is no upper bound.
    maximum = Typed(int)

    #: The base in which the int is represented.
    base = Enum(10, 2, 8, 16)

    def convert(self, text):
        """ Converts the text to an int in the given base.

        Parameters
        ----------
        text : unicode
            The unicode text to convert to an integer.

        Returns
        -------
        result : int
            The integer value for the converted text.

        Raises
        ------
        ValueError
            A ValueError will be raised if the conversion fails.

        """
        return int(text, self.base)

    def validate(self, text, component):
        """ Validates the given text matches the integer range.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        try:
            value = self.convert(text)
        except ValueError:
            return (text, False)
        minimum = self.minimum
        if minimum is not null and value < minimum:
            return (text, False)
        maximum = self.maximum
        if maximum is not null and value > maximum:
            return (text, False)
        return (text, True)

    def client_validator(self):
        """ The client side int validator.

        Returns
        -------
        result : dict
            The dict representation of the client side int validator.

        """
        res = {}
        res['type'] = 'int'
        res['message'] = self.message
        res['arguments'] = {
            'minimum': self.minimum if self.minimum is not null else None,
            'maximum': self.maximum if self.maximum is not null else None,
            'base': self.base
        }
        return res

