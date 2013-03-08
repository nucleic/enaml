#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.fonts import parse_font

from .qt.QtGui import QFont, QApplication


STYLE = {
    'normal': QFont.StyleNormal,
    'italic': QFont.StyleItalic,
    'oblique': QFont.StyleOblique,
}


VARIANT = {
    'normal': QFont.MixedCase,
    'small-caps': QFont.SmallCaps,
}


WEIGHT = {
    'normal': QFont.Normal,
    'bold': QFont.Bold,
    '100': 12,
    '200': 25,
    '300': 37,
    '400': 50,
    '500': 62,
    '600': 75,
    '700': 87,
    '800': 99,
    '900': 99,
}


RELATIVE_WEIGHT = {
    'bolder': {
        100: 50,
        200: 50,
        300: 50,
        400: 75,
        500: 75,
        600: 87,
        700: 99,
        800: 99,
        900: 99,
    },
    'lighter': {
        100: 12,
        200: 12,
        300: 25,
        400: 25,
        500: 50,
        600: 50,
        700: 75,
        800: 87,
        900: 87,
    }
}


SIZES = {
    'xx-small': 0,
    'x-small': 1,
    'small': 2,
    'medium': 3,
    'large': 4,
    'x-large': 5,
    'xx-large': 6,
}


RELATIVE_SIZES = {
    'larger': 4,
    'smaller': 2,
}


SCALE_FACTORS = [0.6, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0]


# Convert CSS units into points.
UNIT_CONVERTERS = {
    'in': lambda size: size * 72.0,
    'cm': lambda size: size * 72.0 / 2.54,
    'mm': lambda size: size * 72.0 / 254.0,
    'pt': lambda size: size,
    'pc': lambda size: size * 12.0,
    'px': lambda size: size * 0.75,
}


class QtFontCache(object):

    def __init__(self, default=None):
        """ Initialize a QFontCache.

        Parameters
        ----------
        default: QFont, optional
            The font to use to fill the default parameters of fonts.

        """
        self._default = default
        self._cache = {}  # XXX need an lru cache here.

    def __getitem__(self, font):
        cache = self._cache
        if font in cache:
            return cache[font]
        if isinstance(font, basestring):
            font_ = parse_font(font)
            if font_ is None:
                return self._default or QFont()
            qfont = self._make_qfont(font_)
            cache[font] = cache[font_] = qfont
        else:
            qfont = self._make_qfont(font)
            cache[font] = qfont
        return qfont

    def _make_qfont(self, font):
        """ Create a QFont from an Enaml Font object.

        Parameters
        ----------
        font : Font
            The Enaml Font object.

        Returns
        -------
        result : QFont
            An equivalent QFont for the given Enaml Font.

        """
        app = QApplication.instance()
        if app is not None:
            app_default = app.font()
        else:
            app_default = QFont()

        default = self._default
        if default is None:
            default = app_default

        qfont = QFont()
        qfont.setStyle(STYLE[font.style])
        qfont.setCapitalization(VARIANT[font.variant])
        if font.family:
            qfont.setFamily(font.family)

        fweight = font.weight
        if fweight in WEIGHT:
            qfont.setWeight(WEIGHT[fweight])
        elif fweight in RELATIVE_WEIGHT:
            mapping = RELATIVE_WEIGHT[fweight]
            sweight = int(round(default.weight() * 8 / 100.0) * 100)
            qfont.setWeight(mapping[sweight])

        fsize = font.size
        if fsize in SIZES:
            scale_idx = SIZES[fsize]
            size = app_default.pointSizeF() * SCALE_FACTORS[scale_idx]
            qfont.setPointSizeF(size)
        elif fsize in RELATIVE_SIZES:
            scale = SCALE_FACTORS[RELATIVE_SIZES[fsize]]
            if default.pointSize() < 0:
                size = default.pixelSize() * scale
                qfont.setPixelSize(int(size))
            else:
                size = default.pointSizeF() * scale
                qfont.setPointSizeF(size)
        elif fsize[-1] == '%':
            scale = float(fsize[:-1]) / 100.0
            if default.pointSize() < 0:
                size = default.pixelSize() * scale
                qfont.setPixelSize(int(size))
            else:
                size = default.pointSizeF() * scale
                qfont.setPointSizeF(size)
        else:
            size = float(fsize[:-2])
            converter = UNIT_CONVERTERS[fsize[-2:]]
            qfont.setPointSizeF(converter(size))

        return qfont.resolve(default)


QtGlobalFontCache = QtFontCache()

