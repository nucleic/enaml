#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import QSize
from enaml.qt.QtGui import QIcon, QPainter
from enaml.qt.QtWidgets import QFrame


class QIconWidget(QFrame):
    """ A custom QFrame which paints an icon.

    """
    def __init__(self, parent=None):
        """ Initialize a QIconWidget.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the icon widget.

        """
        super(QIconWidget, self).__init__(parent)
        self._icon_size = QSize()
        self._icon = QIcon()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def icon(self):
        """ Get the icon for the widget.

        Returns
        -------
        result : QIcon
            The icon installed on the widget.

        """
        return self._icon

    def setIcon(self, icon):
        """ Set the icon for the widget.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the widget.

        """
        self._icon = icon
        self.update()

    def iconSize(self):
        """ Get the icon size for the widget.

        Returns
        -------
        result : QSize
            The size to use for displaying the icon.

        """
        return self._icon_size

    def setIconSize(self, size):
        """ Set the icon size for the widget.

        Parameters
        ----------
        size : QSize
            The icon size to use for the widget.

        """
        self._icon_size = size
        self.updateGeometry()
        self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Get the size hint for the widget.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the widget.

        """
        size = self._icon_size
        if not size.isValid():
            size = QSize(16, 16)
        left, top, right, bottom = self.getContentsMargins()
        return size + QSize(left + right, top + bottom)

    def paintEvent(self, event):
        """ Handle the paint event for the widget.

        """
        super(QIconWidget, self).paintEvent(event)
        icon = self._icon
        if icon.isNull():
            return
        icon.paint(QPainter(self), self.contentsRect())
