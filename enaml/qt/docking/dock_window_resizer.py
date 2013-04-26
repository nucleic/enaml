#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint


class DockWindowResizer(object):
    """ A class to assist resizing top-level dock windows.

    """
    #: Do not resize the window.
    NoResize = 0

    #: Resize the window vertically from the north edge.
    North = 1

    #: Resize the window horizontally from the east edge.
    East = 2

    #: Resize the window vertically from the south edge.
    South = 3

    #: Resize the window horizontally from the west edge.
    West = 4

    #: Resize the window diagonally from the northeast edge.
    NorthEast = 5

    #: Resize the window diagonally from the northwest edge.
    NorthWest = 6

    #: Resize the window diagonally from the southeast edge.
    SouthEast = 7

    #: Resize the window diagonally from the southwest edge.
    SouthWest = 8

    #: The cursors to use for a given resize mode.
    Cursors = {
        North: Qt.SizeVerCursor,
        South: Qt.SizeVerCursor,
        East: Qt.SizeHorCursor,
        West: Qt.SizeHorCursor,
        NorthEast: Qt.SizeBDiagCursor,
        SouthWest: Qt.SizeBDiagCursor,
        NorthWest: Qt.SizeFDiagCursor,
        SouthEast: Qt.SizeFDiagCursor,
    }

    @classmethod
    def cursor(cls, mode):
        """ Get the cursor style to show for a given mode.

        Parameters
        ----------
        mode : int
            One of the resize mode enum values.

        Returns
        -------
        result : Qt.CursorShape or None
            The cursor shape to use for the mode, or None if the
            cursor should be unset.

        """
        return cls.Cursors.get(mode)

    @classmethod
    def hit_test(cls, window, pos, margins, extra):
        """ Hit test a window for the resize mode.

        Hit testing is confined to the contents margins of the window.

        Parameters
        ----------
        window : QWidget
            The top-level dock window to test for resize area.

        pos : QPoint
            The point of interest, expressed in local coordinates.

        margins : QMargins
            The margins which represent the resize hot-spots areas
            around the border of the window.

        extra : int
            Extra space to add to the hit test for corners. The
            default is 0.

        Returns
        -------
        result : tuple
            A 2-tuple of (int, QPoint) representing the resize mode
            and offset for the mode.

        """
        x = pos.x()
        y = pos.y()
        width = window.width()
        height = window.height()
        if x < margins.left():
            if y < margins.top() + extra:
                mode = cls.NorthWest
                offset = QPoint(x, y)
            elif y > height - (margins.bottom() + extra):
                mode = cls.SouthWest
                offset = QPoint(x, height - y)
            else:
                mode = cls.West
                offset = QPoint(x, 0)
        elif y < margins.top():
            if x < margins.left() + extra:
                mode = cls.NorthWest
                offset = QPoint(x, y)
            elif x > width - (margins.right() + extra):
                mode = cls.NorthEast
                offset = QPoint(width - x, y)
            else:
                mode = cls.North
                offset = QPoint(0, y)
        elif x > width - margins.right():
            if y < margins.top() + extra:
                mode = cls.NorthEast
                offset = QPoint(width - x, y)
            elif y > height - (margins.bottom() + extra):
                mode = cls.SouthEast
                offset = QPoint(width - x, height - y)
            else:
                mode = cls.East
                offset = QPoint(width - x, 0)
        elif y > height - margins.bottom():
            if x < margins.left() + extra:
                mode = cls.SouthWest
                offset = QPoint(x, height - y)
            elif x > width - (margins.right() + extra):
                mode = cls.SouthEast
                offset = QPoint(width - x, height - y)
            else:
                mode = cls.South
                offset = QPoint(0, height - y)
        else:
            mode = cls.NoResize
            offset = QPoint()
        return mode, offset

    @staticmethod
    def resize(window, pos, mode, offset):
        """ Reset the window for the given state.

        Parameters
        ----------
        window : QWidget
            The top-level dock window to resize.

        pos : QPoint
            The position of the mouse, in local coordinates.

        mode : int
            The resize mode to apply during the resize. This should be
            the first value returned from the borderTest() method.

        offset : QPoint
            The offset of the mouse press at the border. This should be
            the second value returned from the borderTest() method.

        """
        handler = _RESIZE_HANDLERS.get(mode)
        if handler is not None:
            handler(window, pos, offset)


def _resize_north(widget, pos, offset):
    """ A resize handler for north resizing.

    """
    dh = pos.y() - offset.y()
    height = widget.height()
    min_height = widget.minimumSizeHint().height()
    if height - dh < min_height:
        dh = height - min_height
    rect = widget.geometry()
    rect.setY(rect.y() + dh)
    widget.setGeometry(rect)


def _resize_south(widget, pos, offset):
    """ A resize handler for south resizing.

    """
    dh = pos.y() - widget.height() + offset.y()
    size = widget.size()
    size.setHeight(size.height() + dh)
    widget.resize(size)


def _resize_east(widget, pos, offset):
    """ A resize handler for east resizing.

    """
    dw = pos.x() - widget.width() + offset.x()
    size = widget.size()
    size.setWidth(size.width() + dw)
    widget.resize(size)


def _resize_west(widget, pos, offset):
    """ A resize handler for west resizing.

    """
    dw = pos.x() - offset.x()
    width = widget.width()
    min_width = widget.minimumSizeHint().width()
    if width - dw < min_width:
        dw = width - min_width
    rect = widget.geometry()
    rect.setX(rect.x() + dw)
    widget.setGeometry(rect)


def _resize_northeast(widget, pos, offset):
    """ A resize handler for northeast resizing.

    """
    dw = pos.x() - widget.width() + offset.x()
    dh = pos.y() - offset.y()
    size = widget.size()
    min_size = widget.minimumSizeHint()
    if size.height() - dh < min_size.height():
        dh = size.height() - min_size.height()
    rect = widget.geometry()
    rect.setWidth(rect.width() + dw)
    rect.setY(rect.y() + dh)
    widget.setGeometry(rect)


def _resize_northwest(widget, pos, offset):
    """ A resize handler for northwest resizing.

    """
    dw = pos.x() - offset.x()
    dh = pos.y() - offset.y()
    size = widget.size()
    min_size = widget.minimumSizeHint()
    if size.width() - dw < min_size.width():
        dw = size.width() - min_size.width()
    if size.height() - dh < min_size.height():
        dh = size.height() - min_size.height()
    rect = widget.geometry()
    rect.setX(rect.x() + dw)
    rect.setY(rect.y() + dh)
    widget.setGeometry(rect)


def _resize_southwest(widget, pos, offset):
    """ A resize handler for southwest resizing.

    """
    dw = pos.x() - offset.x()
    dh = pos.y() - widget.height() + offset.y()
    size = widget.size()
    min_size = widget.minimumSizeHint()
    if size.width() - dw < min_size.width():
        dw = size.width() - min_size.width()
    rect = widget.geometry()
    rect.setX(rect.x() + dw)
    rect.setHeight(rect.height() + dh)
    widget.setGeometry(rect)


def _resize_southeast(widget, pos, offset):
    """ A resize handler for southeast resizing.

    """
    dw = pos.x() - widget.width() + offset.x()
    dh = pos.y() - widget.height() + offset.y()
    size = widget.size()
    size.setWidth(size.width() + dw)
    size.setHeight(size.height() + dh)
    widget.resize(size)


_RESIZE_HANDLERS = {
    DockWindowResizer.North: _resize_north,
    DockWindowResizer.South: _resize_south,
    DockWindowResizer.East: _resize_east,
    DockWindowResizer.West: _resize_west,
    DockWindowResizer.NorthEast: _resize_northeast,
    DockWindowResizer.SouthWest: _resize_southwest,
    DockWindowResizer.NorthWest: _resize_northwest,
    DockWindowResizer.SouthEast: _resize_southeast,
}
