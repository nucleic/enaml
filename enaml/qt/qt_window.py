#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.layout.geometry import Pos, Rect, Size
from enaml.widgets.window import ProxyWindow

from .QtCore import Qt, QPoint, QRect, QSize, Signal
from .QtGui import QApplication, QFrame, QLayout, QIcon

from .q_resource_helpers import get_cached_qicon
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


MODALITY = {
    'non_modal': Qt.NonModal,
    'application_modal': Qt.ApplicationModal,
    'window_modal': Qt.WindowModal,
}


class QWindowLayout(QSingleWidgetLayout):
    """ A QSingleWidgetLayout subclass which adds support for windows
    which explicitly set their minimum and maximum sizes.

    """
    def minimumSize(self):
        """ The minimum size for the layout area.

        This is a reimplemented method which will return the explicit
        minimum size of the window, if provided.

        """
        parent = self.parentWidget()
        if parent is not None:
            size = parent.explicitMinimumSize()
            if size.isValid():
                return size
        return super(QWindowLayout, self).minimumSize()

    def maximumSize(self):
        """ The maximum size for the layout area.

        This is a reimplemented method which will return the explicit
        maximum size of the window, if provided.

        """
        parent = self.parentWidget()
        if parent is not None:
            size = parent.explicitMaximumSize()
            if size.isValid():
                return size
        return super(QWindowLayout, self).maximumSize()


class QWindow(QFrame):
    """ A custom QFrame which uses a QWindowLayout to manage its
    central widget.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """
    #: A signal emitted when the window is closed.
    closed = Signal()

    def __init__(self, parent=None):
        """ Initialize a QWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QFrame.

        """
        super(QWindow, self).__init__(parent, Qt.Window)
        self._central_widget = None
        self._expl_min_size = QSize()
        self._expl_max_size = QSize()
        layout = QWindowLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

    def closeEvent(self, event):
        """ Handle the QCloseEvent from the window system.

        By default, this handler calls the superclass' method to close
        the window and then emits the 'closed' signal.

        """
        super(QWindow, self).closeEvent(event)
        self.closed.emit()

    def centralWidget(self):
        """ Returns the central widget for the window.

        Returns
        -------
        result : QWidget or None
            The central widget of the window, or None if no widget
            was provided.

        """
        return self._central_widget

    def setCentralWidget(self, widget):
        """ Set the central widget for this window.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the content of the window.

        """
        self._central_widget = widget
        self.layout().setWidget(widget)

    def explicitMinimumSize(self):
        """ Return the explicit minimum size for this widget.

        Returns
        -------
        result : QSize
            If the user has explitly set the minimum size of the
            widget, that size will be returned. Otherwise, an
            invalid QSize will be returned.

        """
        return self._expl_min_size

    def explicitMaximumSize(self):
        """ Return the explicit maximum size for this widget.

        Returns
        -------
        result : QSize
            If the user has explitly set the maximum size of the
            widget, that size will be returned. Otherwise, an
            invalid QSize will be returned.

        """
        return self._expl_max_size

    def setMinimumSize(self, size):
        """ Set the minimum size for the QWindow.

        This is an overridden parent class method which stores the
        provided size as the explictly set QSize. The explicit
        size can be reset by passing a QSize of (0, 0).

        Parameters
        ----------
        size : QSize
            The minimum size for the QWindow.

        """
        super(QWindow, self).setMinimumSize(size)
        if size == QSize(0, 0):
            self._expl_min_size = QSize()
        else:
            self._expl_min_size = size
        self.layout().update()

    def setMaximumSize(self, size):
        """ Set the maximum size for the QWindow.

        This is an overridden parent class method which stores the
        provided size as the explictly set QSize. The explicit
        size can be reset by passing a QSize equal to the maximum
        widget size of QSize(16777215, 16777215).

        Parameters
        ----------
        size : QSize
            The maximum size for the QWindow.

        """
        super(QWindow, self).setMaximumSize(size)
        if size == QSize(16777215, 16777215):
            self._expl_max_size = QSize()
        else:
            self._expl_max_size = size
        self.layout().update()


class QtWindow(QtWidget, ProxyWindow):
    """ A Qt implementation of an Enaml ProxyWindow.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QWindow widget.

        """
        self.widget = QWindow(self.parent_widget())

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

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.showMinimized()

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
