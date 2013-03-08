#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Python implementations of basic client-side validators.

This module provides basic implementations of client-side validators for
Enaml clients implemented in Python. Enaml client-side implementations in
other languages (eg. javascript) or in tookits which provide their own
validation system should whichever is more appropriate.

"""
import re


def null_validator(text):
    """ A validator function which will return True for all text input.

    Parameters
    ----------
    text : string
        The text to validate.

    """
    return True


def regex_validator(regex):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    regex : unicode
        A regular expression string to use for matching.

    Returns
    -------
    results : callable
        A callable which takes a single unicode argument and returns
        True if the text matches the regex, False otherwise.

    """
    rgx = re.compile(regex, re.UNICODE)
    def validator(text):
        return bool(rgx.match(text))
    return validator


def int_validator(base=10, minimum=None, maximum=None):
    """ Creates a callable which will validate text input against the
    provided integer range.

    Parameters
    ----------
    base : 2, 8, 10, or 16
        The number base to use with the range. Supported bases are
        2, 8, 10, and 16.

    minimum : None or int
        The base 10 lower bound of allowable values, inlcusive. None
        indicates no lower bound.

    maximum : None or int
        The base 10 upper bound of allowable values, inlcusive. None
        indicates no upper bound.

    Returns
    -------
    results : callable
        A callable which takes a single unicode argument and returns
        True if the text matches the range, False otherwise.

    """
    def validator(text):
        try:
            value = int(text, base)
        except ValueError:
            return False
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        return True
    return validator


def float_validator(minimum=None, maximum=None, allow_exponent=False):
    """ Creates a callable which will validate text input against the
    provided float range.

    Parameters
    ----------
    minimum : None or float
        The lower bound of allowable values, inlcusive. None indicates
        no lower bound.

    maximum : None or float
        The upper bound of allowable values, inlcusive. None indicates
        no upper bound.

    allow_exponent : bool
        Whether or not to allow exponents like '1e6' in the input.

    Returns
    -------
    results : callable
        A callable which takes a single unicode argument and returns
        True if the text matches the range, False otherwise.

    """
    def validator(text):
        try:
            value = float(text)
        except ValueError:
            return False
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        if not allow_exponent and 'e' in text.lower():
            return False
        return True
    return validator


_VALIDATOR_TYPES = {
    'regex': regex_validator,
    'int': int_validator,
    'float': float_validator,
}


def make_validator(info):
    """ Make a validator function for the given dict represenation.

    Parameters
    ----------
    info : dict
        The dictionary representation of a client side validator sent
        by the Enaml server widget.

    Returns
    -------
    result : callable
        A callable which takes a single unicode argument and returns
        True if the text is valid. False otherwise. If the validator
        type is not supported, a null validator which accepts all text
        will be returned.

    """
    vtype = info['type']
    if vtype in _VALIDATOR_TYPES:
        return _VALIDATOR_TYPES[vtype](**info['arguments'])
    else:
        return null_validator

