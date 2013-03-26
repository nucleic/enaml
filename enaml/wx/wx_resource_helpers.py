#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from enaml.fontext import FontStyle


FONT_STYLE = {
    FontStyle.Normal: wx.FONTSTYLE_NORMAL,
    FontStyle.Italic: wx.FONTSTYLE_ITALIC,
    FontStyle.Oblique: wx.FONTSTYLE_SLANT,
}


# ASPECT_RATIO_MODE = {
#     'ignore': Qt.IgnoreAspectRatio,
#     'keep': Qt.KeepAspectRatio,
#     'keep_by_expanding': Qt.KeepAspectRatioByExpanding
# }


# TRANSFORM_MODE = {
#     'fast': Qt.FastTransformation,
#     'smooth': Qt.SmoothTransformation
# }


# ICON_MODE = {
#     'normal': QIcon.Normal,
#     'disabled': QIcon.Disabled,
#     'active': QIcon.Active,
#     'selected': QIcon.Selected,
# }


# ICON_STATE = {
#     'off': QIcon.Off,
#     'on': QIcon.On,
# }


# def QImage_from_Image(image):
#     """ Convert an Enaml Image into a QImage.

#     Parameters
#     ----------
#     image : Image
#         The Enaml Image object.

#     Returns
#     -------
#     result : QImage
#         The QImage instance for the given Enaml image.

#     """
#     format = image.format
#     if format == 'auto':
#         format = ''
#     qimage = QImage.fromData(image.data, format)
#     if -1 not in image.size and not qimage.isNull():
#         qsize = QSize(*image.size)
#         if qsize != qimage.size():
#             mode = ASPECT_RATIO_MODE[image.aspect_ratio_mode]
#             transform = TRANSFORM_MODE[image.transform_mode]
#             qimage = qimage.scaled(qsize, mode, transform)
#     return qimage


# def get_cached_qimage(image):
#     """ Get the cached QImage for the Enaml Image.

#     Parameters
#     ----------
#     image : Image
#         The Enaml Image object.

#     Returns
#     -------
#     result : QImage
#         The cached QImage for the image. If no cached image exists, one
#         will be created.

#     """
#     qimage = image._tkdata
#     if not isinstance(qimage, QImage):
#         qimage = image._tkdata = QImage_from_Image(image)
#     return qimage


# def QIcon_from_Icon(icon):
#     """ Convert the given Enaml Icon into a QIcon.

#     Parameters
#     ----------
#     icon : Icon
#         The Enaml Icon object.

#     Returns
#     -------
#     result : QIcon
#         The QIcon instance for the given Enaml icon.

#     """
#     qicon = QIcon()
#     for icon_image in icon.images:
#         image = icon_image.image
#         if not image:
#             continue
#         mode = ICON_MODE[icon_image.mode]
#         state = ICON_STATE[icon_image.state]
#         qimage = get_cached_qimage(image)
#         qpixmap = QPixmap.fromImage(qimage)
#         qicon.addPixmap(qpixmap, mode, state)
#     return qicon


# def get_cached_qicon(icon):
#     """ Get the cached QIcon for the Enaml Icon.

#     Parameters
#     ----------
#     icon : Icon
#         The Enaml Icon object.

#     Returns
#     -------
#     result : QIcon
#         The cached QIcon for the icon. If no cached icon exists, one
#         will be created.

#     """
#     qicon = icon._tkdata
#     if not isinstance(qicon, QIcon):
#         qicon = icon._tkdata = QIcon_from_Icon(icon)
#     return qicon


def wxColor_from_Color(color):
    """ Convert the given Enaml Color into a wxColor.

    Parameters
    ----------
    color : Color
        The Enaml Color object.

    Returns
    -------
    result : wxColor
        The wxColor instance for the given Enaml color.

    """
    return wx.Color(color.red, color.green, color.blue, color.alpha)


def get_cached_wxcolor(color):
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
    wxcolor = color._tkdata
    if not isinstance(wxcolor, wx.Color):
        wxcolor = color._tkdata = wxColor_from_Color(color)
    return wxcolor


def wxFont_from_Font(font):
    """ Convert the given Enaml Font into a wxFont.

    Parameters
    ----------
    font : Font
        The Enaml Font object.

    Returns
    -------
    result : wxFont
        The wxFont instance for the given Enaml font.

    """
    wxstyle = FONT_STYLE[font.style]
    if font.weight < 50:
        wxweight = wx.FONTWEIGHT_LIGHT
    elif font.weight >= 75:
        wxweight = wx.FONTWEIGHT_BOLD
    else:
        wxweight = wx.FONTWEIGHT_NORMAL
    wxfamily = wx.FONTFAMILY_DEFAULT
    wxfont = wx.Font(font.pointsize, wxfamily, wxstyle, wxweight)
    wxfont.SetFaceName(font.family)
    return wxfont


def get_cached_wxfont(font):
    """ Get the cached wxFont for the Enaml Font.

    Parameters
    ----------
    font : Font
        The Enaml Font object.

    Returns
    -------
    result : wxFont
        The cached wxFont for the font. If no cached font exists, one
        will be created.

    """
    wxfont = font._tkdata
    if not isinstance(wxfont, wx.Font):
        wxfont = font._tkdata = wxFont_from_Font(font)
    return wxfont
