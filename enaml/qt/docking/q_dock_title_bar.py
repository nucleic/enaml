#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QSize, QMargins, pyqtSignal
from PyQt4.QtGui import QWidget, QFrame, QPainter, QIcon

from .q_dock_title_bar_buttons import QDockTitleBarButtons


class IDockTitleBar(QWidget):
    """ An interface class for defining a title bar.

    """
    #: A signal emitted when the close button is clicked.
    closeButtonClicked = pyqtSignal()

    def title(self):
        """ Get the title string of the title bar.

        Returns
        -------
        result : unicode
            The unicode title string for the title bar.

        """
        raise NotImplementedError

    def setTitle(self, title):
        """ Set the title string of the title bar.

        Parameters
        ----------
        title : unicode
            The unicode string to use for the title bar.

        """
        raise NotImplementedError

    def icon(self):
        """ Get the icon for the title bar.

        Returns
        -------
        result : QIcon
            The icon set for the title bar.

        """
        raise NotImplementedError

    def setIcon(self, icon):
        """ Set the icon for the title bar.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the title bar.

        """
        raise NotImplementedError

    def iconSize(self):
        """ Get the icon size for the title bar.

        Returns
        -------
        result : QSize
            The size to use for the icons in the title bar.

        """
        raise NotImplementedError

    def setIconSize(self, size):
        """ Set the icon size for the title bar.

        Parameters
        ----------
        icon : QSize
            The icon size to use for the title bar. Icons smaller than
            this size will not be scaled up.

        """
        raise NotImplementedError


class QDockTitleBar(QFrame, IDockTitleBar):
    """ A concrete implementation of IDockTitleBar.

    This class serves as the default title bar for a QDockItem.

    """
    #: A signal emitted when the close button is clicked.
    closeButtonClicked = pyqtSignal()

    #: The minimum height of the title bar.
    MIN_HEIGHT = 19

    #: The horizontal gap between the icon and the title text.
    ICON_HGAP = 3

    #: The vertical padding to use when auto-computing an icon size.
    ICON_PAD = 4

    #: The vertical margin when no icon is present.
    VMARGIN_NO_ICON = 2

    #: The vertical margin when an icon is present.
    VMARGIN_ICON = 4

    #: The horizontal margin.
    HMARGIN = 4

    def __init__(self, parent=None):
        """ Initialize a QDockTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockTitleBar, self).__init__(parent)
        self._size_hint = QSize()
        self._cicon_size = QSize()
        self._title = u''
        self._icon = QIcon()
        self._icon_size = QSize()
        self._buttons = QDockTitleBarButtons(self)
        self._buttons.closeButtonClicked.connect(self.closeButtonClicked)
        hmargin = self.HMARGIN
        vmargin = self.VMARGIN_NO_ICON
        self.setContentsMargins(QMargins(hmargin, vmargin, hmargin, vmargin))

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

    def _invalidate(self):
        """ Invalidate the computed cached data.

        """
        self._size_hint = QSize()
        self._cicon_size = QSize()

    def _effectiveIconSize(self):
        """ Get the actual icon size for the title bar.

        This will return the user specified size if valid, or a size
        computed from the text height of the title bar.

        """
        size = self._icon_size
        if size.isValid():
            return size
        size = self._cicon_size
        if size.isValid():
            return size
        pad = 2 * self.ICON_PAD
        height = self.fontMetrics().tightBoundingRect('M').height() + pad
        size = self._cicon_size = QSize(height, height)
        return size

    #--------------------------------------------------------------------------
    # IDockItemTitleBar API
    #--------------------------------------------------------------------------
    def title(self):
        """ Get the title string of the title bar.

        Returns
        -------
        result : unicode
            The unicode title string for the title bar.

        """
        return self._title

    def setTitle(self, title):
        """ Set the title string of the title bar.

        Parameters
        ----------
        title : unicode
            The unicode string to use for the title bar.

        """
        self._invalidate()
        self._title = title
        self.updateGeometry()
        self.update()

    def icon(self):
        """ Get the icon for the title bar.

        Returns
        -------
        result : QIcon
            The icon set for the title bar.

        """
        return self._icon

    def setIcon(self, icon):
        """ Set the icon for the title bar.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the title bar.

        """
        self._invalidate()
        self._icon = icon
        hmargin = self.HMARGIN
        vmargin = self.VMARGIN_NO_ICON if icon.isNull() else self.VMARGIN_ICON
        self.setContentsMargins(QMargins(hmargin, vmargin, hmargin, vmargin))
        self.updateGeometry()
        self.update()

    def iconSize(self):
        """ Get the icon size for the title bar.

        Returns
        -------
        result : QSize
            The size to use for the icons in the title bar.

        """
        return self._icon_size

    def setIconSize(self, size):
        """ Set the icon size for the title bar.

        Parameters
        ----------
        icon : QSize
            The icon size to use for the title bar. Icons smaller than
            this size will not be scaled up.

        """
        self._invalidate()
        self._icon_size = size
        self.updateGeometry()
        self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def resizeEvent(self, event):
        """ Handle the resize event for the title bar.

        This handler will position the title bar buttons.

        """
        super(QDockTitleBar, self).resizeEvent(event)
        buttons = self._buttons
        size = buttons.minimumSizeHint()
        x = self.width() - size.width() - self.contentsMargins().right()
        y = (self.height() - size.height()) / 2
        rect = QRect(x, y, size.width(), size.height())
        buttons.setGeometry(rect)

    def paintEvent(self, event):
        """ Handle the paint event for the title bar.

        This paint handler draws the title bar text and title buttons.

        """
        super(QDockTitleBar, self).paintEvent(event)
        painter = QPainter(self)
        rect = self.contentsRect()
        icon = self._icon
        if not icon.isNull():
            pm = icon.pixmap(self._effectiveIconSize())
            x = rect.left()
            y = rect.top() + (rect.height() - pm.height()) / 2
            painter.drawPixmap(x, y, pm)
            rect.setLeft(x + pm.width() + self.ICON_HGAP + 1)
        metrics = self.fontMetrics()
        width_adjust = self._buttons.width() + self.ICON_HGAP
        rect = rect.adjusted(0, 0, -width_adjust, 0)
        text = metrics.elidedText(self._title, Qt.ElideRight, rect.width())
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)

    def sizeHint(self):
        """ Get the size hint for the title bar.

        The title bar's size hint is equivalent to its minimumSizeHint.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the title bar.

        The minimum size hint allows for enough space for the minimum
        elided text, the icon, and the contents margins.

        """
        size = self._size_hint
        if size.isValid():
            return size
        metrics = self.fontMetrics()
        mgns = self.contentsMargins()
        text = self._computeElidedText(self._title)
        bsize = self._buttons.minimumSizeHint()
        bwidth = bsize.width() + self.ICON_HGAP
        width = mgns.left() + metrics.width(text) + bwidth + mgns.right()
        height = mgns.top() + mgns.bottom()
        if self._icon.isNull():
            height += max(metrics.height(), bsize.height())
        else:
            icon_size = self._effectiveIconSize()
            width += icon_size.width() + self.ICON_HGAP
            height += max(metrics.height(), icon_size.height(), bsize.height())
        size = self._size_hint = QSize(width, max(self.MIN_HEIGHT, height))
        return size
