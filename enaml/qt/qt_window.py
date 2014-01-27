#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed

from enaml.layout.geometry import Pos, Rect, Size
from enaml.widgets.window import ProxyWindow

from .QtCore import Qt, QPoint, QRect, QSize, Signal
from .QtGui import QApplication, QIcon

from .q_resource_helpers import get_cached_qicon
from .q_window_base import QWindowBase
from .qt_container import QtContainer
from .qt_widget import QtWidget


MODALITY = {
    'non_modal': Qt.NonModal,
    'application_modal': Qt.ApplicationModal,
    'window_modal': Qt.WindowModal,
}


class QWindow(QWindowBase):
    """ A window base subclass which handles the close event.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """

    #: A signal which is emitted when the user ask to close the window.
    #: It is then up to the declaration to validate or not this request.
    closing = Signal()    
    
    def __init__(self, parent=None):
        """ Initialize a QWindow.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the window.

        """
        super(QWindow, self).__init__(parent, Qt.Window)
        self.closing_requested = False

    def closeEvent(self, event):
        """ Handle the QCloseEvent from the window system.

        If no previous QCloseEvent is registered emit the closing signal.
        Otherwise calls the superclass' method to close the window and then
        emits the 'closed' signal.

        """
        if not self.closing_requested:
            self.closing_requested = True
            event.ignore()
            self.closing.emit()
        else:
            super(QWindow, self).closeEvent(event)
            self.closed.emit()


class QtWindow(QtWidget, ProxyWindow):
    """ A Qt implementation of an Enaml ProxyWindow.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def creation_flags(self):
        """ A convenience function for getting the creation flags.

        """
        flags = Qt.Widget
        if self.declaration.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        return flags

    def create_widget(self):
        """ Create the QWindow widget.

        """
        flags = self.creation_flags()
        self.widget = QWindow(self.parent_widget(), flags)

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtWindow, self).init_widget()
        d = self.declaration
        if d.title:
            self.set_title(d.title)
        if -1 not in d.initial_size:
            self.widget.resize(*d.initial_size)
        if -1 not in d.initial_position:
            self.widget.move(*d.initial_position)
        if d.modality != 'non_modal':
            self.set_modality(d.modality)
        if d.icon:
            self.set_icon(d.icon)
        self.widget.closed.connect(self.on_closed)
        self.widget.closing.connect(self.on_closing)

    def init_layout(self):
        """ Initialize the widget layout.

        """
        super(QtWindow, self).init_layout()
        self.widget.setCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Find and return the central widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The central widget defined for this widget, or None if one
            is not defined.

        """
        d = self.declaration.central_widget()
        if d is not None:
            return d.proxy.widget

    def on_closing(self):
        """The signal handler for the 'closing' signal.

        This method will call the validate_close function on the 
        declaration.
        
        """ 
        if self.declaration._handle_closing():
            self.widget.close()
        else:
            self.widget.closing_requested = False

    def on_closed(self):
        """ The signal handler for the 'closed' signal.

        This method will fire the 'closed' event on the declaration.

        """
        self.declaration._handle_close()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtWindow.

        """
        super(QtWindow, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setCentralWidget(self.central_widget())

    def child_removed(self, child):
        """ Handle the child added event for a QtWindow.

        """
        super(QtWindow, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # ProxyWindow API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.setWindowTitle(title)

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        self.widget.setWindowModality(MODALITY[modality])

    def set_icon(self, icon):
        """ Set the window icon.

        """
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setWindowIcon(qicon)

    def position(self):
        """ Get the position of the of the window.

        """
        point = self.widget.pos()
        return Pos(point.x(), point.y())

    def set_position(self, pos):
        """ Set the position of the window.

        """
        self.widget.move(*pos)

    def size(self):
        """ Get the size of the window.

        """
        size = self.widget.size()
        return Size(size.width(), size.height())

    def set_size(self, size):
        """ Set the size of the window.

        """
        size = QSize(*size)
        if size.isValid():
            self.widget.resize(size)

    def geometry(self):
        """ Get the geometry of the window.

        """
        rect = self.widget.geometry()
        return Rect(rect.x(), rect.y(), rect.width(), rect.height())

    def set_geometry(self, rect):
        """ Set the geometry of the window.

        """
        rect = QRect(*rect)
        if rect.isValid():
            self.widget.setGeometry(rect)

    def frame_geometry(self):
        """ Get the geometry of the window.

        """
        rect = self.widget.frameGeometry()
        return Rect(rect.x(), rect.y(), rect.width(), rect.height())

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.showMaximized()

    def is_maximized(self):
        """ Get whether the window is maximized.

        """
        return bool(self.widget.windowState() & Qt.WindowMaximized)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.showMinimized()

    def is_minimized(self):
        """ Get whether the window is minimized.

        """
        return bool(self.widget.windowState() & Qt.WindowMinimized)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.showNormal()

    def send_to_front(self):
        """ Move the window to the top of the Z order.

        """
        self.widget.raise_()

    def send_to_back(self):
        """ Move the window to the bottom of the Z order.

        """
        self.widget.lower()

    def activate_window(self):
        """ Activate the underlying window widget.

        """
        self.widget.activateWindow()
        if sys.platform == 'win32':
            # For some reason, this needs to be called twice on Windows
            # in order to get the taskbar entry to flash.
            self.widget.activateWindow()

    def center_on_screen(self):
        """ Center the window on the screen.

        """
        widget = self.widget
        rect = QRect(QPoint(0, 0), widget.frameGeometry().size())
        geo = QApplication.desktop().screenGeometry(widget)
        widget.move(geo.center() - rect.center())

    def center_on_widget(self, other):
        """ Center the window on another widget.

        """
        widget = self.widget
        rect = QRect(QPoint(0, 0), widget.frameGeometry().size())
        other_widget = other.proxy.widget
        if other_widget.isWindow():
            geo = other_widget.frameGeometry()
        else:
            size = other_widget.size()
            point = other_widget.mapToGlobal(QPoint(0, 0))
            geo = QRect(point, size)
        widget.move(geo.center() - rect.center())

    def close(self):
        """ Close the window.

        """
        self.widget.close()
