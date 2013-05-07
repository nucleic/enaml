#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QFrame, QPainter


class QTextLabel(QFrame):
    """ A custom QFrame which draws elided text.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QTextLabel, self).__init__(parent)
        self._size_hint = QSize()
        self._text = u''

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @staticmethod
    def _computeElidedText(text):
        """ Compute the minimum elided text for the tab title.

        """
        # Based on QTabBar::computeElidedText
        if len(text) > 3:
            text = text[:2] + '...'
        return text

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def text(self):
        """ Get the text string of the text label.

        Returns
        -------
        result : unicode
            The unicode text string for the text label.

        """
        return self._text

    def setText(self, text):
        """ Set the text string of the text label.

        Parameters
        ----------
        text : unicode
            The unicode string to use for the text label.

        """
        self._size_hint = QSize()
        self._text = text
        self.updateGeometry()
        self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Get the size hint for the text label.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the text label.

        """
        size = self._size_hint
        if size.isValid():
            return size
        metrics = self.fontMetrics()
        text = self._computeElidedText(self._text)
        return QSize(metrics.width(text), metrics.height())

    def paintEvent(self, event):
        """ Handle the paint event for the title bar.

        This paint handler draws the title bar text and title buttons.

        """
        super(QTextLabel, self).paintEvent(event)
        rect = self.rect()
        metrics = self.fontMetrics()
        text = metrics.elidedText(self._text, Qt.ElideRight, rect.width())
        QPainter(self).drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
