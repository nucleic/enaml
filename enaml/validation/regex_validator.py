#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re

from atom.api import Str

from .validator import Validator


class RegexValidator(Validator):
    """ A concrete Validator which handles text input.

    This validator ensures that the text matches a provided regular
    expression string.

    """
    #: The regular expression string to use for validation. The default
    #: regex matches everything.
    regex = Str(r'.*')

    def validate(self, text, component):
        """ Validates the given text matches the regular expression.

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
        return (text, bool(re.match(self.regex, text)))

    def client_validator(self):
        """ The client side regex validator.

        Returns
        -------
        result : dict
            The dict representation of the client side regex validator.

        """
        res = {}
        res['type'] = 'regex'
        res['message'] = self.message
        res['arguments'] = {'regex': self.regex}
        return res
