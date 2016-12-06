#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import re

from atom.api import Atom, Bool, Typed, Enum, Str, Unicode


class Validator(Atom):
    """ The base class for creating widget text validators.

    This class is abstract. It's abstract api must be implemented by a
    subclass in order to be usable.

    """
    #: An optional message to associate with the validator. This message
    #: may be used by the toolkit to display information to the user
    #: about what went wrong.
    message = Unicode()

    def validate(self, text):
        """ Validate the text as the user types.

        This method is called on every keystroke to validate the text
        as the user inputs characters. It should be efficient. This is
        an abstract method which must be implemented by subclasses.

        Parameters
        ----------
        text : unicode
            The unicode text entered by the user.

        Returns
        -------
        result : bool
            True if the text is valid, False otherwise.

        """
        raise NotImplementedError

    def fixup(self, text):
        """ An optional method to fix invalid user input.

        This method will be called if user attempts to apply text which
        is not valid. This method may convert the text to a valid form.
        The returned text will be retested for validity. The default
        implementation of this method is a no-op.

        Returns
        -------
        result : unicode
            The optionally modified input text.

        """
        return text


class IntValidator(Validator):
    """ A concrete Validator which handles integer input.

    This validator ensures that the text represents an integer within a
    specified range in a specified base.

    """
    #: The minimum value allowed for the int, inclusive, or None if
    #: there is no lower bound.
    minimum = Typed(int)

    #: The maximum value allowed for the int, inclusive, or None if
    #: there is no upper bound.
    maximum = Typed(int)

    #: The base in which the int is represented.
    base = Enum(10, 2, 8, 16)

    #: Whether or not to automatically fix user input if it is
    #: outside of the bounds set by minimum and maximum
    fix_invalid_input = Bool(False)

    def validate(self, text):
        """ Validates the given text matches the integer range.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        Returns
        -------
        result : bool
            True if the text is valid, False otherwise.

        """
        try:
            value = int(text, self.base)
        except ValueError:
            return False
        minimum = self.minimum
        if minimum is not None and value < minimum:
            return False
        maximum = self.maximum
        if maximum is not None and value > maximum:
            return False
        return True

    def fixup(self, text):
        """ Fix the user input if fix_input is True

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        Returns
        -------
        result : int
            The value to place into the client widget
        """
        if self.fix_invalid_input:
            try:
                value = int(text)
                if self.minimum is not None and value < self.minimum:
                    text = self.minimum
                elif self.maximum is not None and value > self.maximum:
                    text = self.maximum
            except ValueError:
                # text isn't an int, return the input text
                text = self.minimum
        return str(text)

class FloatValidator(Validator):
    """ A concrete Validator which handles floating point input.

    This validator ensures that the text represents a floating point
    number within a specified range.

    """
    #: The minimum value allowed for the float, inclusive, or None if
    #: there is no lower bound.
    minimum = Typed(float)

    #: The maximum value allowed for the float, inclusive, or None if
    #: there is no upper bound.
    maximum = Typed(float)

    #: Whether or not to allow exponents like '1e6' in the input.
    allow_exponent = Bool(True)

    #: Whether or not to automatically fix user input if it is
    #: outside of the bounds set by minimum and maximum
    fix_invalid_input = Bool(False)

    def validate(self, text):
        """ Validates the given text matches the float range.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        Returns
        -------
        result : bool
            True if the text is valid, False otherwise.

        """
        try:
            value = float(text)
        except ValueError:
            return False
        minimum = self.minimum
        if minimum is not None and value < minimum:
            return False
        maximum = self.maximum
        if maximum is not None and value > maximum:
            return False
        if not self.allow_exponent and 'e' in text.lower():
            return False
        return True

    def fixup(self, text):
        """ Fix the user input if fix_input is True

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        Returns
        -------
        result : float
            The value to place into the client widget
        """
        if self.fix_invalid_input:
            try:
                value = float(text)
                if self.minimum is not None and value < self.minimum:
                    text = self.minimum
                elif self.maximum is not None and value > self.maximum:
                    text = self.maximum
            except ValueError:
                # text isn't a float, return the input text
                text = self.minimum
        return str(text)


class RegexValidator(Validator):
    """ A concrete Validator which handles text input.

    This validator ensures that the text matches a provided regular
    expression string.

    """
    #: The regular expression string to use for validation. The default
    #: regex matches everything.
    regex = Str(r'.*')

    def validate(self, text):
        """ Validates the given text matches the regular expression.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        Returns
        -------
        result : bool
            True if the text is valid, False otherwise.

        """
        return bool(re.match(self.regex, text))
