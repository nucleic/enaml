#------------------------------------------------------------------------------
#  Copyright (c) 2013, Nucleic Development Team.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

from enaml.validator import Validator


class PhoneNumberValidator(Validator):
    """ A really dumb phone number validator.

    """
    all_digits = re.compile(r'[0-9]{10}$')

    dashes = re.compile(r'([0-9]{3})\-([0-9]{3})\-([0-9]{4})$')

    proper = re.compile(r'\(([0-9]{3})\)\ ([0-9]{3})\-([0-9]{4})$')

    def validate(self, text, component):
        match = self.proper.match(text) or self.dashes.match(text)
        if match:
            area = match.group(1)
            prefix = match.group(2)
            suffix = match.group(3)
            formatted_text = '(%s) %s-%s' % (area, prefix, suffix)
            return formatted_text, True
        match = self.all_digits.match(text)
        if match:
            area = text[:3]
            prefix = text[3:6]
            suffix = text[6:10]
            formatted_text = '(%s) %s-%s' % (area, prefix, suffix)
            return formatted_text, True
        return text, False
