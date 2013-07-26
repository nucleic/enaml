#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import json
import logging
import md5

from enaml.colors import parse_color
from enaml.fonts import parse_font

from .QtGui import QColor, QFont

from .q_resource_helpers import QColor_from_Color, QFont_from_Font


#: The module-level logger
logger = logging.getLogger(__name__)


def _make_color(color_str):
    """ A function which converts a color string into a QColor.

    """
    color = parse_color(color_str)
    if color is not None:
        return QColor_from_Color(color)
    return QColor()


def _make_font(font_str):
    """ A function which converts a font string into a QColor.

    """
    font = parse_font(font_str)
    if font is not None:
        return QFont_from_Font(font)
    return QFont()


#: A static cache of parsed themes. A key in the cache is the md5 hash
#: of the json theme text. The value is the parsed theme. The number of
#: themes will be finite and relatively small. Rather than re-parsing
#: the theme for every file in every editor, they are cached and reused.
_theme_parse_cache = {}


def parse_theme(theme):
    """ Parse a json theme file into a theme dictionary.

    If the given theme has already been parsed once, the cached parsed
    theme will be returned.

    Parameters
    ----------
    theme : str
        A json string defining the theme.

    Returns
    -------
    result : dict
        The parsed them dict. Since this may be a cached value, it
        should be considered read-only.

    """
    md5_sum = md5.new()
    md5_sum.update(theme)
    md5_hash = md5_sum.digest()
    if md5_hash in _theme_parse_cache:
        return _theme_parse_cache[md5_hash]

    try:
        theme_dict = json.loads(theme)
    except Exception as e:
        msg = "error occured while parsing the json theme: '%s'"
        logger.error(msg % e.message)
        print e
        return {}

    colorcache = {}
    fontcache = {}

    def get_color(color_str):
        if color_str in colorcache:
            return colorcache[color_str]
        color = colorcache[color_str] = _make_color(color_str)
        return color

    def get_font(font_str):
        if font_str in fontcache:
            return fontcache[font_str]
        font = fontcache[font_str] = _make_font(font_str)
        return font

    style_conv = [
        ('color', get_color),
        ('paper', get_color),
        ('font',  get_font),
    ]

    settings = theme_dict.get('settings')
    if settings is not None:
        if 'caret' in settings:
            settings['caret'] = get_color(settings['caret'])
        for key, func in style_conv:
            if key in settings:
                settings[key] = func(settings[key])

    for key, token_styles in theme_dict.iteritems():
        if key == 'settings':
            continue
        for style in token_styles.itervalues():
            for key, func in style_conv:
                if key in style:
                    style[key] = func(style[key])

    _theme_parse_cache[md5_hash] = theme_dict

    return theme_dict
