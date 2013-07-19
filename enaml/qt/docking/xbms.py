#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Int, Str

from enaml.qt.QtCore import QSize
from enaml.qt.QtGui import QBitmap, QImage


class XBM(Atom):
    """ A simple class representing an XMB image.

    """
    #: The width of the xbm image.
    width = Int()

    #: The height of the xbm image.
    height = Int()

    #: The bytestring of image data.
    data = Str()

    def __init__(self, width, height, data):
        """ Initialize an XBM image.

        Parameters
        ----------
        width : int
            The width of the bitmap.

        height : int
            The height of the bitmap.

        data : list
            A list of 1s and 0s which represent the bitmap data.
            The length must be equal to width * height.

        """
        assert len(data) == (width * height)
        bytes = []
        for row in xrange(height):
            val = 0
            offset = row * width
            for col in xrange(width):
                d = col % 8
                if col > 0 and d == 0:
                    bytes.append(chr(val))
                    val = 0
                v = data[offset + col]
                val |= v << (7 - d)
            bytes.append(chr(val))
        self.width = width
        self.height = height
        self.data = ''.join(bytes)

    def toBitmap(self):
        size = QSize(self.width, self.height)
        return QBitmap.fromData(size, self.data, QImage.Format_Mono)


CLOSE_BUTTON = XBM(8, 7, [
    1, 1, 0, 0, 0, 0, 1, 1,
    0, 1, 1, 0, 0, 1, 1, 0,
    0, 0, 1, 1, 1, 1, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 1, 1, 1, 1, 0, 0,
    0, 1, 1, 0, 0, 1, 1, 0,
    1, 1, 0, 0, 0, 0, 1, 1,
])


MAXIMIZE_BUTTON = XBM(8, 7, [
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
])


RESTORE_BUTTON = XBM(10, 9, [
    0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
])


LINKED_BUTTON = XBM(10, 9, [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 0, 0, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 0, 0, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
])


UNLINKED_BUTTON = XBM(10, 9, [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 0, 0, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 0, 0, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
])


PIN_BUTTON = XBM(9, 9, [
    0, 0, 1, 1, 1, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 1, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0,
    0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 0, 0, 0,
])


UNPIN_BUTTON = XBM(9, 9, [
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 1, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 0, 0, 0, 0, 1,
    0, 0, 0, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 1, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
])
