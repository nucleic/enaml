#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed

from enaml.qt.QtCore import (
    Qt, QMetaObject, QMargins, QPoint, QRect, QSize, Signal
)
from enaml.qt.QtWidgets import QFrame, QHBoxLayout, QLayout

from .event_types import DockAreaContentsChanged
from .q_bitmap_button import QBitmapButton, QCheckedBitmapButton
from .q_dock_area import QDockArea
from .q_dock_frame import QDockFrame
from .q_dock_frame_layout import QDockFrameLayout
from .xbms import (
    CLOSE_BUTTON, MAXIMIZE_BUTTON, RESTORE_BUTTON, LINKED_BUTTON,
    UNLINKED_BUTTON
)


class QDockWindowButtons(QFrame):
    """ A custom QFrame which provides the buttons for a QDockWindow.

    """
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = Signal(bool)

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = Signal(bool)

    #: A signal emitted when the close button is closed.
    closeButtonClicked = Signal(bool)

    #: A signal emitted when the link button is toggled.
    linkButtonToggled = Signal(bool)

    #: Do not show any buttons in the widget.
    NoButtons = 0x0

    #: Show the maximize button in the widget.
    MaximizeButton = 0x1

    #: Show the restore button in the widget.
    RestoreButton = 0x2

    #: Show the close button in the widget.
    CloseButton = 0x4

    #: Show the link button in the widget.
    LinkButton = 0x8

    def __init__(self, parent=None):
        """ Initialize a QDockWindowButtons instance.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the window buttons.

        """
        super(QDockWindowButtons, self).__init__(parent)
        self._buttons = (
            self.CloseButton | self.MaximizeButton | self.LinkButton
        )

        max_button = self._max_button = QBitmapButton(self)
        max_button.setObjectName('dockwindow-maximize-button')
        max_button.setBitmap(MAXIMIZE_BUTTON.toBitmap())
        max_button.setIconSize(QSize(20, 15))
        max_button.setVisible(self._buttons & self.MaximizeButton)
        max_button.setToolTip('Maximize')

        restore_button = self._restore_button = QBitmapButton(self)
        restore_button.setObjectName('dockwindow-restore-button')
        restore_button.setBitmap(RESTORE_BUTTON.toBitmap())
        restore_button.setIconSize(QSize(20, 15))
        restore_button.setVisible(self._buttons & self.RestoreButton)
        restore_button.setToolTip('Restore Down')

        close_button = self._close_button = QBitmapButton(self)
        close_button.setObjectName('dockwindow-close-button')
        close_button.setBitmap(CLOSE_BUTTON.toBitmap())
        close_button.setIconSize(QSize(34, 15))
        close_button.setVisible(self._buttons & self.CloseButton)
        close_button.setToolTip('Close')

        link_button = self._link_button = QCheckedBitmapButton(self)
        link_button.setObjectName('dockwindow-link-button')
        link_button.setBitmap(UNLINKED_BUTTON.toBitmap())
        link_button.setCheckedBitmap(LINKED_BUTTON.toBitmap())
        link_button.setIconSize(QSize(20, 15))
        link_button.setVisible(self._buttons & self.LinkButton)
        link_button.setToolTip('Link Window')
        link_button.setCheckedToolTip('Unlink Window')

        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(1)

        layout.addWidget(link_button)
        layout.addWidget(max_button)
        layout.addWidget(restore_button)
        layout.addWidget(close_button)

        self.setLayout(layout)

        max_button.clicked.connect(self.maximizeButtonClicked)
        restore_button.clicked.connect(self.restoreButtonClicked)
        close_button.clicked.connect(self.closeButtonClicked)
        link_button.toggled.connect(self.linkButtonToggled)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def buttons(self):
        """ Get the buttons to show in the title bar.

        Returns
        -------
        result : int
            An or'd combination of the buttons to show.

        """
        return self._buttons

    def setButtons(self, buttons):
        """ Set the buttons to show in the title bar.

        Parameters
        ----------
        buttons : int
            An or'd combination of the buttons to show.

        """
        self._buttons = buttons
        self._max_button.setVisible(buttons & self.MaximizeButton)
        self._restore_button.setVisible(buttons & self.RestoreButton)
        self._close_button.setVisible(buttons & self.CloseButton)
        self._link_button.setVisible(buttons & self.LinkButton)

    def isLinked(self):
        """ Get whether the link button is checked.

        Returns
        -------
        result : bool
            True if the link button is checked, False otherwise.

        """
        return self._link_button.isChecked()

    def setLinked(self, linked):
        """ Set whether or not the link button is checked.

        Parameters
        ----------
        linked : bool
            True if the link button should be checked, False otherwise.

        """
        self._link_button.setChecked(linked)


class QDockWindow(QDockFrame):
    """ A QDockFrame which holds a toplevel dock area.

    """
    #: The static resize margins for the dock window.
    ResizeMargins = QMargins(5, 5, 5, 5)

    #: The static normal contents margins for the dock window.
    NormalMargins = QMargins(5, 20, 5, 5)

    #: The static maximized margins for the dock window.
    MaximizedMargins = QMargins(0, 20, 0, 0)

    #: The minimum offset for the window buttons from the right edge.
    MinButtonOffset = 5

    class FrameState(QDockFrame.FrameState):
        """ A private class for managing window drag state.

        """
        #: The press position in the window title bar.
        press_pos = Typed(QPoint)

        #: Whether or not the window is being dragged by the user.
        dragging = Bool(False)

        #: Whether the window is inside it's close event.
        in_close_event = Bool(False)

    def __init__(self, manager, parent=None):
        """ Initialize a QDockWindow.

        Parameters
        ----------
        manager : DockManager
            The dock manager which owns the dock window.

        parent : QWidget or None
            The parent of the dock window, or None.

        """
        super(QDockWindow, self).__init__(manager, parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        layout = QDockFrameLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        layout.setContentsMargins(self.NormalMargins)
        self.setLayout(layout)
        self.setDockArea(QDockArea())
        buttons = self._title_buttons = QDockWindowButtons(self)
        buttons.maximizeButtonClicked.connect(self.showMaximized)
        buttons.restoreButtonClicked.connect(self.showNormal)
        buttons.closeButtonClicked.connect(self.close)
        buttons.linkButtonToggled.connect(self.linkButtonToggled)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def showMaximized(self):
        """ Handle a show maximized request for the window.

        """
        self.layout().setContentsMargins(self.MaximizedMargins)
        super(QDockWindow, self).showMaximized()
        title_buttons = self._title_buttons
        buttons = title_buttons.buttons()
        buttons |= title_buttons.RestoreButton
        buttons &= ~title_buttons.MaximizeButton
        buttons &= ~title_buttons.LinkButton
        title_buttons.setButtons(buttons)
        title_buttons.setLinked(False)
        self._updateButtonGeometry()

    def showNormal(self):
        """ Handle a show normal request for the window.

        """
        super(QDockWindow, self).showNormal()
        self.applyNormalState()
        self._updateButtonGeometry()

    def applyNormalState(self):
        """ Apply the proper state for normal window geometry.

        """
        self.layout().setContentsMargins(self.NormalMargins)
        title_buttons = self._title_buttons
        buttons = title_buttons.buttons()
        buttons |= title_buttons.MaximizeButton
        buttons |= title_buttons.LinkButton
        buttons &= ~title_buttons.RestoreButton
        title_buttons.setButtons(buttons)
        title_buttons.setLinked(False)

    def titleBarGeometry(self):
        """ Get the geometry rect for the title bar.

        Returns
        -------
        result : QRect
            The geometry rect for the title bar, expressed in frame
            coordinates. An invalid rect is returned if title bar
            should not be active.

        """
        cmargins = self.layout().contentsMargins()
        if self.isMaximized():
            return QRect(0, 0, self.width(), cmargins.top())
        rmargins = self.ResizeMargins
        width = self.width() - (cmargins.left() + cmargins.right())
        height = cmargins.top() - rmargins.top()
        return QRect(cmargins.left(), rmargins.top(), width, height)

    def resizeMargins(self):
        """ Get the margins to use for resizing the container.

        Returns
        -------
        result : QMargins
            The margins to use for container resizing when the container
            is a top-level window.

        """
        if self.isMaximized():
            return QMargins()
        return self.ResizeMargins

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def dockArea(self):
        """ Get the dock area installed on the container.

        Returns
        -------
        result : QDockArea or None
            The dock area installed in the container, or None.

        """
        return self.layout().getWidget()

    def setDockArea(self, dock_area):
        """ Set the dock area for the container.

        Parameters
        ----------
        dock_area : QDockArea
            The dock area to use in the container.

        """
        old = self.dockArea()
        if old is not None:
            old.removeEventFilter(self)
        self.layout().setWidget(dock_area)
        if dock_area is not None:
            dock_area.installEventFilter(self)

    def isLinked(self):
        """ Get whether or not the window is linked.

        """
        return self._title_buttons.isLinked()

    def setLinked(self, linked):
        """ Set whether or not the window is linked.

        This method should be reimplemented by a subclass.

        Parameters
        ----------
        linked : bool
            True if the window is considered linked, False otherwise.

        """
        self._title_buttons.setLinked(linked)

    def toggleMaximized(self):
        """ Toggle the maximized state of the window.

        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def eventFilter(self, area, event):
        """ Filter the events on the dock area.

        This filter listens for contents changes on the dock area and
        will close the window when the dock area is empty.

        """
        if event.type() == DockAreaContentsChanged and area.isEmpty():
            # Hide the window so that it doesn't steal events from
            # the floating window when this window is closed.
            self.hide()
            # Close the window later so that the event filter can
            # return before the child dock area is destroyed.
            QMetaObject.invokeMethod(self, 'close', Qt.QueuedConnection)
        return False

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def closeEvent(self, event):
        """ Handle a close event for the window.

        """
        # Protect against reentrency and posted contents events which
        # get delivered after the manager has already been removed.
        state = self.frame_state
        if state.in_close_event:
            return
        manager = self.manager()
        if manager is None:
            return
        state.in_close_event = True
        manager.close_window(self, event)
        state.in_close_event = False

    def resizeEvent(self, event):
        """ Handle the resize event for the dock window.

        """
        super(QDockWindow, self).resizeEvent(event)
        self._updateButtonGeometry()

    def mouseDoubleClickEvent(self, event):
        """ Handle the mouse double click event for the dock window.

        This handler will toggle the maximization of the window if the
        click occurs within the title bar.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            geo = self.titleBarGeometry()
            geo.setRight(self._title_buttons.geometry().left())
            if geo.contains(event.pos()):
                self.toggleMaximized()
                event.accept()

    def hoverMoveEvent(self, event):
        """ Handle the hover move event for the dock window.

        This reimplementation unsets the cursor when the mouse hovers
        over the dock window buttons.

        """
        if self._title_buttons.geometry().contains(event.pos()):
            self.unsetCursor()
        else:
            super(QDockWindow, self).hoverMoveEvent(event)

    def titleBarMousePressEvent(self, event):
        """ Handle the mouse press event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is None:
                state.press_pos = event.pos()
                return True
        return False

    def titleBarMouseMoveEvent(self, event):
        """ Handle the mouse move event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.frame_state
        if state.press_pos is not None:
            global_pos = event.globalPos()
            if self.isMaximized():
                coeff = state.press_pos.x() / float(self.width())
                self.showNormal()
                button_width = self._title_buttons.width()
                margins = self.layout().contentsMargins()
                max_x = self.width() - margins.right() - button_width - 5
                test_x = int(coeff * self.width())
                new_x = max(5, min(test_x, max_x))
                state.press_pos.setX(new_x)
                state.press_pos.setY(margins.top() / 2)
            target_pos = global_pos - state.press_pos
            self.manager().drag_move_frame(self, target_pos, global_pos)
            return True
        return False

    def titleBarMouseReleaseEvent(self, event):
        """ Handle the mouse release event for the dock window.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is not None:
                self.manager().drag_release_frame(self, event.globalPos())
                state.dragging = False
                state.press_pos = None
                return True
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _updateButtonGeometry(self):
        """ Update the geometry of the window buttons.

        This method will set the geometry of the window buttons
        according to the current window size.

        """
        title_buttons = self._title_buttons
        size = title_buttons.minimumSizeHint()
        margins = self.layout().contentsMargins()
        offset = max(self.MinButtonOffset, margins.right())
        x = self.width() - size.width() - offset
        rect = QRect(x, 1, size.width(), size.height())
        title_buttons.setGeometry(rect)
