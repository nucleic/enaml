#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QSize, QMargins
from PyQt4.QtGui import QWidget, QFrame, QPainter, QLayout, QIcon

from .q_dock_container import QDockContainer
from .q_dock_tab_widget import QDockTabWidget


class IDockItemTitleBar(QWidget):
    """ An interface class for defining a dock title bar.

    """
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


class QDockItemTitleBar(QFrame, IDockItemTitleBar):
    """ A concrete implementation of IDockItemTitleBar.

    This class serves as the default title bar for a QDockItem.

    """
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
        """ Initialize a QDockItemTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockItemTitleBar, self).__init__(parent)
        self._size_hint = QSize()
        self._cicon_size = QSize()
        self._title = u''
        self._icon = QIcon()
        self._icon_size = QSize()
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
    def paintEvent(self, event):
        """ Handle the paint event for the title bar.

        This paint handler draws the title bar text and title buttons.

        """
        super(QDockItemTitleBar, self).paintEvent(event)
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
        margins = self.contentsMargins()
        text = self._computeElidedText(self._title)
        width = metrics.width(text) + margins.left() + margins.right()
        height = margins.top() + margins.bottom()
        if self._icon.isNull():
            height += metrics.height()
        else:
            icon_size = self._effectiveIconSize()
            width += icon_size.width() + self.ICON_HGAP
            height += max(metrics.height(), icon_size.height())
        size = self._size_hint = QSize(width, max(self.MIN_HEIGHT, height))
        return size


class QDockItemLayout(QLayout):
    """ A QLayout subclass for laying out a dock item.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QDockItemLayout, self).__init__(parent)
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        self._title_bar = None
        self._dock_widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def titleBarWidget(self):
        """ Get the title bar widget set for the layout.

        Returns
        -------
        result : IDockItemTitleBar or None
            The title bar widget for the layout, or None if no widget
            is applied.

        """
        return self._title_bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        title_bar : IDockItemTitleBar or None
            A concrete implementor of the title bar interface, or None.

        """
        old_bar = self._title_bar
        if old_bar is not None:
            old_bar.hide()
            old_bar.setParent(None)
        self._title_bar = title_bar
        if title_bar is not None:
            title_bar.setParent(self.parentWidget())
        self.invalidate()

    def dockWidget(self):
        """ Get the dock widget set for the layout.

        Returns
        -------
        result : QWidget
            The primary widget set in the dock item layout.

        """
        return self._dock_widget

    def setDockWidget(self, widget):
        """ Set the dock widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the primary content in the layout.

        """
        old_widget = self._dock_widget
        if widget is old_widget:
            return
        if old_widget is not None:
            old_widget.hide()
            old_widget.setParent(None)
        self._dock_widget = widget
        if widget is not None:
            widget.setParent(self.parentWidget())
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the layout.

        """
        super(QDockItemLayout, self).invalidate()
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockItemLayout, self).setGeometry(rect)
        title = self._title_bar
        widget = self._dock_widget
        title_rect = QRect(rect)
        widget_rect = QRect(rect)
        if title is not None and not title.isHidden():
            msh = title.minimumSizeHint()
            title_rect.setHeight(msh.height())
            widget_rect.setTop(title_rect.bottom() + 1)
            title.setGeometry(title_rect)
        if widget is not None and not widget.isHidden():
            widget.setGeometry(widget_rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        sh = self._size_hint
        if not sh.isValid():
            width = height = 0
            title = self._title_bar
            widget = self._dock_widget
            if title is not None and not title.isHidden():
                hint = title.sizeHint()
                width += hint.width()
                height += hint.height()
            if widget is not None and not widget.isHidden():
                hint = widget.sizeHint()
                width = max(width, hint.width())
                height += hint.height()
            sh = self._size_hint = QSize(width, height)
        return sh

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        ms = self._min_size
        if not ms.isValid():
            width = height = 0
            title = self._title_bar
            widget = self._dock_widget
            if title is not None and not title.isHidden():
                hint = title.minimumSizeHint()
                width += hint.width()
                height += hint.height()
            if widget is not None and not widget.isHidden():
                hint = widget.minimumSizeHint()
                width = max(width, hint.width())
                height += hint.height()
            ms = self._min_size = QSize(width, height)
        return ms

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        ms = self._max_size
        if not ms.isValid():
            widget = self._dock_widget
            if widget is not None:
                ms = widget.maximumSize()
                title = self._title_bar
                if title is not None and not title.isHidden():
                    height = ms.height() + title.minimumSizeHint().height()
                    ms.setHeight(min(16777215, height))
            else:
                ms = QSize(16777215, 16777215)
            self._max_size = ms
        return ms

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        msg = 'Use `setTitleBarWidget | setDockWidget` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        return 0

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        return None

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None


class QDockItem(QFrame):
    """ A QFrame subclass which acts as an item QDockArea.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockItem.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the dock item.

        """
        super(QDockItem, self).__init__(parent)
        layout = QDockItemLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.setTitleBarWidget(QDockItemTitleBar())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def title(self):
        """ Get the title for the dock item.

        Returns
        -------
        result : unicode
            The unicode title for the dock item.

        """
        return self.titleBarWidget().title()

    def setTitle(self, title):
        """ Set the title for the dock item.

        Parameters
        ----------
        title : unicode
            The unicode title to use for the dock item.

        """
        self.titleBarWidget().setTitle(title)
        # A concession to practicality: walk the ancestry and update
        # the tab title if this item lives in a dock tab.
        container = self.parent()
        if container is not None:
            stacked = container.parent()
            if stacked is not None:
                tabs = stacked.parent()
                if isinstance(tabs, QDockTabWidget):
                    index = tabs.indexOf(container)
                    tabs.setTabText(index, title)

    def icon(self):
        """ Get the icon for the dock item.

        Returns
        -------
        result : QIcon
            The icon in use for the dock item.

        """
        return self.titleBarWidget().icon()

    def setIcon(self, icon):
        """ Set the icon for the dock item.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the dock item.

        """
        self.titleBarWidget().setIcon(icon)
        # A concession to practicality: walk the ancestry and update
        # the tab icon if this item lives in a dock tab.
        container = self.parent()
        if container is not None:
            stacked = container.parent()
            if stacked is not None:
                tabs = stacked.parent()
                if isinstance(tabs, QDockTabWidget):
                    index = tabs.indexOf(container)
                    tabs.setTabIcon(index, icon)

    def iconSize(self):
        """ Get the icon size for the title bar.

        Returns
        -------
        result : QSize
            The size to use for the icons in the title bar.

        """
        return self.titleBarWidget().iconSize()

    def setIconSize(self, size):
        """ Set the icon size for the title bar.

        Parameters
        ----------
        icon : QSize
            The icon size to use for the title bar. Icons smaller than
            this size will not be scaled up.

        """
        self.titleBarWidget().setIconSize(size)

    def titleBarWidget(self):
        """ Get the title bar widget for the dock item.

        If a custom title bar has not been assigned, a default title
        bar will be returned. To prevent showing a title bar, set the
        visibility on the returned title bar to False.

        Returns
        -------
        result : IDockItemTitleBar
            An implementation of IDockItemTitleBar. This will never be
            None.

        """
        layout = self.layout()
        bar = layout.titleBarWidget()
        if bar is None:
            bar = QDockItemTitleBar()
            layout.setTitleBarWidget(bar)
        return bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the dock item.

        Parameters
        ----------
        title_bar : IDockItemTitleBar or None
            A custom implementation of IDockItemTitleBar, or None. If
            None, then the default title bar will be restored.

        """
        title_bar = title_bar or QDockItemTitleBar()
        self.layout().setTitleBarWidget(title_bar)

    def dockWidget(self):
        """ Get the dock widget for this dock item.

        Returns
        -------
        result : QWidget or None
            The dock widget being managed by this item.

        """
        return self.layout().dockWidget()

    def setDockWidget(self, widget):
        """ Set the dock widget for this dock item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the dock widget in this item.

        """
        self.layout().setDockWidget(widget)

    def closeEvent(self, event):
        """ Handle the close event for the dock item.

        """
        event.accept()
        parent = self.parent()
        if isinstance(parent, QDockContainer):
            manager = parent.manager()
            if manager is not None:
                manager.remove_dock_item(self)
                event.ignore()  # the item has already been hidden
