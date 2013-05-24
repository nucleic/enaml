#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QBitmap, QImage


def _make_bitmap(data):
    height = len(data)
    width = len(data[0])
    img = QImage(width, height, QImage.Format_MonoLSB)
    for y in xrange(height):
        row = data[y]
        for x in xrange(width):
            idx = 0 if row[x] else 1
            img.setPixel(x, y, idx)
    return QBitmap.fromImage(img)


_close_data = [
    [1, 1, 0, 0, 0, 0, 1, 1],
    [0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 1, 0],
    [1, 1, 0, 0, 0, 0, 1, 1],
]


_close_bmp = None


def close_bitmap():
    global _close_bmp
    if _close_bmp is None:
        _close_bmp = _make_bitmap(_close_data)
    return _close_bmp


_maximize_data = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]


_maximize_bmp = None


def maximize_bitmap():
    global _maximize_bmp
    if _maximize_bmp is None:
        _maximize_bmp = _make_bitmap(_maximize_data)
    return _maximize_bmp


_restore_data = [
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
]


_restore_bmp = None


def restore_bitmap():
    global _restore_bmp
    if _restore_bmp is None:
        _restore_bmp = _make_bitmap(_restore_data)
    return _restore_bmp
