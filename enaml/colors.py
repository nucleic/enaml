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


#: Regex sub-expressions used for building more complex expression.
_int = r'\s*((?:\+|\-)?[0-9]+)\s*'
_real = r'\s*((?:\+|\-)?[0-9]*(?:\.[0-9]+)?)\s*'
_perc = r'\s*((?:\+|\-)?[0-9]*(?:\.[0-9]+)?)%\s*'

#: Regular expressions used by the parsing routines.
_HEX_RE = re.compile(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', re.UNICODE)
_RGB_NUM_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_int, _int, _int), re.UNICODE)
_RGB_PER_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_perc, _perc, _perc), re.UNICODE)
_RGBA_NUM_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_int, _int, _int, _real), re.UNICODE)
_RGBA_PER_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_perc, _perc, _perc, _real), re.UNICODE)
_HSL_RE = re.compile(r'^hsl\(%s,%s,%s\)$' % (_real, _perc, _perc), re.UNICODE)
_HSLA_RE = re.compile(r'^hsla\(%s,%s,%s,%s\)$' % (_real, _perc, _perc, _real), re.UNICODE)


#: A table of all 147 named SVG colors supported by CSS3. These values
#: will be converted to a floating point rgba color table immediately
#: after the definition.
_SVG_COLORS = {
    'aliceblue': (240, 248, 255),
    'antiquewhite': (250, 235, 215),
    'aqua': (0, 255, 255),
    'aquamarine': (127, 255, 212),
    'azure': (240, 255, 255),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'black': (0, 0, 0),
    'blanchedalmond': (255, 235, 205),
    'blue': (0, 0, 255),
    'blueviolet': (138, 43, 226),
    'brown': (165, 42, 42),
    'burlywood': (222, 184, 135),
    'cadetblue': (95, 158, 160),
    'chartreuse': (127, 255, 0),
    'chocolate': (210, 105, 30),
    'coral': (255, 127, 80),
    'cornflowerblue': (100, 149, 237),
    'cornsilk': (255, 248, 220),
    'crimson': (220, 20, 60),
    'cyan': (0, 255, 255),
    'darkblue': (0, 0, 139),
    'darkcyan': (0, 139, 139),
    'darkgoldenrod': (184, 134, 11),
    'darkgray': (169, 169, 169),
    'darkgreen': (0, 100, 0),
    'darkgrey': (169, 169, 169),
    'darkkhaki': (189, 183, 107),
    'darkmagenta': (139, 0, 139),
    'darkolivegreen': (85, 107, 47),
    'darkorange': (255, 140, 0),
    'darkorchid': (153, 50, 204),
    'darkred': (139, 0, 0),
    'darksalmon': (233, 150, 122),
    'darkseagreen': (143, 188, 143),
    'darkslateblue': (72, 61, 139),
    'darkslategray': (47, 79, 79),
    'darkslategrey': (47, 79, 79),
    'darkturquoise': (0, 206, 209),
    'darkviolet': (148, 0, 211),
    'deeppink': (255, 20, 147),
    'deepskyblue': (0, 191, 255),
    'dimgray': (105, 105, 105),
    'dimgrey': (105, 105, 105),
    'dodgerblue': (30, 144, 255),
    'firebrick': (178, 34, 34),
    'floralwhite': (255, 250, 240),
    'forestgreen': (34, 139, 34),
    'fuchsia': (255, 0, 255),
    'gainsboro': (220, 220, 220),
    'ghostwhite': (248, 248, 255),
    'gold': (255, 215, 0),
    'goldenrod': (218, 165, 32),
    'gray': (128, 128, 128),
    'grey': (128, 128, 128),
    'green': (0, 128, 0),
    'greenyellow': (173, 255, 47),
    'honeydew': (240, 255, 240),
    'hotpink': (255, 105, 180),
    'indianred': (205, 92, 92),
    'indigo': (75, 0, 130),
    'ivory': (255, 255, 240),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'lavenderblush': (255, 240, 245),
    'lawngreen': (124, 252, 0),
    'lemonchiffon': (255, 250, 205),
    'lightblue': (173, 216, 230),
    'lightcoral': (240, 128, 128),
    'lightcyan': (224, 255, 255),
    'lightgoldenrodyellow': (250, 250, 210),
    'lightgray': (211, 211, 211),
    'lightgreen': (144, 238, 144),
    'lightgrey': (211, 211, 211),
    'lightpink': (255, 182, 193),
    'lightsalmon': (255, 160, 122),
    'lightseagreen': (32, 178, 170),
    'lightskyblue': (135, 206, 250),
    'lightslategray': (119, 136, 153),
    'lightslategrey': (119, 136, 153),
    'lightsteelblue': (176, 196, 222),
    'lightyellow': (255, 255, 224),
    'lime': (0, 255, 0),
    'limegreen': (50, 205, 50),
    'linen': (250, 240, 230),
    'magenta': (255, 0, 255),
    'maroon': (128, 0, 0),
    'mediumaquamarine': (102, 205, 170),
    'mediumblue': (0, 0, 205),
    'mediumorchid': (186, 85, 211),
    'mediumpurple': (147, 112, 219),
    'mediumseagreen': (60, 179, 113),
    'mediumslateblue': (123, 104, 238),
    'mediumspringgreen': (0, 250, 154),
    'mediumturquoise': (72, 209, 204),
    'mediumvioletred': (199, 21, 133),
    'midnightblue': (25, 25, 112),
    'mintcream': (245, 255, 250),
    'mistyrose': (255, 228, 225),
    'moccasin': (255, 228, 181),
    'navajowhite': (255, 222, 173),
    'navy': (0, 0, 128),
    'oldlace': (253, 245, 230),
    'olive': (128, 128, 0),
    'olivedrab': (107, 142, 35),
    'orange': (255, 165, 0),
    'orangered': (255, 69, 0),
    'orchid': (218, 112, 214),
    'palegoldenrod': (238, 232, 170),
    'palegreen': (152, 251, 152),
    'paleturquoise': (175, 238, 238),
    'palevioletred': (219, 112, 147),
    'papayawhip': (255, 239, 213),
    'peachpuff': (255, 218, 185),
    'peru': (205, 133, 63),
    'pink': (255, 192, 203),
    'plum': (221, 160, 221),
    'powderblue': (176, 224, 230),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'rosybrown': (188, 143, 143),
    'royalblue': (65, 105, 225),
    'saddlebrown': (139, 69, 19),
    'salmon': (250, 128, 114),
    'sandybrown': (244, 164, 96),
    'seagreen': (46, 139, 87),
    'seashell': (255, 245, 238),
    'sienna': (160, 82, 45),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'slateblue': (106, 90, 205),
    'slategray': (112, 128, 144),
    'slategrey': (112, 128, 144),
    'snow': (255, 250, 250),
    'springgreen': (0, 255, 127),
    'steelblue': (70, 130, 180),
    'tan': (210, 180, 140),
    'teal': (0, 128, 128),
    'thistle': (216, 191, 216),
    'tomato': (255, 99, 71),
    'turquoise': (64, 224, 208),
    'violet': (238, 130, 238),
    'wheat': (245, 222, 179),
    'white': (255, 255, 255),
    'whitesmoke': (245, 245, 245),
    'yellow': (255, 255, 0),
    'yellowgreen': (154, 205, 50),
}


#: Convert the svg color table into a floating point rgba color table.
_COLOR_TABLE = {}
for key, value in _SVG_COLORS.iteritems():
    r, g, b = value
    r /= 255.0
    g /= 255.0
    b /= 255.0
    _COLOR_TABLE[key] = (r, g, b, 1.0)


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
        return (r / 255.0, g / 255.0, b / 255.0, 1.0)


def _parse_rgb_color(color):
    """ Parse a CSS color string which starts with the 'r' character.

    """
    int_ = int
    min_ = min
    max_ = max
    match = _RGB_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0, min_(255, int_(rs))) / 255.0
        g = max_(0, min_(255, int_(gs))) / 255.0
        b = max_(0, min_(255, int_(bs))) / 255.0
        return (r, g, b, 1.0)

    float_ = float
    match = _RGB_PER_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0.0, min_(100.0, float_(rs))) / 100.0
        g = max_(0.0, min_(100.0, float_(gs))) / 100.0
        b = max_(0.0, min_(100.0, float_(bs))) / 100.0
        return (r, g, b, 1.0)

    match = _RGBA_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0, min_(255, int_(rs))) / 255.0
        g = max_(0, min_(255, int_(gs))) / 255.0
        b = max_(0, min_(255, int_(bs))) / 255.0
        a = max_(0.0, min_(1.0, float_(as_)))
        return (r, g, b, a)

    match = _RGBA_PER_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0.0, min_(100.0, float_(rs))) / 100.0
        g = max_(0.0, min_(100.0, float_(gs))) / 100.0
        b = max_(0.0, min_(100.0, float_(bs))) / 100.0
        a = max_(0.0, min_(1.0, float_(as_)))
        return (r, g, b, a)


def _parse_hsl_color(color):
    """ Parse a CSS color string that starts with the 'h' character.

    """
    float_ = float
    min_ = min
    max_ = max
    match = _HSL_RE.match(color)
    if match is not None:
        hs, ss, ls = match.groups()
        h = ((float_(hs) % 360.0 + 360.0) % 360.0) / 360.0
        s = max_(0.0, min_(100.0, float_(ss))) / 100.0
        l = max_(0.0, min_(100.0, float_(ls))) / 100.0
        r, g, b = hls_to_rgb(h, l, s)
        return (r, g, b, 1.0)

    match = _HSLA_RE.match(color)
    if match is not None:
        hs, ss, ls, as_ = match.groups()
        h = ((float_(hs) % 360.0 + 360.0) % 360.0) / 360.0
        s = max_(0.0, min_(100.0, float_(ss))) / 100.0
        l = max_(0.0, min_(100.0, float_(ls))) / 100.0
        a = max_(0.0, min_(1.0, float_(as_)))
        r, g, b = hls_to_rgb(h, l, s)
        return (r, g, b, a)


#: A dispatch table of color parser functions.
_COLOR_PARSERS = {
    '#': _parse_hex_color,
    'r': _parse_rgb_color,
    'h': _parse_hsl_color,
}


def parse_color(color):
    """ Parse a color string into a tuple of RGBA values.

    Parameters
    ----------
    color : string
        A CSS3 string representation of the color.

    Returns
    -------
    result : tuple or None
        A tuple of RGBA values. All values are floats in the range
        0.0 - 1.0. If the string is invalid, None will be returned.

    """
    if color in _COLOR_TABLE:
        return _COLOR_TABLE[color]
    color = color.strip()
    if color:
        key = color[0]
        if key in _COLOR_PARSERS:
            return _COLOR_PARSERS[key](color)


def composite_colors(first, second):
    """ Composite two colors together using their given alpha.

    The first color will be composited on top of the second color.

    Parameters
    ----------
    first : tuple
        The rgba tuple of the first color. All values are floats in
        the range 0.0 - 1.0.

    second : tuple
        The rgba tuple of the second color. The format of this tuple
        is the same as the first color.

    Returns
    -------
    result : tuple
        The composited rgba color tuple.

    """
    r1, g1, b1, a1 = first
    r2, g2, b2, a2 = second
    y = a2 * (1.0 - a1)
    ro = r1 * a1 + r2 * y
    go = g1 * a1 + g2 * y
    bo = b1 * a1 + b2 * y
    ao = a1 + y
    return (ro, go, bo, ao)

