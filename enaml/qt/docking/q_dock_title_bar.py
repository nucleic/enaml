#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import str
from enaml.qt.QtCore import Qt, QSize, QPoint, QMargins, Signal
from enaml.qt.QtWidgets import (
    QWidget, QFrame, QLineEdit, QHBoxLayout, QSizePolicy
)

from .q_bitmap_button import QBitmapButton, QCheckedBitmapButton
from .q_icon_widget import QIconWidget
from .q_text_label import QTextLabel
from .xbms import (
    CLOSE_BUTTON, MAXIMIZE_BUTTON, RESTORE_BUTTON, LINKED_BUTTON,
    UNLINKED_BUTTON, PIN_BUTTON, UNPIN_BUTTON
)


class IDockTitleBar(QWidget):
    """ An interface class for defining a title bar.

    """
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = Signal(bool)

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = Signal(bool)

    #: A signal emitted when the close button is clicked.
    closeButtonClicked = Signal(bool)

    #: A signal emitted when the link button is toggled.
    linkButtonToggled = Signal(bool)

    #: A signal emitted when the pin button is toggled.
    pinButtonToggled = Signal(bool)

    #: A signal emitted when the title is edited by the user.
    titleEdited = Signal(str)

    #: A signal emitted when the title bar is left double clicked.
    leftDoubleClicked = Signal(QPoint)

    #: A signal emitted when the title bar is right clicked.
    rightClicked = Signal(QPoint)

    #: Do not show any buttons in the title bar.
    NoButtons = 0x0

    #: Show the maximize button in the title bar.
    MaximizeButton = 0x1

    #: Show the restore button in the title bar.
    RestoreButton = 0x2

    #: Show the close button in the title bar.
    CloseButton = 0x4

    #: Show the link button in the title bar.
    LinkButton = 0x8

    #: Show the pin button in the title bar.
    PinButton = 0x10

    def buttons(self):
        """ Get the buttons to show in the title bar.

        Returns
        -------
        result : int
            An or'd combination of the buttons to show.

        """
        raise NotImplementedError

    def setButtons(self, buttons):
        """ Set the buttons to show in the title bar.

        Parameters
        ----------
        buttons : int
            An or'd combination of the buttons to show.

        """
        raise NotImplementedError

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

    def label(self):
        """ Get the label for the title bar.

        Returns
        -------
        result : QTextLabel
            The label for the title bar.

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

    def isLinked(self):
        """ Get whether the link button is checked.

        Returns
        -------
        result : bool
            True if the link button is checked, False otherwise.

        """
        raise NotImplementedError

    def setLinked(self, linked):
        """ Set whether or not the link button is checked.

        Parameters
        ----------
        linked : bool
            True if the link button should be checked, False otherwise.

        """
        raise NotImplementedError

    def isPinned(self):
        """ Get whether the pin button is checked.

        Returns
        -------
        result : bool
            True if the pin button is checked, False otherwise.

        """
        raise NotImplementedError

    def setPinned(self, pinned, quiet=False):
        """ Set whether or not the pin button is checked.

        Parameters
        ----------
        pinned : bool
            True if the pin button should be checked, False otherwise.

        quiet : bool, optional
            True if the state should be set without emitted the toggled
            signal. The default is False.

        """
        raise NotImplementedError

    def isEditable(self):
        """ Get whether the title is user editable.

        Returns
        -------
        result : bool
            True if the title is user editable, False otherwise.

        """
        raise NotImplementedError

    def setEditable(self, editable):
        """ Set whether or not the title is user editable.

        Parameters
        ----------
        editable : bool
            True if the title is user editable, False otherwise.

        """
        raise NotImplementedError

    def isForceHidden(self):
        """ Get whether or not the title bar is force hidden.

        Returns
        -------
        result : bool
            Whether or not the title bar is force hidden.

        """
        raise NotImplementedError

    def setForceHidden(self, hidden):
        """ Set the force hidden state of the title bar.

        Parameters
        ----------
        hidden : bool
            True if the title bar should be hidden, False otherwise.

        """
        raise NotImplementedError


class QDockTitleBar(QFrame, IDockTitleBar):
    """ A concrete implementation of IDockTitleBar.

    This class serves as the default title bar for a QDockItem.

    """
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = Signal(bool)

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = Signal(bool)

    #: A signal emitted when the close button is clicked.
    closeButtonClicked = Signal(bool)

    #: A signal emitted when the link button is toggled.
    linkButtonToggled = Signal(bool)

    #: A signal emitted when the pin button is toggled.
    pinButtonToggled = Signal(bool)

    #: A signal emitted when the title is edited by the user.
    titleEdited = Signal(str)

    #: A signal emitted when the empty area is left double clicked.
    leftDoubleClicked = Signal(QPoint)

    #: A signal emitted when the empty area is right clicked.
    rightClicked = Signal(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockTitleBar, self).__init__(parent)
        self._buttons = self.CloseButton | self.MaximizeButton | self.PinButton
        self._is_editable = False
        self._force_hidden = False
        self._last_visible = True
        self._line_edit = None

        title_icon = self._title_icon = QIconWidget(self)
        title_icon.setVisible(False)

        title_label = self._title_label = QTextLabel(self)

        spacer = self._spacer = QWidget(self)
        policy = spacer.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        spacer.setSizePolicy(policy)

        btn_size = QSize(14, 13)

        max_button = self._max_button = QBitmapButton(self)
        max_button.setObjectName('docktitlebar-maximize-button')
        max_button.setBitmap(MAXIMIZE_BUTTON.toBitmap())
        max_button.setIconSize(btn_size)
        max_button.setVisible(self._buttons & self.MaximizeButton)
        max_button.setToolTip('Maximize')

        restore_button = self._restore_button = QBitmapButton(self)
        restore_button.setObjectName('docktitlebar-restore-button')
        restore_button.setBitmap(RESTORE_BUTTON.toBitmap())
        restore_button.setIconSize(btn_size)
        restore_button.setVisible(self._buttons & self.RestoreButton)
        restore_button.setToolTip('Restore Down')

        close_button = self._close_button = QBitmapButton(self)
        close_button.setObjectName('docktitlebar-close-button')
        close_button.setBitmap(CLOSE_BUTTON.toBitmap())
        close_button.setIconSize(btn_size)
        close_button.setVisible(self._buttons & self.CloseButton)
        close_button.setToolTip('Close')

        link_button = self._link_button = QCheckedBitmapButton(self)
        link_button.setObjectName('docktitlebar-link-button')
        link_button.setBitmap(UNLINKED_BUTTON.toBitmap())
        link_button.setCheckedBitmap(LINKED_BUTTON.toBitmap())
        link_button.setIconSize(btn_size)
        link_button.setVisible(self._buttons & self.LinkButton)
        link_button.setToolTip('Link Window')
        link_button.setCheckedToolTip('Unlink Window')

        pin_button = self._pin_button = QCheckedBitmapButton(self)
        pin_button.setObjectName('docktitlebar-pin-button')
        pin_button.setBitmap(PIN_BUTTON.toBitmap())
        pin_button.setCheckedBitmap(UNPIN_BUTTON.toBitmap())
        pin_button.setIconSize(QSize(13, 13))
        pin_button.setVisible(self._buttons & self.PinButton)
        pin_button.setToolTip('Pin Window')
        pin_button.setCheckedToolTip('Unpin Window')

        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(5, 2, 5, 2))
        layout.setSpacing(1)
        layout.addWidget(title_icon)
        layout.addSpacing(0)
        layout.addWidget(title_label)
        layout.addWidget(spacer)
        layout.addSpacing(4)
        layout.addWidget(pin_button)
        layout.addWidget(link_button)
        layout.addWidget(max_button)
        layout.addWidget(restore_button)
        layout.addWidget(close_button)

        self.setLayout(layout)

        max_button.clicked.connect(self.maximizeButtonClicked)
        restore_button.clicked.connect(self.restoreButtonClicked)
        close_button.clicked.connect(self.closeButtonClicked)
        link_button.toggled.connect(self.linkButtonToggled)
        pin_button.toggled.connect(self.pinButtonToggled)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """ Handle the mouse double click event for the title bar.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            is_editable = self._is_editable
            if self._adjustedLabelGeometry().contains(pos) and is_editable:
                self._showTitleLineEdit()
                event.accept()
                return
            if self._clickableGeometry().contains(pos):
                self.leftDoubleClicked.emit(event.globalPos())
                event.accept()
                return

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the title bar.

        """
        event.ignore()
        if event.button() == Qt.RightButton:
            if self._clickableGeometry().contains(event.pos()):
                self.rightClicked.emit(event.globalPos())
                event.accept()
                return

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def setVisible(self, visible):
        """ An overridden virtual visibility setter.

        This handler enforces the force-hidden setting.

        """
        self._last_visible = visible
        if visible and self._force_hidden:
            return
        super(QDockTitleBar, self).setVisible(visible)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _adjustedLabelGeometry(self):
        """ Get the adjust label geometry.

        Returns
        -------
        result : QRect
            A rectangle representing the label geometry which has been
            adjusted for potentially empty text. This rect can be used
            for a usable hit-testing rect for the label text.

        """
        label = self._title_label
        label_geo = label.geometry()
        if not label.text():
            label_geo = label_geo.adjusted(0, 0, 10, 0)
        return label_geo

    def _clickableGeometry(self):
        """ Get the geometry rect which represents clickable area.

        Returns
        -------
        result : QRect
            A rectangle adjusted for the clickable geometry.

        """
        rect = self.rect().adjusted(5, 2, -5, -2)
        rect.setRight(self._spacer.geometry().right())
        return rect

    def _showTitleLineEdit(self):
        """ Setup the line edit widget for editing the title.

        """
        old_line_edit = self._line_edit
        if old_line_edit is not None:
            old_line_edit.hide()
            old_line_edit.deleteLater()
        line_edit = self._line_edit = QLineEdit(self)
        line_edit.setFrame(False)
        line_edit.setText(self._title_label.text())
        line_edit.selectAll()
        h = self._title_label.height()
        line_edit.setMinimumHeight(h)
        line_edit.setMaximumHeight(h)
        line_edit.editingFinished.connect(self._onEditingFinished)
        layout = self.layout()
        idx = layout.indexOf(self._spacer)
        layout.insertWidget(idx, line_edit)
        self._spacer.hide()
        self._title_label.hide()
        line_edit.show()
        line_edit.setFocus(Qt.MouseFocusReason)

    def _onEditingFinished(self):
        """ Handle the 'editingFinished' signal for title line edit.

        """
        line_edit = self._line_edit
        if line_edit is not None:
            text = line_edit.text()
            line_edit.hide()
            line_edit.deleteLater()
            self._line_edit = None
            changed = self._title_label.text() != text
            if changed:
                self._title_label.setText(text)
            self._title_label.show()
            self._spacer.show()
            if changed:
                self.titleEdited.emit(text)

    #--------------------------------------------------------------------------
    # IDockItemTitleBar API
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
        self._pin_button.setVisible(buttons & self.PinButton)

    def title(self):
        """ Get the title string of the title bar.

        Returns
        -------
        result : unicode
            The unicode title string for the title bar.

        """
        return self._title_label.text()

    def setTitle(self, title):
        """ Set the title string of the title bar.

        Parameters
        ----------
        title : unicode
            The unicode string to use for the title bar.

        """
        self._title_label.setText(title)

    def label(self):
        """ Get the label which holds the title string.

        Returns
        -------
        result : QTextLabel
            The label widget which holds the title string.

        """
        return self._title_label

    def icon(self):
        """ Get the icon for the title bar.

        Returns
        -------
        result : QIcon
            The icon set for the title bar.

        """
        return self._title_icon.icon()

    def setIcon(self, icon):
        """ Set the icon for the title bar.

        Parameters
        ----------
        icon : QIcon
            The icon to use for the title bar.

        """
        visible, spacing = (False, 0) if icon.isNull() else (True, 4)
        title_icon = self._title_icon
        title_icon.setIcon(icon)
        title_icon.setVisible(visible)
        layout = self.layout()
        layout.takeAt(1)
        layout.insertSpacing(1, spacing)

    def iconSize(self):
        """ Get the icon size for the title bar.

        Returns
        -------
        result : QSize
            The size to use for the icons in the title bar.

        """
        return self._title_icon.iconSize()

    def setIconSize(self, size):
        """ Set the icon size for the title bar.

        Parameters
        ----------
        icon : QSize
            The icon size to use for the title bar. Icons smaller than
            this size will not be scaled up.

        """
        self._title_icon.setIconSize(size)

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

    def isPinned(self):
        """ Get whether the pin button is checked.

        Returns
        -------
        result : bool
            True if the pin button is checked, False otherwise.

        """
        return self._pin_button.isChecked()

    def setPinned(self, pinned, quiet=False):
        """ Set whether or not the pin button is checked.

        Parameters
        ----------
        pinned : bool
            True if the pin button should be checked, False otherwise.

        quiet : bool, optional
            True if the state should be set without emitted the toggled
            signal. The default is False.

        """
        old = self._pin_button.blockSignals(quiet)
        self._pin_button.setChecked(pinned)
        self._pin_button.blockSignals(old)

    def isEditable(self):
        """ Get whether the title is user editable.

        Returns
        -------
        result : bool
            True if the title is user editable, False otherwise.

        """
        return self._is_editable

    def setEditable(self, editable):
        """ Set whether or not the title is user editable.

        Parameters
        ----------
        editable : bool
            True if the title is user editable, False otherwise.

        """
        self._is_editable = editable

    def isForceHidden(self):
        """ Get whether or not the title bar is force hidden.

        Returns
        -------
        result : bool
            Whether or not the title bar is always hidden.

        """
        return self._force_hidden

    def setForceHidden(self, hidden):
        """ Set the force hidden state of the title bar.

        Parameters
        ----------
        hidden : bool
            True if the title bar should be hidden, False otherwise.

        """
        self._force_hidden = hidden
        if not hidden and self._last_visible:
            super(QDockTitleBar, self).setVisible(True)
        elif hidden:
            super(QDockTitleBar, self).setVisible(False)
