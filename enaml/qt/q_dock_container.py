#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, QMargins, QPoint, QEvent
from PyQt4.QtGui import QFrame, QLayout, QRegion

from atom.api import Atom, Typed, Int, Bool

from .dock_window_resizer import DockWindowResizer


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
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        self._dock_item = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockItem(self):
        """ Get the dock item for the layout.

        Returns
        -------
        result : QDockItem
            The dock item set in the layout.

        """
        return self._dock_item

    def setDockItem(self, dock_item):
        """ Set the dock item for the layout.

        The old dock item will be hidden and unparented, but not
        destroyed.

        Parameters
        ----------
        dock_item : QDockItem
            The primary dock item to use in the layout.

        """
        old_item = self._dock_item
        if old_item is not None:
            old_item.hide()
            old_item.setParent(None)
        self._dock_item = dock_item
        if dock_item is not None:
            dock_item.setParent(self.parentWidget())
            dock_item.show()
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        size = QSize()
        self._size_hint = size
        self._min_size = size
        self._max_size = size
        super(QDockContainerLayout, self).invalidate()

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockContainerLayout, self).setGeometry(rect)
        dock_item = self._dock_item
        if dock_item is not None:
            dock_item.setGeometry(self.contentsRect())

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        hint = self._size_hint
        if hint.isValid():
            return hint
        dock_item = self._dock_item
        if dock_item is not None:
            hint = dock_item.sizeHint()
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
        dock_item = self._dock_item
        if dock_item is not None:
            size = dock_item.minimumSizeHint()
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
        dock_item = self._dock_item
        if dock_item is not None:
            size = dock_item.maximumSize()
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
        return 0

    def itemAt(self, idx):
        """ A required virtual method implementation.

        """
        return None

    def takeAt(self, idx):
        """ A required virtual method implementation.

        """
        return None


class QDockContainer(QFrame):
    """ A custom QFrame which holds a QDockItem instance.

    The dock container provides a level of indirection when tearing
    dock items out of a dock area. The window flags for the container
    are controlled by the dock manager driving the dock area.

    """
    #: The size of the extra space for hit testing a resize corner.
    ResizeCornerExtra = 8

    class ContainerState(Atom):
        """ A private class for managing container drag state.

        """
        #: Whether the container is floating as a toplevel window.
        is_floating = Bool(False)

        #: The resize mode based on the mouse hover position.
        resize_mode = Int(DockWindowResizer.NoResize)

        #: The offset point of the cursor during a resize press.
        resize_offset = Typed(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockContainer.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the QDockContainer.

        """
        super(QDockContainer, self).__init__(parent)
        layout = QDockContainerLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.state = self.ContainerState()
        self.handler = None  # set by the dock manager

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockItem(self):
        """ Get the dock item installed on the container.

        Returns
        -------
        result : QDockItem or None
            The dock item installed in the container, or None.

        """
        return self.layout().dockItem()

    def setDockItem(self, dock_item):
        """ Set the dock item for the container.

        Parameters
        ----------
        dock_item : QDockItem
            The dock item to use in the container.

        """
        self.layout().setDockItem(dock_item)

    def isFloating(self):
        """ Get whether the container is floating.

        Returns
        -------
        result : bool
            True if the container is floating, False otherwise.

        """
        return self.state.is_floating

    def setFloating(self, floating):
        """ Set whether the container is floating.

        This flag only affects how the container draws itself. It does
        not change the window flags; that responsibility lies with the
        dock manager which controls the container.

        Parameters
        ----------
        floating : bool
            True if the container is floating, False otherwise.

        """
        state = self.state
        state.is_floating = floating
        self.setAttribute(Qt.WA_Hover, floating)
        if floating:
            self.setContentsMargins(QMargins(5, 5, 5, 5))
        else:
            self.setContentsMargins(QMargins(0, 0, 0, 0))
            self.clearMask()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock container.

        This handler dispatches hover events which are sent when the
        container is floating. It also notifies the dock manager when
        it is activated so that the manager can maintain a proper
        top-level Z-order.

        """
        # hover events are only generated if the WA_Hover attribute is
        # set, and that is only set when the container is floating.
        if event.type() == QEvent.HoverMove:
            self.hoverMoveEvent(event)
            return True
        if event.type() == QEvent.WindowActivate:
            if self.state.is_floating and self.handler is not None:
                self.handler.window_activated()
        return super(QDockContainer, self).event(event)

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the container.

        This handler is invoked when the container is in floating mode.
        It updates the cursor if the mouse is hovered over one of the
        containers resize areas.

        """
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            # don't change the cursor until the resize is finished.
            if state.resize_mode != dwr.NoResize:
                return
            extra = self.ResizeCornerExtra
            mode, ignored = dwr.hit_test(self, event.pos(), extra)
            cursor = dwr.cursor(mode)
            if cursor is None:
                self.unsetCursor()
            else:
                self.setCursor(cursor)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the container.

        This handler sets up the resize and drag operations when the
        container is in floating mode.

        """
        event.ignore()
        state = self.state
        if state.is_floating and event.button() == Qt.LeftButton:
            dwr = DockWindowResizer
            extra = self.ResizeCornerExtra
            mode, offset = dwr.hit_test(self, event.pos(), extra)
            if mode != dwr.NoResize:
                state.resize_mode = mode
                state.resize_offset = offset
                event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the container.

        This handler finalizes the mouse event when the container is
        in floating mode.

        """
        event.ignore()
        state = self.state
        if state.is_floating and event.button() == Qt.LeftButton:
            state.resize_mode = DockWindowResizer.NoResize
            state.resize_offset = None
            event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the container.

        This handler resizes and moves the container when it is in
        floating mode.

        """
        event.ignore()
        state = self.state
        if state.is_floating:
            dwr = DockWindowResizer
            if state.resize_mode != dwr.NoResize:
                mode = state.resize_mode
                offset = state.resize_offset
                dwr.resize(self, event.pos(), mode, offset)
                event.accept()

    def resizeEvent(self, event):
        """ Handle the resize event for the container.

        This handler updates the mask on the container if it is set
        to floating mode.

        """
        state = self.state
        if state.is_floating:
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
