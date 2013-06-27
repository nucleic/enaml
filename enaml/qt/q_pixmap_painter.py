#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QObject, QEvent, Slot
from .QtGui import QPainter, QPixmap


class QPixmapPainter(QObject):
    """ A QObject class which will paint a pixmap onto a QWidget.

    """
    def __init__(self):
        """ Initialize a QPixmapPainter.

        """
        super(QPixmapPainter, self).__init__()
        self._target = None
        self._pixmap = None

    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    @Slot(QPixmap)
    def drawPixmap(self, pixmap):
        """ Draw the given pixmap onto the parent widget.

        This method is also a Slot which can be connected to signal that
        emits a QPixmap payload.

        Parameters
        ----------
        pixmap : QPixmap
            The pixmap to draw in on the parent.

        """
        self._pixmap = pixmap
        target = self._target
        if target is not None:
            target.update()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def targetWidget(self):
        """ Get the target widget of this painter.

        Returns
        -------
        result : QWidget or None
            The target widget onto which this painter will paint, or
            None if a widget has not yet been provided.

        """
        return self._target

    def setTargetWidget(self, widget):
        """ Set the target widget for this painter.

        Parameters
        ----------
        widget : QWidget
            The widget onto which this painter will paint incoming
            pixmaps.

        """
        old = self._target
        if old is not None:
            old.removeEventFilter(self)
        if widget is not None:
            widget.installEventFilter(self)
        self._target = widget

    def eventFilter(self, obj, event):
        """ Filter the events for the given object.

        This method will only filter paint events for the target of this
        object. If there is a pixmap available for drawing, then that
        will be drawn onto the target.

        """
        if event.type() == QEvent.Paint:
            if obj is self._target:
                pm = self._pixmap
                if pm is not None:
                    painter = QPainter(obj)
                    painter.drawPixmap(0, 0, pm)
                    return True
        return False
