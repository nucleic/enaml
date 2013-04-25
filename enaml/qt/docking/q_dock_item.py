#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QSize, QMargins
from PyQt4.QtGui import QWidget, QFrame, QPainter, QLayout


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


class QDockItemTitleBar(QFrame, IDockItemTitleBar):
    """ A concrete implementation of IDockItemTitleBar.

    This class serves as the default title bar for a QDockItem.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockItemTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockItemTitleBar, self).__init__(parent)
        self._sh = QSize()
        self._title = u''
        self.setContentsMargins(QMargins(5, 2, 5, 2))

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
        self._sh = QSize()
        self._title = title
        self.updateGeometry()

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
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, self.title())

    def sizeHint(self):
        """ Get the size hint for the title bar.

        The title bar's size hint is equivalent to its minimumSizeHint.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the title bar.

        The size hint allows for enough space for the text with a bit
        of padding on all sides.

        """
        sh = self._sh
        if sh.isValid():
            return sh
        m = self.contentsMargins()
        fm = self.fontMetrics()
        height = fm.height() + m.top() + m.bottom()
        width = fm.width(self.title()) + m.left() + m.right()
        sh = QSize(width, max(19, height))
        self._sh = sh
        return sh


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
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        super(QDockItemLayout, self).invalidate()

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
        self.handler = None  # set by the dock manager

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

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """ Handle the mouse press event for the dock item.

        This handler forwards the mouse press to the dock handler which
        handles the event for docking purposes.

        """
        event.ignore()
        handler = self.handler
        if handler is not None:
            if handler.mouse_press_event(event):
                event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the dock item.

        This handler forwards the mouse press to the dock handler which
        handles the event for docking purposes.

        """
        event.ignore()
        handler = self.handler
        if handler is not None:
            if handler.mouse_move_event(event):
                event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the dock item.

        This handler forwards the mouse press to the dock handler which
        handles the event for docking purposes.

        """
        event.ignore()
        handler = self.handler
        if handler is not None:
            if handler.mouse_release_event(event):
                event.accept()
