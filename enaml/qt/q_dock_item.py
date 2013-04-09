#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect, QPoint, QSize, QMargins, pyqtProperty
from PyQt4.QtGui import QWidget, QFrame, QPainter, QLayout, QApplication

from atom.api import Atom, Typed, Bool

from .q_dock_area import QDockArea


class TitlePosition(object):
    """ An enum for describing the position of a dock title bar.

    """
    #: The title bar is aligned with the left side of the item.
    Left = 1

    #: The title bar is aligned with the top side of the item.
    Top = 2

    #: The title bar is aligned with the right side of the item.
    Right = 3

    #: The title bar is aligned with the bottom side of the item.
    Bottom = 4


class IDockTitleBar(QWidget):
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

    def titlePosition(self):
        """ Get the position of the title bar within the dock item.

        Returns
        -------
        result : int
            A TitlePosition enum value for the title position.

        """
        raise NotImplementedError

    def setTitlePosition(self, position):
        """ Set the position of the title bar within the dock item.

        Parameters
        ----------
        position : int
            A TitlePosition enum value for the title position.

        """
        raise NotImplementedError


class QDockTitleBar(QFrame, IDockTitleBar):
    """ A concrete implementation of IDockTitleBar.

    This class serves as the default title bar for a QDockItem.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockTitleBar, self).__init__(parent)
        self._sh = QSize()
        self._title = u''
        self._title_position = TitlePosition.Top
        self._margins = QMargins(5, 2, 5, 2)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def margins(self):
        """ Get the margins for the title bar.

        Returns
        -------
        result : QMargins
            The margins for the title bar.

        """
        return self._margins

    def setMargins(self, margins):
        """ Set the margins for the title bar.

        Parameters
        ----------
        margins : QMargins
            The margins to use for the title bar.

        """
        self._sh = QSize()
        self._margins = margins
        self.updateGeometry()

    #--------------------------------------------------------------------------
    # IDockTitleBar API
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

    p_title = pyqtProperty(unicode, title, setTitle)

    def titlePosition(self):
        """ Get the position of the title bar within the dock item.

        Returns
        -------
        result : int
            A TitlePosition enum value for the title position.

        """
        return self._title_position

    def setTitlePosition(self, position):
        """ Set the position of the title bar within the dock item.

        Parameters
        ----------
        position : int
            A TitlePosition enum value for the title position.

        """
        self._sh = QSize()
        self._title_position = position
        self.updateGeometry()

    p_titlePosition = pyqtProperty(int, titlePosition, setTitlePosition)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ Handle the paint event for the title bar.

        This paint handler draws the title bar text and title buttons.

        """
        super(QDockTitleBar, self).paintEvent(event)
        painter = QPainter(self)
        m = self.margins()
        w = self.width()
        h = self.height()
        pos = self.titlePosition()
        if pos == TitlePosition.Left:
            rect = QRect(m.left(), m.top(), h - m.right(), w - m.bottom())
            painter.rotate(-90)
            painter.translate(-h, 0)
        elif pos == TitlePosition.Right:
            rect = QRect(m.left(), m.top(), h - m.right(), w - m.bottom())
            painter.rotate(90)
            painter.translate(0, -w)
        else:
            rect = QRect(m.left(), m.top(), w - m.right(), h - m.bottom())
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
        mgns = self.margins()
        fm = self.fontMetrics()
        height = fm.height() + mgns.top() + mgns.bottom()
        width = fm.width(self.title()) + mgns.left() + mgns.right()
        sh = QSize(width, height)
        pos = self.titlePosition()
        if pos == TitlePosition.Left or pos == TitlePosition.Right:
            sh.transpose()
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
        self._sh = QSize()
        self._ms = QSize()
        self._title_bar = None
        self._dock_widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def titleBarWidget(self):
        """ Get the title bar widget set for the layout.

        Returns
        -------
        result : IDockTitleBar or None
            The title bar widget for the layout, or None if no widget
            is applied.

        """
        return self._title_bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        title_bar : IDockTitleBar or None
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
        self._sh = QSize()
        self._ms = QSize()
        super(QDockItemLayout, self).invalidate()

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockItemLayout, self).setGeometry(rect)
        title = self._title_bar
        widget = self._dock_widget
        do_title = title is not None and not title.isHidden()
        do_widget = widget is not None and not widget.isHidden()
        if not do_title and not do_widget:
            return
        if not do_title:
            widget.setGeometry(rect)
            return
        title_rect = QRect(rect)
        widget_rect = QRect(rect)
        pos = title.titlePosition()
        msh = title.minimumSizeHint()
        if pos == TitlePosition.Top:
            title_rect.setHeight(msh.height())
            widget_rect.setTop(title_rect.bottom() + 1)
        elif pos == TitlePosition.Bottom:
            widget_rect.setHeight(rect.height() - msh.height())
            title_rect.setTop(widget_rect.bottom() + 1)
        elif pos == TitlePosition.Left:
            title_rect.setWidth(msh.width())
            widget_rect.setLeft(title_rect.right() + 1)
        elif pos == TitlePosition.Right:
            widget_rect.setWidth(rect.width() - msh.width())
            title_rect.setLeft(widget_rect.right() + 1)
        title.setGeometry(title_rect)
        if do_widget:
            widget.setGeometry(widget_rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        sh = self._sh
        if not sh.isValid():
            ms, sh = self._getSizeHints()
            self._ms = ms
            self._sh = sh
        return sh

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        ms = self._ms
        if not ms.isValid():
            ms, sh = self._getSizeHints()
            self._ms = ms
            self._sh = sh
        return ms

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _getSizeHints(self):
        """ Compute the size hint and minimum size simultaneously.

        Returns
        -------
        result : tuple
            A 2-tuple of (min_size, size_hint) for the layout.

        """
        vert_title = False
        min_width = min_height = 0
        hint_width = hint_height = 0
        title = self._title_bar
        widget = self._dock_widget
        if title is not None and not title.isHidden():
            msh = title.minimumSizeHint()
            min_width = hint_width = msh.width()
            min_height = hint_height = msh.height()
            p = title.titlePosition()
            vert_title = p == TitlePosition.Left or p == TitlePosition.Right
        if widget is not None and not widget.isHidden():
            sh = widget.sizeHint()
            msh = widget.minimumSizeHint()
            if vert_title:
                hint_width += sh.width()
                min_width += msh.width()
                hint_height = max(hint_height, sh.height())
                min_height = max(min_height, msh.height())
            else:
                hint_height += sh.height()
                min_height += msh.height()
                hint_width = max(hint_width, sh.width())
                min_width = max(min_width, sh.width())
        min_size = QSize(min_width, min_height)
        hint_size = QSize(hint_width, hint_height)
        return (min_size, hint_size)

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        msg = 'Use `setTitleBar | setDockWidget` instead.'
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
    class DragState(Atom):
        """ A framework class for managing a dock item drag.

        This class should not be used directly by user code.

        """
        #: The original position of the drag press.
        press_pos = Typed(QPoint)

        #: Whether or not the dock item is being dragged.
        dragging = Bool(False)

    class DockState(Atom):
        """ A framework class for managing a dock item's state.

        This class should not be used directly by user code.

        """
        #: Whether or not the dock item is floating.
        floating = Bool(False)

        #: Whether or not the dock item can be floated by the user.
        floatable = Bool(True)

        #: Whether or not the dock item can be moved by the user.
        movable = Bool(True)

        #: The dock area which owns the item.
        area = Typed(QDockArea)

        layout = Typed(object)

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
        self.setTitleBarWidget(QDockTitleBar())
        self._dock_state = self.DockState()
        self._drag_state = None

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
        self.updateGeometry()

    def titleBarWidget(self):
        """ Get the title bar widget for the dock item.

        If a custom title bar has not been assigned, a default title
        bar will be returned. To prevent showing a title bar, set the
        visibility on the returned title bar to False.

        Returns
        -------
        result : IDockTitleBar
            An implementation of IDockTitleBar. This will never be None.

        """
        layout = self.layout()
        bar = layout.titleBarWidget()
        if bar is None:
            bar = QDockTitleBar()
            layout.setTitleBarWidget(bar)
        return bar

    def setTitleBarWidget(self, title_bar):
        """ Set the title bar widget for the dock item.

        Parameters
        ----------
        title_bar : IDockTitleBar or None
            A custom implementation of IDockTitleBar, or None. If None,
            then the default title bar will be restored.

        """
        title_bar = title_bar or QDockTitleBar()
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
        self.updateGeometry()

    def dockArea(self):
        """ Find the dock area which is the ancestor of this dock item.

        Returns
        -------
        result : QDockArea or None
            The dock area instance which is an ancestor of this item,
            or None if no such ancestor exists.

        """
        area = self._dock_state.area
        if area is not None:
            return area
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                self._dock_state.area = parent
                return parent
            parent = parent.parent()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _initDrag(self, pos):
        """ Initialize the drag state for the dock item.

        If the drag state is already inited, this method is a no-op.

        Parameters
        ----------
        pos : QPoint
            The point where the user clicked the mouse, expressed in
            the local coordinate system.

        """
        if self._drag_state is not None:
            return
        state = self._drag_state = self.DragState()
        state.press_pos = pos

    def _startDrag(self):
        """" Start the drag process for the dock item.

        If the item is already being dragged, this method is a no-op.

        """
        state = self._drag_state
        if state is None or state.dragging:
            return
        dock_area = self.dockArea()
        if dock_area is None:
            return
        dock_area.unplug(self)
        state.dragging = True
        self.grabMouse()

    def _endDrag(self):
        """ End the drag process for the dock item.

        If the item was not being dragged, this method is a no-op.

        """
        if self._drag_state is None:
            return
        self._drag_state = None
        self.releaseMouse()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """ Handle the mouse press event for the dock item.

        This handler will initialize the drag state when the left mouse
        button is pressed within the title bar area.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            rect = self.titleBarWidget().rect()
            if rect.contains(event.pos()):
                self._initDrag(event.pos())
                event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the dock item.

        This handler will start the drag process when the mouse move
        reaches the start drag distance for the application.

        """
        event.ignore()
        state = self._drag_state
        if state is None:
            return
        if state.dragging:
            pos = event.globalPos() - state.press_pos
            self.move(pos)
            area = self.dockArea()
            if area is not None:
                area.hover(self, event.globalPos(), event.modifiers())
            event.accept()
        else:
            dist = (event.pos() - state.press_pos).manhattanLength()
            if dist > QApplication.startDragDistance():
                self._startDrag()
                event.accept()

    def mouseReleaseEvent(self, event):
        """ Hanlde the mouse release event for the dock item.

        This handler will end the drag operation when the left mouse
        button is released.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            self._endDrag()
            area = self.dockArea()
            if area is not None:
                area.endHover(self, event.globalPos(), event.modifiers())
            event.accept()
