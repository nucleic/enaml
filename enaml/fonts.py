#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A utility module for dealing with CSS3 font strings.

"""
from past.builtins import basestring

from atom.api import Coerced

from .fontext import Font, FontStyle, FontCaps


#: A mapping from CSS font style keyword to style enum
_STYLES = {
    'normal': FontStyle.Normal,
    'italic': FontStyle.Italic,
    'oblique': FontStyle.Oblique,
}


#: A mapping from CSS font variant keyword to caps enum
_VARIANTS = {
    'normal': FontCaps.MixedCase,
    'small-caps':  FontCaps.SmallCaps,
}


#: A mapping from CSS font weight to integer weight. These values are
#: pulled from the Qt stylesheet implementation of font parsing. Enaml
#: does not support the 'bolder' and 'lighter' keywords.
_WEIGHTS = {
    '100': 12,
    '200': 25,
    '300': 37,
    '400': 50,
    '500': 62,
    '600': 75,
    '700': 87,
    '800': 99,
    '900': 99,
    'normal': 50,
    'bold': 75,
}


#: A mapping from CSS font size keywords to font point sizes. These are
#: based on a standard 12 point font size.
_SIZES = {
    'xx-small': 7,
    'x-small': 8,
    'small': 9,
    'medium': 12,
    'large': 14,
    'x-large': 18,
    'xx-large': 24,
}


#: A mapping from CSS font units to functions which convert to points.
_UNITS = {
    'in': lambda size: int(size * 72.0),
    'cm': lambda size: int(size * 72.0 / 2.54),
    'mm': lambda size: int(size * 72.0 / 254.0),
    'pt': lambda size: int(size),
    'pc': lambda size: int(size * 12.0),
    'px': lambda size: int(size * 0.75),
}


def parse_font(font):
    """ Parse a CSS3 shorthand font string into an Enaml Font object.

    Returns
    -------
    result : Font or None
        A font object representing the parsed font. If the string is
        invalid, None will be returned.

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
        if token in _STYLES or token in _VARIANTS or token in _WEIGHTS:
            if len(sizes) > 0 or len(families) > 0:
                return None
            optionals.append(token)
        elif token in _SIZES or token[-2:] in _UNITS:
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

    for opt in optionals:
        if opt == 'normal':
            continue
        elif opt in _STYLES:
            if style is not None:
                return None
            style = opt
        elif opt in _VARIANTS:
            if variant is not None:
                return None
            variant = opt
        elif opt in _WEIGHTS:
            if weight is not None:
                return None
            weight = opt
        else:
            return None

    size = sizes[0]
    if size in _SIZES:
        size = _SIZES[size]
    else:
        sizenum, units = size[:-2], size[-2:]
        try:
            sizenum = float(sizenum)
        except ValueError:
            return None
        size = _UNITS[units](sizenum)

    family = str(families[0])
    weight = _WEIGHTS[weight] if weight else _WEIGHTS['normal']
    style = _STYLES[style] if style else _STYLES['normal']
    variant = _VARIANTS[variant] if variant else _VARIANTS['normal']

    return Font(family, size, weight, style, variant)


def coerce_font(font):
    """ The coercing function for the FontMember.

    """
    if isinstance(font, basestring):
        return parse_font(font)


class FontMember(Coerced):
    """ An Atom member class which coerces a value to a font.

    A font member can be set to a Font, a string, or None. A string
    font will be parsed into a Font object. If the parsing fails,
    the font will be None.  Font strings must be given in CSS grammar,
    e.g. 'bold 12pt arial', which is order dependant.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a FontMember.

        default : Font, string, or None, optional
            The default font to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        Notes
        -----
        When providing a default font value, prefer using a Font object
        directly as this object will be shared among all instances of
        the class. Using a font string will result in a new Font object
        being created for each class instance.

        """
        if factory is None:
            factory = lambda: default
        kind = (Font, type(None))
        sup = super(FontMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_font)
