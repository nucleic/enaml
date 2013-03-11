#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QColor

from enaml.colors import parse_color


def q_parse_color(color):
    """ Convert a color string into a QColor.

    Parameters
    ----------
    color : string
        A CSS3 color string to convert to a QColor.

    Returns
    -------
    result : QColor
        The QColor for the given color string

    """
    rgba = parse_color(color)
    if rgba is None:
        qcolor = QColor()
    else:
        r, g, b, a = rgba
        qcolor = QColor.fromRgbF(r, g, b, a)
    return qcolor
