#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A utility module for dealing with CSS3 color strings.

"""
from colorsys import hls_to_rgb
import re
from past.builtins import basestring

from atom.api import Coerced

from .colorext import Color


#: Regex sub-expressions used for building more complex expression.
_int = r'\s*((?:\+|\-)?[0-9]+)\s*'
_real = r'\s*((?:\+|\-)?[0-9]*(?:\.[0-9]+)?)\s*'
_perc = r'\s*((?:\+|\-)?[0-9]*(?:\.[0-9]+)?)%\s*'

#: Regular expressions used by the parsing routines.
_HEX_RE = re.compile(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', re.UNICODE)
_HEXA_RE = re.compile(r'^#([A-Fa-f0-9]{4}|[A-Fa-f0-9]{8})$', re.UNICODE)
_RGB_NUM_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_int, _int, _int), re.UNICODE)
_RGB_PER_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_perc, _perc, _perc), re.UNICODE)
_RGBA_NUM_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_int, _int, _int, _real), re.UNICODE)
_RGBA_PER_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_perc, _perc, _perc, _real), re.UNICODE)
_HSL_RE = re.compile(r'^hsl\(%s,%s,%s\)$' % (_real, _perc, _perc), re.UNICODE)
_HSLA_RE = re.compile(r'^hsla\(%s,%s,%s,%s\)$' % (_real, _perc, _perc, _real), re.UNICODE)


#: A table of all 147 named SVG colors supported by CSS3.
SVG_COLORS = {
    'aliceblue': Color(240, 248, 255),
    'antiquewhite': Color(250, 235, 215),
    'aqua': Color(0, 255, 255),
    'aquamarine': Color(127, 255, 212),
    'azure': Color(240, 255, 255),
    'beige': Color(245, 245, 220),
    'bisque': Color(255, 228, 196),
    'black': Color(0, 0, 0),
    'blanchedalmond': Color(255, 235, 205),
    'blue': Color(0, 0, 255),
    'blueviolet': Color(138, 43, 226),
    'brown': Color(165, 42, 42),
    'burlywood': Color(222, 184, 135),
    'cadetblue': Color(95, 158, 160),
    'chartreuse': Color(127, 255, 0),
    'chocolate': Color(210, 105, 30),
    'coral': Color(255, 127, 80),
    'cornflowerblue': Color(100, 149, 237),
    'cornsilk': Color(255, 248, 220),
    'crimson': Color(220, 20, 60),
    'cyan': Color(0, 255, 255),
    'darkblue': Color(0, 0, 139),
    'darkcyan': Color(0, 139, 139),
    'darkgoldenrod': Color(184, 134, 11),
    'darkgray': Color(169, 169, 169),
    'darkgreen': Color(0, 100, 0),
    'darkgrey': Color(169, 169, 169),
    'darkkhaki': Color(189, 183, 107),
    'darkmagenta': Color(139, 0, 139),
    'darkolivegreen': Color(85, 107, 47),
    'darkorange': Color(255, 140, 0),
    'darkorchid': Color(153, 50, 204),
    'darkred': Color(139, 0, 0),
    'darksalmon': Color(233, 150, 122),
    'darkseagreen': Color(143, 188, 143),
    'darkslateblue': Color(72, 61, 139),
    'darkslategray': Color(47, 79, 79),
    'darkslategrey': Color(47, 79, 79),
    'darkturquoise': Color(0, 206, 209),
    'darkviolet': Color(148, 0, 211),
    'deeppink': Color(255, 20, 147),
    'deepskyblue': Color(0, 191, 255),
    'dimgray': Color(105, 105, 105),
    'dimgrey': Color(105, 105, 105),
    'dodgerblue': Color(30, 144, 255),
    'firebrick': Color(178, 34, 34),
    'floralwhite': Color(255, 250, 240),
    'forestgreen': Color(34, 139, 34),
    'fuchsia': Color(255, 0, 255),
    'gainsboro': Color(220, 220, 220),
    'ghostwhite': Color(248, 248, 255),
    'gold': Color(255, 215, 0),
    'goldenrod': Color(218, 165, 32),
    'gray': Color(128, 128, 128),
    'grey': Color(128, 128, 128),
    'green': Color(0, 128, 0),
    'greenyellow': Color(173, 255, 47),
    'honeydew': Color(240, 255, 240),
    'hotpink': Color(255, 105, 180),
    'indianred': Color(205, 92, 92),
    'indigo': Color(75, 0, 130),
    'ivory': Color(255, 255, 240),
    'khaki': Color(240, 230, 140),
    'lavender': Color(230, 230, 250),
    'lavenderblush': Color(255, 240, 245),
    'lawngreen': Color(124, 252, 0),
    'lemonchiffon': Color(255, 250, 205),
    'lightblue': Color(173, 216, 230),
    'lightcoral': Color(240, 128, 128),
    'lightcyan': Color(224, 255, 255),
    'lightgoldenrodyellow': Color(250, 250, 210),
    'lightgray': Color(211, 211, 211),
    'lightgreen': Color(144, 238, 144),
    'lightgrey': Color(211, 211, 211),
    'lightpink': Color(255, 182, 193),
    'lightsalmon': Color(255, 160, 122),
    'lightseagreen': Color(32, 178, 170),
    'lightskyblue': Color(135, 206, 250),
    'lightslategray': Color(119, 136, 153),
    'lightslategrey': Color(119, 136, 153),
    'lightsteelblue': Color(176, 196, 222),
    'lightyellow': Color(255, 255, 224),
    'lime': Color(0, 255, 0),
    'limegreen': Color(50, 205, 50),
    'linen': Color(250, 240, 230),
    'magenta': Color(255, 0, 255),
    'maroon': Color(128, 0, 0),
    'mediumaquamarine': Color(102, 205, 170),
    'mediumblue': Color(0, 0, 205),
    'mediumorchid': Color(186, 85, 211),
    'mediumpurple': Color(147, 112, 219),
    'mediumseagreen': Color(60, 179, 113),
    'mediumslateblue': Color(123, 104, 238),
    'mediumspringgreen': Color(0, 250, 154),
    'mediumturquoise': Color(72, 209, 204),
    'mediumvioletred': Color(199, 21, 133),
    'midnightblue': Color(25, 25, 112),
    'mintcream': Color(245, 255, 250),
    'mistyrose': Color(255, 228, 225),
    'moccasin': Color(255, 228, 181),
    'navajowhite': Color(255, 222, 173),
    'navy': Color(0, 0, 128),
    'oldlace': Color(253, 245, 230),
    'olive': Color(128, 128, 0),
    'olivedrab': Color(107, 142, 35),
    'orange': Color(255, 165, 0),
    'orangered': Color(255, 69, 0),
    'orchid': Color(218, 112, 214),
    'palegoldenrod': Color(238, 232, 170),
    'palegreen': Color(152, 251, 152),
    'paleturquoise': Color(175, 238, 238),
    'palevioletred': Color(219, 112, 147),
    'papayawhip': Color(255, 239, 213),
    'peachpuff': Color(255, 218, 185),
    'peru': Color(205, 133, 63),
    'pink': Color(255, 192, 203),
    'plum': Color(221, 160, 221),
    'powderblue': Color(176, 224, 230),
    'purple': Color(128, 0, 128),
    'red': Color(255, 0, 0),
    'rosybrown': Color(188, 143, 143),
    'royalblue': Color(65, 105, 225),
    'saddlebrown': Color(139, 69, 19),
    'salmon': Color(250, 128, 114),
    'sandybrown': Color(244, 164, 96),
    'seagreen': Color(46, 139, 87),
    'seashell': Color(255, 245, 238),
    'sienna': Color(160, 82, 45),
    'silver': Color(192, 192, 192),
    'skyblue': Color(135, 206, 235),
    'slateblue': Color(106, 90, 205),
    'slategray': Color(112, 128, 144),
    'slategrey': Color(112, 128, 144),
    'snow': Color(255, 250, 250),
    'springgreen': Color(0, 255, 127),
    'steelblue': Color(70, 130, 180),
    'tan': Color(210, 180, 140),
    'teal': Color(0, 128, 128),
    'thistle': Color(216, 191, 216),
    'tomato': Color(255, 99, 71),
    'turquoise': Color(64, 224, 208),
    'violet': Color(238, 130, 238),
    'wheat': Color(245, 222, 179),
    'white': Color(255, 255, 255),
    'whitesmoke': Color(245, 245, 245),
    'yellow': Color(255, 255, 0),
    'yellowgreen': Color(154, 205, 50),
}


def _parse_hex_color(color):
    """ Parse a CSS color string which starts with the '#' character.

    """
    int_ = int
    match = _HEX_RE.match(color)
    if match is not None:
        hex_str = match.group(1)
        if len(hex_str) == 3:
            r = int_(hex_str[0], 16)
            r |= (r << 4)
            g = int_(hex_str[1], 16)
            g |= (g << 4)
            b = int_(hex_str[2], 16)
            b |= (b << 4)
        else:
            r = int_(hex_str[:2], 16)
            g = int_(hex_str[2:4], 16)
            b = int_(hex_str[4:6], 16)
        return Color(r, g, b, 255)
    match = _HEXA_RE.match(color)
    if match is not None:
        hex_str = match.group(1)
        if len(hex_str) == 4:
            r = int_(hex_str[0], 16)
            r |= (r << 4)
            g = int_(hex_str[1], 16)
            g |= (g << 4)
            b = int_(hex_str[2], 16)
            b |= (b << 4)
            a = int_(hex_str[3], 16)
            a |= (a << 4)
        else:
            r = int_(hex_str[:2], 16)
            g = int_(hex_str[2:4], 16)
            b = int_(hex_str[4:6], 16)
            a = int_(hex_str[6:8], 16)
        return Color(r, g, b, a)


def _parse_rgb_color(color):
    """ Parse a CSS color string which starts with the 'r' character.

    """
    int_ = int
    min_ = min
    max_ = max
    match = _RGB_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0, min_(255, int_(rs)))
        g = max_(0, min_(255, int_(gs)))
        b = max_(0, min_(255, int_(bs)))
        return Color(r, g, b, 255)

    float_ = float
    match = _RGB_PER_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0.0, min_(100.0, float_(rs))) / 100.0
        g = max_(0.0, min_(100.0, float_(gs))) / 100.0
        b = max_(0.0, min_(100.0, float_(bs))) / 100.0
        r = int_(255 * r)
        g = int_(255 * g)
        b = int_(255 * b)
        return Color(r, g, b, 255)

    match = _RGBA_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0, min_(255, int_(rs)))
        g = max_(0, min_(255, int_(gs)))
        b = max_(0, min_(255, int_(bs)))
        a = max_(0.0, min_(1.0, float_(as_)))
        a = int_(255 * a)
        return Color(r, g, b, a)

    match = _RGBA_PER_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0.0, min_(100.0, float_(rs))) / 100.0
        g = max_(0.0, min_(100.0, float_(gs))) / 100.0
        b = max_(0.0, min_(100.0, float_(bs))) / 100.0
        a = max_(0.0, min_(1.0, float_(as_)))
        r = int_(255 * r)
        g = int_(255 * g)
        b = int_(255 * b)
        a = int_(255 * a)
        return Color(r, g, b, a)


def _parse_hsl_color(color):
    """ Parse a CSS color string that starts with the 'h' character.

    """
    float_ = float
    int_ = int
    min_ = min
    max_ = max
    match = _HSL_RE.match(color)
    if match is not None:
        hs, ss, ls = match.groups()
        h = ((float_(hs) % 360.0 + 360.0) % 360.0) / 360.0
        s = max_(0.0, min_(100.0, float_(ss))) / 100.0
        l = max_(0.0, min_(100.0, float_(ls))) / 100.0
        r, g, b = hls_to_rgb(h, l, s)
        r = int_(255 * r)
        g = int_(255 * g)
        b = int_(255 * b)
        return Color(r, g, b, 255)

    match = _HSLA_RE.match(color)
    if match is not None:
        hs, ss, ls, as_ = match.groups()
        h = ((float_(hs) % 360.0 + 360.0) % 360.0) / 360.0
        s = max_(0.0, min_(100.0, float_(ss))) / 100.0
        l = max_(0.0, min_(100.0, float_(ls))) / 100.0
        a = max_(0.0, min_(1.0, float_(as_)))
        r, g, b = hls_to_rgb(h, l, s)
        r = int_(255 * r)
        g = int_(255 * g)
        b = int_(255 * b)
        a = int_(255 * a)
        return Color(r, g, b, a)


#: A dispatch table of color parser functions.
_COLOR_PARSERS = {
    '#': _parse_hex_color,
    'r': _parse_rgb_color,
    'h': _parse_hsl_color,
}


def parse_color(color):
    """ Parse a CSS3 color string into a tuple of RGBA values.

    Parameters
    ----------
    color : string
        A CSS3 string representation of the color.

    Returns
    -------
    result : Color or None
        A color object representing the parsed color. If the string
        is invalid, None will be returned.

    """
    if color in SVG_COLORS:
        return SVG_COLORS[color]
    color = color.strip()
    if color:
        key = color[0]
        if key in _COLOR_PARSERS:
            return _COLOR_PARSERS[key](color)


def coerce_color(color):
    """ The coercing function for the ColorMember.

    """
    if isinstance(color, basestring):
        return parse_color(color)


class ColorMember(Coerced):
    """ An Atom member class which coerces a value to a color.

    A color member can be set to a Color, a string, or None. A string
    color will be parsed into a Color object. If the parsing fails,
    the color will be None.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        """ Initialize a ColorMember.

        default : Color, string, or None, optional
            The default color to use for the member.

        factory : callable, optional
            An optional callable which takes no arguments and returns
            the default value for the member. If this is provided, it
            will override any value passed as 'default'.

        Notes
        -----
        When providing a default color value, prefer using a Color
        object or a named color string as these color objects will be
        shared among all instances of the class. Using a color string
        which must be parsed will result in a new Color object being
        created for each class instance.

        """
        if factory is None:
            factory = lambda: default
        kind = (Color, type(None))
        sup = super(ColorMember, self)
        sup.__init__(kind, factory=factory, coercer=coerce_color)
