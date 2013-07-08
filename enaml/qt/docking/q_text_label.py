#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import Qt, QSize, QEvent
from enaml.qt.QtGui import QFrame, QPainter


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
        self._min_text_size = QSize()
        self._text_size = QSize()
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
        self._min_text_size = QSize()
        self._text_size = QSize()
        self._text = text
        self.updateGeometry()
        self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def event(self, event):
        """ The generic event handler for the text label.

        This handler ensures the size hint caches are invalidated when
        the widget style changes.

        """
        if event.type() == QEvent.StyleChange:
            self._min_text_size = QSize()
            self._text_size = QSize()
        return super(QTextLabel, self).event(event)

    def sizeHint(self):
        """ Get the size hint for the text label.

        """
        base = self._text_size
        if not base.isValid():
            metrics = self.fontMetrics()
            base = QSize(metrics.width(self._text), metrics.height())
            self._text_size = base
        left, top, right, bottom = self.getContentsMargins()
        return base + QSize(left + right, top + bottom)

    def minimumSizeHint(self):
        """ Get the minimum size hint for the text label.

        """
        base = self._min_text_size
        if not base.isValid():
            metrics = self.fontMetrics()
            text = self._computeElidedText(self._text)
            base = QSize(metrics.width(text), metrics.height())
            self._min_text_size = base
        left, top, right, bottom = self.getContentsMargins()
        return base + QSize(left + right, top + bottom)

    def paintEvent(self, event):
        """ Handle the paint event for the title bar.

        This paint handler draws the title bar text and title buttons.

        """
        super(QTextLabel, self).paintEvent(event)
        rect = self.contentsRect()
        metrics = self.fontMetrics()
        # The +1 is to fix a seeming off-by-one error in elidedText.
        # https://github.com/nucleic/enaml/issues/38
        text = metrics.elidedText(self._text, Qt.ElideRight, rect.width() + 1)
        QPainter(self).drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
