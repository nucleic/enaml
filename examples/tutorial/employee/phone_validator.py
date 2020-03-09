#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import unicode_literals

import re

from enaml.validator import Validator


class PhoneNumberValidator(Validator):
    """ A really dumb phone number validator.

    """
    all_digits = re.compile(r'[0-9]{10}$')

    dashes = re.compile(r'([0-9]{3})\-([0-9]{3})\-([0-9]{4})$')

    proper = re.compile(r'\(([0-9]{3})\)\ ([0-9]{3})\-([0-9]{4})$')

    def validate(self, text):
        """ Validate the input text.

        The text must be in of the form: (555) 555-5555 in order to
        pass the standard validation. The fixup method will convert
        some alternative forms into a correct format.

        """
        return bool(self.proper.match(text))

    def fixup(self, text):
        """ Attempt to convert the given text into the proper format.

        This method is called by the backend when the current text is
        not valid, but can maybe be *made* to be valid by this method.
        The returned text is re-validated to test for viability.

        """
        match = self.dashes.match(text)
        if match:
            area = match.group(1)
            prefix = match.group(2)
            suffix = match.group(3)
            return '(%s) %s-%s' % (area, prefix, suffix)
        match = self.all_digits.match(text)
        if match:
            area = text[:3]
            prefix = text[3:6]
            suffix = text[6:10]
            return '(%s) %s-%s' % (area, prefix, suffix)
        return text
