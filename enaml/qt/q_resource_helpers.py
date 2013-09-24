#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import Qt, QSize
from .QtGui import QColor, QFont, QImage, QIcon, QPixmap


from enaml.fontext import FontStyle, FontCaps


# Mapping from enaml font styles to Qt font styles.
_qfont_style_mapping = {
    FontStyle.Normal: QFont.Style.StyleNormal,
    FontStyle.Italic: QFont.Style.StyleItalic,
    FontStyle.Oblique: QFont.Style.StyleOblique,
}


# Mapping from enaml capitalization modes to Qt capitalization modes.
_qfont_capitalization_mapping = {
    FontCaps.MixedCase: QFont.Capitalization.MixedCase,
    FontCaps.AllUppercase: QFont.Capitalization.AllUppercase,
    FontCaps.AllLowercase: QFont.Capitalization.AllLowercase,
    FontCaps.SmallCaps: QFont.Capitalization.SmallCaps,
    FontCaps.Capitalize: QFont.Capitalization.Capitalize,
}


ASPECT_RATIO_MODE = {
    'ignore': Qt.IgnoreAspectRatio,
    'keep': Qt.KeepAspectRatio,
    'keep_by_expanding': Qt.KeepAspectRatioByExpanding
}


TRANSFORM_MODE = {
    'fast': Qt.FastTransformation,
    'smooth': Qt.SmoothTransformation
}


ICON_MODE = {
    'normal': QIcon.Normal,
    'disabled': QIcon.Disabled,
    'active': QIcon.Active,
    'selected': QIcon.Selected,
}


ICON_STATE = {
    'off': QIcon.Off,
    'on': QIcon.On,
}


def QImage_from_Image(image):
    """ Convert an Enaml Image into a QImage.

    Parameters
    ----------
    image : Image
        The Enaml Image object.

    Returns
    -------
    result : QImage
        The QImage instance for the given Enaml image.

    """
    format = image.format
    if format == 'auto':
        format = ''
    qimage = QImage.fromData(image.data, format)
    if -1 not in image.size and not qimage.isNull():
        qsize = QSize(*image.size)
        if qsize != qimage.size():
            mode = ASPECT_RATIO_MODE[image.aspect_ratio_mode]
            transform = TRANSFORM_MODE[image.transform_mode]
            qimage = qimage.scaled(qsize, mode, transform)
    return qimage


def get_cached_qimage(image):
    """ Get the cached QImage for the Enaml Image.

    Parameters
    ----------
    image : Image
        The Enaml Image object.

    Returns
    -------
    result : QImage
        The cached QImage for the image. If no cached image exists, one
        will be created.

    """
    qimage = image._tkdata
    if not isinstance(qimage, QImage):
        qimage = image._tkdata = QImage_from_Image(image)
    return qimage


def QIcon_from_Icon(icon):
    """ Convert the given Enaml Icon into a QIcon.

    Parameters
    ----------
    icon : Icon
        The Enaml Icon object.

    Returns
    -------
    result : QIcon
        The QIcon instance for the given Enaml icon.

    """
    qicon = QIcon()
    for icon_image in icon.images:
        image = icon_image.image
        if not image:
            continue
        mode = ICON_MODE[icon_image.mode]
        state = ICON_STATE[icon_image.state]
        qimage = get_cached_qimage(image)
        qpixmap = QPixmap.fromImage(qimage)
        qicon.addPixmap(qpixmap, mode, state)
    return qicon


def get_cached_qicon(icon):
    """ Get the cached QIcon for the Enaml Icon.

    Parameters
    ----------
    icon : Icon
        The Enaml Icon object.

    Returns
    -------
    result : QIcon
        The cached QIcon for the icon. If no cached icon exists, one
        will be created.

    """
    qicon = icon._tkdata
    if not isinstance(qicon, QIcon):
        qicon = icon._tkdata = QIcon_from_Icon(icon)
    return qicon


def QColor_from_Color(color):
    """ Convert the given Enaml Color into a QColor.

    Parameters
    ----------
    color : Color
        The Enaml Color object.

    Returns
    -------
    result : QColor
        The QColor instance for the given Enaml color.

    """
    return QColor.fromRgba(color.argb)


def get_cached_qcolor(color):
    """ Get the cached QColor for the Enaml Color.

    Parameters
    ----------
    color : Color
        The Enaml Color object.

    Returns
    -------
    result : QColor
        The cached QColor for the color. If no cached color exists, one
        will be created.

    """
    qcolor = color._tkdata
    if not isinstance(qcolor, QColor):
        qcolor = color._tkdata = QColor_from_Color(color)
    return qcolor


def QFont_from_Font(font):
    """ Convert the given Enaml Font into a QFont.

    Parameters
    ----------
    font : Font
        The Enaml Font object.

    Returns
    -------
    result : QFont
        The QFont instance for the given Enaml font.

    """
    qfont = QFont(font.family, font.pointsize, font.weight)
    qfont.setStyle(_qfont_style_mapping[font.style])
    qfont.setCapitalization(_qfont_capitalization_mapping[font.caps])
    return qfont


def get_cached_qfont(font):
    """ Get the cached QFont for the Enaml Font.

    Parameters
    ----------
    font : Font
        The Enaml Font object.

    Returns
    -------
    result : QFont
        The cached QFont for the font. If no cached font exists, one
        will be created.

    """
    qfont = font._tkdata
    if not isinstance(qfont, QFont):
        qfont = font._tkdata = QFont_from_Font(font)
    return qfont
