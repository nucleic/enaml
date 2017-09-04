#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed, atomref

from enaml.layout.geometry import Pos, Rect, Size
from enaml.widgets.window import ProxyWindow, CloseEvent

from .QtCore import Qt, QPoint, QRect, QSize
from .QtGui import QIcon
from .QtWidgets import QApplication

from .q_deferred_caller import deferredCall
from .q_resource_helpers import get_cached_qicon
from .q_window_base import QWindowBase
from .qt_container import QtContainer
from .qt_widget import QtWidget


MODALITY = {
    'non_modal': Qt.NonModal,
    'application_modal': Qt.ApplicationModal,
    'window_modal': Qt.WindowModal,
}


def finalize_close(d):
    """ Finalize the closing of the declaration object.

    This is performed as a deferred call so that the window may fully
    close before the declaration is potentially destroyed.

    """
    d.visible = False
    d.closed()
    if d.destroy_on_close:
        d.destroy()


class QWindow(QWindowBase):
    """ A window base subclass which handles the close event.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """
    def __init__(self, proxy, parent=None, flags=Qt.Widget):
        """ Initialize a QWindow.

        Parameters
        ----------
        proxy : QtWindow
            The proxy object which owns this window. Only an atomref
            will be maintained to this object.

        parent : QWidget, optional
            The parent of the window.

        flags : Qt.WindowFlags, optional
            The window flags to pass to the parent constructor.

        """
        super(QWindow, self).__init__(parent, Qt.Window | flags)
        self._proxy_ref = atomref(proxy)

    def closeEvent(self, event):
        """ Handle the close event for the window.

        """
        event.accept()
        if not self._proxy_ref:
            return
        proxy = self._proxy_ref()
        d = proxy.declaration
        d_event = CloseEvent()
        d.closing(d_event)
        if d_event.is_accepted():
            deferredCall(finalize_close, d)
        else:
            event.ignore()


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
        self.widget = QWindow(self, self.parent_widget(), flags)

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
