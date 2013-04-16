#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QMargins, QPoint, QEvent
from PyQt4.QtGui import QFrame, QLayout, QRegion, QWidgetItem

from atom.api import Atom, Typed, Bool


class QDockContainerLayout(QLayout):
    """ A QLayout subclass which handles the layout for QDockContainer.

    This class is used by the docking framework and is not intended for
    direct use by user code.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockContainerLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QDockContainerLayout, self).__init__(parent)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        self._widget_item = None
        self._widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockWidget(self):
        """ Get the dock widget set for the layout.

        Returns
        -------
        result : QWidget
            The primary dock widget set in the container layout.

        """
        return self._widget

    def setDockWidget(self, widget):
        """ Set the dock widget for the layout.

        The old widget will be hidden and unparented, but not destroyed.

        Parameters
        ----------
        widget : QWidget
            The primary widget to use in the layout.

        """
        old_widget = self._widget
        if old_widget is not None:
            old_widget.hide()
            old_widget.setParent(None)
        self._widget_item = None
        self._widget = widget
        if widget is not None:
            self._widget_item = QWidgetItem(widget)
            widget.setParent(self.parentWidget())
            widget.show()
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        super(QDockContainerLayout, self).invalidate()

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockContainerLayout, self).setGeometry(rect)
        widget = self._widget
        if widget is not None:
            widget.setGeometry(self.contentsRect())

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        hint = self._size_hint
        if hint.isValid():
            return hint
        widget = self._widget
        if widget is not None:
            hint = widget.sizeHint()
        else:
            hint = QSize(256, 192)
        m = self.contentsMargins()
        hint.setWidth(hint.width() + m.left() + m.right())
        hint.setHeight(hint.height() + m.top() + m.bottom())
        self._size_hint = hint
        return hint

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        size = self._min_size
        if size.isValid():
            return size
        widget = self._widget
        if widget is not None:
            size = widget.minimumSizeHint()
        else:
            size = QSize(256, 192)
        m = self.contentsMargins()
        size.setWidth(size.width() + m.left() + m.right())
        size.setHeight(size.height() + m.top() + m.bottom())
        self._min_size = size
        return size

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        size = self._max_size
        if size.isValid():
            return size
        widget = self._widget
        if widget is not None:
            size = widget.maximumSize()
        else:
            size = QSize(16777215, 16777215)
        self._max_size = size
        return size

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        raise NotImplementedError('Use `setWidget` instead.')

    def count(self):
        """ A required virtual method implementation.

        """
        return 1 if self._widget_item is not None else 0

    def itemAt(self, idx):
        """ A required virtual method implementation.

        """
        if idx == 0:
            return self._widget_item

    def takeAt(self, idx):
        """ A required virtual method implementation.

        """
        if idx == 0:
            self._widget_item = None
            if self._widget:
                self._widget.hide()
                self._widget.setParent(None)
                self._widget = None


class QDockContainer(QFrame):
    """ A custom QFrame which hold one or more QDockItem instances.

    The dock manager which manages the container will drive the layout
    of the container.

    """
    #: The size of the resize hit box in the lower-right corner.
    RESIZER_BOX_SIZE = 10

    #: The height to allocate for the title bar when it's visible.
    TITLE_BAR_HEIGHT = 15

    #: The offset use for the cursor during resize events.
    RESIZE_OFFSET = 2

    class ContainerState(Atom):
        """ A private class for managing container drag state.

        """
        #: Whether or not the title bar is visible.
        title_bar_visible = Bool(False)

        #: The position of the mouse press in the title bar.
        title_press_pos = Typed(QPoint)

        #: Whether the container is floating as a toplevel window.
        floating = Bool(False)

        #: Whether the mouse is hovering over the resize box.
        in_resize_box = Bool(False)

        #: Whether the container is being actively resized.
        resizing = Bool(False)

        #: Whether a mask is installed on the container.
        has_mask = Bool(False)

    def __init__(self, parent=None):
        """ Initialize a QDockContainer.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the QDockContainer.

        """
        super(QDockContainer, self).__init__(parent)
        layout = QDockContainerLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.dock_manager = None  # set by framework
        self._state = self.ContainerState()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def floating(self):
        """ Get whether the container is floating.

        Returns
        -------
        result : bool
            True if the container is floating, False otherwise.

        """
        return self._state.floating

    def setFloating(self, floating):
        """ Set whether the container is in floating mode.

        This flag only affects how the container draws itself. It does
        not change the window hierarchy; that responsibility lies with
        the docking manager in use for the container.

        Parameters
        ----------
        floating : bool
            True if floating mode should be active, False otherwise.

        """
        state = self._state
        state.floating = floating
        self.setAttribute(Qt.WA_Hover, floating)
        if floating:
            self.setContentsMargins(QMargins(5, 5, 5, 5))
        else:
            self.setContentsMargins(QMargins(0, 0, 0, 0))
            if state.has_mask:
                state.has_mask = False
                self.unsetMask()

    def titleBarVisible(self):
        """ Get whether the title bar is visible.

        Returns
        -------
        result : bool
            True if the title bar area is visible, False otherwise.

        """
        return self._state.title_bar_visible

    def setTitleBarVisible(self, visible):
        """ Set whether the title bar is visible for the container.

        Parameters
        ----------
        floating : bool
            True if the title bar should be visible, False otherwise.

        """
        self._state.title_bar_visible = visible
        layout = self.layout()
        if layout is not None:
            height = self.TITLE_BAR_HEIGHT
            margins = QMargins(0, height if visible else 0, 0, 0)
            layout.setContentsMargins(margins)

    def dockWidget(self):
        """ Get the dock widget installed on the container.

        Returns
        -------
        result : QDockItem or None
            The dock widget installed on the container, or None if
            no widget is installed.

        """
        return self.layout().dockWidget()

    def setDockWidget(self, widget):
        """ Set the dock widget for the container.

        Parameters
        ----------
        widget : QWidget or None
            The primary widget to use in the container, or None to
            unset the widget.

        """
        self.layout().setDockWidget(widget)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock container.

        This handler dispatches hover events which are sent when the
        container is in floating mode. It also notifies the docking
        manager when it is activated so that the manager can maintain
        a proper top-level Z-order.

        """
        if event.type() == QEvent.HoverMove:
            self.hoverMoveEvent(event)
            return True
        if event.type() == QEvent.WindowActivate:
            pass
        return super(QDockContainer, self).event(event)

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the container.

        This handler is invoked when the container is in floating mode.
        It updates the cursor if the mouse is hovered over the resize
        hit-box in the lower right corner of the widget.

        """
        state = self._state
        if state.floating:
            pos = event.pos()
            width = self.width()
            height = self.height()
            box_size = self.RESIZER_BOX_SIZE
            if pos.x() >= width - box_size and pos.y() >= height - box_size:
                state.in_resize_box = True
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                state.in_resize_box = False
                self.unsetCursor()

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the container.

        This handler sets up the resize and drag operations when the
        container is in floating mode.

        """
        event.ignore()
        state = self._state
        if state.floating and event.button() == Qt.LeftButton:
            if state.in_resize_box:
                state.resizing = True
                event.accept()
            elif state.title_bar_visible:
                margins = self.contentsMargins()
                l_margins = self.layout().contentsMargins()
                if event.pos().y() < margins.top() + l_margins.top():
                    state.title_press_pos = event.pos()
                    event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the container.

        This handler finalizes the mouse event when the container is
        in floating mode.

        """
        event.ignore()
        state = self._state
        if state.floating and event.button() == Qt.LeftButton:
            if state.resizing or state.title_press_pos is not None:
                state.resizing = False
                state.title_press_pos = None
                event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the container.

        This handler resizes and moves the container when it is in
        floating mode.

        """
        event.ignore()
        state = self._state
        if state.floating:
            if state.resizing:
                pos = event.pos()
                offset = self.RESIZE_OFFSET
                self.resize(QSize(pos.x() + offset, pos.y() + offset))
                event.accept()
            elif state.title_press_pos is not None:
                self.move(event.globalPos() - state.title_press_pos)
                event.accept()

    def resizeEvent(self, event):
        """ Handle the resize event for the container.

        This handler updates the mask on the container if it is set
        to floating mode.

        """
        state = self._state
        if state.floating:
            w = self.width()
            h = self.height()
            region = QRegion(0, 0, w, h)
            # top left
            region -= QRegion(0, 0, 3, 1)
            region -= QRegion(0, 0, 1, 3)
            # top right
            region -= QRegion(w - 3, 0, 3, 1)
            region -= QRegion(w - 1, 0, 1, 3)
            # bottom left
            region -= QRegion(0, h - 3, 1, 3)
            region -= QRegion(0, h - 1, 3, 1)
            # bottom right
            region -= QRegion(w - 1, h - 3, 1, 3)
            region -= QRegion(w - 3, h - 1, 3, 1)
            self.setMask(region)
            state.has_mask = True

    def paintEvent(self, event):
        """ Handle the paint event for the container.

        This handler draws the title bar for the container if the
        title bar is set to visible.

        """
        super(QDockContainer, self).paintEvent(event)
        state = self._state
        if state.title_bar_visible:
            #top = self.layout().contentsMargins().top()
            # draw stuff.
            pass
