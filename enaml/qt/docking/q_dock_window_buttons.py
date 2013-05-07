#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPainter, QImage, QFrame, QCursor

from atom.api import Atom, Bool, Int, Value

# Make sure the resources get registered.
from . import dock_resources


class QDockWindowButtons(QFrame):
    """ A custom QFrame which manages the buttons for a QDockWindow.

    """
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = pyqtSignal()

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = pyqtSignal()

    #: A signal emitted when the close button is closed.
    closeButtonClicked = pyqtSignal()

    class WindowButtonState(Atom):
        """ A private class which manages the object state.

        """
        #: Whether or not the left image is pressed.
        left_pressed = Bool(False)

        #: Whether or not the right image is pressed.
        right_pressed = Bool(False)

        #: Whether or not the buttons are in maximized mode.
        maximized = Bool(False)

    class ButtonImages(Atom):
        """ A private class for managing the button images.

        """
        #: The default button image.
        Default = 0

        #: The left hover button image.
        LeftHover = 1

        #: The right hover button image.
        RightHover = 2

        #: The left press button image.
        LeftPress = 3

        #: The right press button image.
        RightPress = 4

        #: The array offset to use when the buttons are maximized.
        #: This is intended for internal use only.
        Maximized = 5

        #: The array offset for the active button image.
        active = Int(Default)

        #: The images used to render the buttons.
        images = Value(factory=lambda: [
            QImage(':dock_images/winbtns_std.png'),
            QImage(':dock_images/winbtns_stdhl.png'),
            QImage(':dock_images/winbtns_stdhr.png'),
            QImage(':dock_images/winbtns_stdpl.png'),
            QImage(':dock_images/winbtns_stdpr.png'),
            QImage(':dock_images/winbtns_rstr.png'),
            QImage(':dock_images/winbtns_rstrhl.png'),
            QImage(':dock_images/winbtns_rstrhr.png'),
            QImage(':dock_images/winbtns_rstrpl.png'),
            QImage(':dock_images/winbtns_rstrpr.png'),
        ])

    def __init__(self, parent=None):
        """ Initialize a QDockWindowButtons instance.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the window buttons.

        """
        super(QDockWindowButtons, self).__init__(parent)
        self.setMouseTracking(True)
        self._buttons = self.ButtonImages()
        self._state = self.WindowButtonState()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def isMaximized(self):
        """ Get whether the buttons are in maximized mode.

        """
        return self._state.maximized

    def setMaximized(self, maximized):
        """ Set whether the buttons are in maximized mode.

        Parameters
        ----------
        maximized : bool
            Whether or not the buttons should be in maximized mode.

        """
        state = self._state
        if maximized != state.maximized:
            state.maximized = maximized
            pos = self.mapFromGlobal(QCursor.pos())
            self.hoverButtons(pos)

    def hoverButtons(self, pos):
        """ Update the buttons for a hovered position.

        Parameters
        ----------
        pos : QPoint
            The position of interest, expressed in local coordinates.

        """
        buttons = self._buttons
        if self.rect().contains(pos):
            left = pos.x() < (self.width() - pos.x())
            active = buttons.LeftHover if left else buttons.RightHover
        else:
            active = buttons.Default
        if buttons.active != active:
            buttons.active = active
            self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Get the size hint for the window buttons.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the window buttons.

        """
        buttons = self._buttons
        return buttons.images[buttons.Default].size()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def leaveEvent(self, event):
        """ Handle the leave event for the buttons.

        """
        buttons = self._buttons
        if buttons.active != buttons.Default:
            buttons.active = buttons.Default
            self.update()

    def hideEvent(self, event):
        """ Handle the hide event for the buttons.

        """
        buttons = self._buttons
        buttons.active = buttons.Default

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the buttons.

        """
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            state = self._state
            buttons = self._buttons
            if self.rect().contains(pos):
                left = pos.x() < (self.width() - pos.x())
                state.left_pressed = left
                state.right_pressed = not left
                active = buttons.LeftPress if left else buttons.RightPress
            else:
                state.left_pressed = False
                state.right_pressed = False
                active = buttons.Default
            if active != buttons.active:
                buttons.active = active
                self.update()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the buttons.

        """
        state = self._state
        if not state.left_pressed and not state.right_pressed:
            self.hoverButtons(event.pos())
            return
        pos = event.pos()
        btns = self._buttons
        if self.rect().contains(pos):
            left = pos.x() < (self.width() - pos.x())
            if state.left_pressed:
                active = btns.LeftPress if left else btns.LeftHover
            else:
                active = btns.RightPress if not left else btns.RightHover
        else:
            active = btns.LeftHover if state.left_pressed else btns.RightHover
        if active != btns.active:
            btns.active = active
            self.update()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the buttons.

        """
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            state = self._state
            if self.rect().contains(pos):
                left = pos.x() < (self.width() - pos.x())
                if left and state.left_pressed:
                    if state.maximized:
                        self.restoreButtonClicked.emit()
                    else:
                        self.maximizeButtonClicked.emit()
                elif not left and state.right_pressed:
                    self.closeButtonClicked.emit()
            state.left_pressed = False
            state.right_pressed = False
            pos = self.mapFromGlobal(QCursor.pos())
            self.hoverButtons(pos)

    def paintEvent(self, event):
        """ Handle the paint event for the buttons.

        """
        super(QDockWindowButtons, self).paintEvent(event)
        painter = QPainter(self)
        buttons = self._buttons
        target = buttons.active
        if self._state.maximized:
            target += buttons.Maximized
        image = buttons.images[target]
        painter.drawImage(self.rect(), image)
