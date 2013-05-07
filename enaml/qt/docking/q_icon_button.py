#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QAbstractButton, QPainter, QIcon


class QIconButton(QAbstractButton):
    """ A button widget which renders tightly to its icon.

    """
    def __init__(self, parent=None):
        """ Initialize a QIconButton.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the icon button.

        """
        super(QIconButton, self).__init__(parent)
        self._has_mouse = False

    def sizeHint(self):
        """ Get the size hint for the icon button.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the icon button.

        """
        return self.iconSize()

    def mousePressEvent(self, event):
        """ Handle the mouse move event for the button.

        """
        self._has_mouse = True
        super(QIconButton, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the button.

        """
        self._has_mouse = self.hitButton(event.pos())
        super(QIconButton, self).mouseReleaseEvent(event)

    def enterEvent(self, event):
        """ Handle the enter event for the button.

        """
        self._has_mouse = True
        super(QIconButton, self).leaveEvent(event)

    def leaveEvent(self, event):
        """ Handle the leave event for the button.

        """
        self._has_mouse = False
        super(QIconButton, self).leaveEvent(event)

    def paintEvent(self, event):
        """ Handle the paint event for the button.

        """
        icon = self.icon()
        if icon.isNull():
            return
        if self.isDown():
            mode = QIcon.Selected
        elif self._has_mouse:
            mode = QIcon.Active
        else:
            mode = QIcon.Normal
        icon.paint(QPainter(self), self.rect(), mode=mode)
