#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QSize, QMargins, pyqtSignal
from PyQt4.QtGui import QWidget, QFrame, QHBoxLayout, QIcon

from .q_icon_button import QIconButton
from .q_icon_widget import QIconWidget
from .q_text_label import QTextLabel

# Make sure the resources get registered.
from . import dock_resources


class IDockTitleBar(QWidget):
    """ An interface class for defining a title bar.

    """
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = pyqtSignal()

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = pyqtSignal()

    #: A signal emitted when the close button is clicked.
    closeButtonClicked = pyqtSignal()

    #: Do not show any buttons in the title bar.
    NoButtons = 0x0

    #: Show the maximize button in the title bar.
    MaximizeButton = 0x1

    #: Show the restore button in the title bar.
    RestoreButton = 0x2

    #: Show the close button in the title bar.
    CloseButton = 0x4

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
    #: A signal emitted when the maximize button is clicked.
    maximizeButtonClicked = pyqtSignal()

    #: A signal emitted when the restore button is clicked.
    restoreButtonClicked = pyqtSignal()

    #: A signal emitted when the close button is clicked.
    closeButtonClicked = pyqtSignal()

    def __init__(self, parent=None):
        """ Initialize a QDockTitleBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the title bar.

        """
        super(QDockTitleBar, self).__init__(parent)
        self._buttons = self.CloseButton

        title_icon = self._title_icon = QIconWidget(self)
        title_icon.setVisible(False)

        title_label = self._title_label = QTextLabel(self)

        max_icon = QIcon()
        max_icon.addFile(':dock_images/maxbtn_s.png')
        max_icon.addFile(':dock_images/maxbtn_h.png', mode=QIcon.Active)
        max_icon.addFile(':dock_images/maxbtn_p.png', mode=QIcon.Selected)

        restore_icon = QIcon()
        restore_icon.addFile(':dock_images/rstrbtn_s.png')
        restore_icon.addFile(':dock_images/rstrbtn_h.png', mode=QIcon.Active)
        restore_icon.addFile(':dock_images/rstrbtn_p.png', mode=QIcon.Selected)

        close_icon = QIcon()
        close_icon.addFile(':dock_images/closebtn_s.png')
        close_icon.addFile(':dock_images/closebtn_h.png', mode=QIcon.Active)
        close_icon.addFile(':dock_images/closebtn_p.png', mode=QIcon.Selected)

        btn_size = QSize(14, 13)

        max_button = self._max_button = QIconButton(self)
        max_button.setIcon(max_icon)
        max_button.setIconSize(btn_size)
        max_button.setVisible(self._buttons & self.MaximizeButton)

        restore_button = self._restore_button = QIconButton(self)
        restore_button.setIcon(restore_icon)
        restore_button.setIconSize(btn_size)
        restore_button.setVisible(self._buttons & self.RestoreButton)

        close_button = self._close_button = QIconButton(self)
        close_button.setIcon(close_icon)
        close_button.setIconSize(btn_size)
        close_button.setVisible(self._buttons & self.CloseButton)

        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(1)

        layout.addWidget(title_icon)
        layout.addSpacing(0)
        layout.addWidget(title_label, 1)
        layout.addSpacing(4)
        layout.addWidget(max_button)
        layout.addWidget(restore_button)
        layout.addWidget(close_button)

        self.setContentsMargins(QMargins(5, 2, 5, 2))
        self.setLayout(layout)

        max_button.clicked.connect(self.maximizeButtonClicked)
        restore_button.clicked.connect(self.restoreButtonClicked)
        close_button.clicked.connect(self.closeButtonClicked)

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
