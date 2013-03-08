#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A utility module for dealing with CSS3 font strings.

"""
from collections import namedtuple


#: CSS3 keywords for font style.
_styles = set(['normal', 'italic', 'oblique'])

#: CSS3 keywords for font variants.
_variants = set(['normal', 'small-caps'])

#: CSS3 keywords for font weight.
_weights = set([
    'normal', 'bold', 'bolder', 'lighter', '100', '200', '300', '400',
    '500', '600', '700', '800', '900'
])

#: CSS3 keywords for font sizes.
_sizes = set([
    'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large',
    'larger', 'smaller',
])

#: CSS3 font size unit suffixes.
_units = set(['in', 'cm', 'mm', 'pt', 'pc', 'px'])


#: A namedtuple for storing parsed font information.
Font = namedtuple('Font', 'style variant weight size family')


def parse_font(font):
    """ Parse a CSS shorthand font string into a Font namedtuple.

    Returns
    -------
    result : Font or None
        A namedtuple of font information for the given string, or None
        if the given string is not a valid CSS shorthand font.

    """
    token = []
    tokens = []
    quotechar = None
    for char in font:
        if quotechar is not None:
            if char == quotechar:
                tokens.append(''.join(token))
                token = []
                quotechar = None
            else:
                token.append(char)
        elif char == '"' or char == "'":
            quotechar = char
        elif char in ' \t':
            if token:
                tokens.append(''.join(token))
                token = []
        else:
            token.append(char)

    # Failed to close quoted string.
    if quotechar is not None:
        return

    if token:
        tokens.append(''.join(token))

    sizes = []
    families = []
    optionals = []
    for token in tokens:
        if token in _styles or token in _variants or token in _weights:
            if len(sizes) > 0 or len(families) > 0:
                return None
            optionals.append(token)
        elif token in _sizes or token[-1] == '%' or token[-2:] in _units:
            if len(families) > 0:
                return None
            sizes.append(token)
        else:
            families.append(token)

    if len(optionals) > 3:
        return None
    if len(sizes) != 1:
        return None
    if len(families) != 1:
        return None

    style = None
    variant = None
    weight = None
    size = sizes[0]
    family = families[0]

    for opt in optionals:
        if opt == 'normal':
            continue
        elif opt in _styles:
            if style is not None:
                return None
            style = opt
        elif opt in _variants:
            if variant is not None:
                return None
            variant = opt
        elif opt in _weights:
            if weight is not None:
                return None
            weight = opt
        else:
            return None

    style = style or 'normal'
    variant = variant or 'normal'
    weight = weight or 'normal'

    if size[-1] == '%':
        try:
            float(size[:-1])
        except ValueError:
            return None
    else:
        try:
            float(size[:-2])
        except ValueError:
            return None

    return Font(style, variant, weight, size, family)

