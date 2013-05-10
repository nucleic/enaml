#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QAbstractButton, QPainter, QIcon


class QIconButton(QAbstractButton):
    """ A button widget which renders tightly to its icon.

    """
    def sizeHint(self):
        """ Get the size hint for the icon button.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the icon button.

        """
        left, top, right, bottom = self.getContentsMargins()
        return self.iconSize() + QSize(left + right, top + bottom)

    def enterEvent(self, event):
        """ Handle the enter event for the button.

        """
        super(QIconButton, self).enterEvent(event)
        if sys.platform == 'darwin':
            self.repaint()

    def leaveEvent(self, event):
        """ Handle the leave event for the button.

        """
        super(QIconButton, self).leaveEvent(event)
        if sys.platform == 'darwin':
            self.repaint()

    def paintEvent(self, event):
        """ Handle the paint event for the button.

        """
        icon = self.icon()
        if icon.isNull():
            return
        if self.isDown():
            mode = QIcon.Selected
        elif self.underMouse():
            mode = QIcon.Active
        else:
            mode = QIcon.Normal
        icon.paint(QPainter(self), self.contentsRect(), mode=mode)
