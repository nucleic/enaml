#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from .qt.QtCore import Qt, QSize, Signal
from .qt.QtGui import QFrame, QLayout, QIcon, QImage, QPixmap
from .q_deferred_caller import deferredCall
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


logger = logging.getLogger(__name__)


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


class QtWindow(QtWidget):
    """ A Qt implementation of an Enaml Window.

    """
    #: Temporary internal storage for the icon source url.
    _icon_source = ''

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QWindow object.

        """
        return QWindow(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtWindow, self).create(tree)
        self.set_title(tree['title'])
        self.set_initial_size(tree['initial_size'])
        self.set_modality(tree['modality'])
        self._icon_source = tree['icon_source']
        self.widget().closed.connect(self.on_closed)

    def init_layout(self):
        """ Perform layout initialization for the control.

        """
        super(QtWindow, self).init_layout()
        self.widget().setCentralWidget(self.central_widget())

    def activate(self):
        """ Activate the window.

        """
        self.set_icon_source(self._icon_source)
        super(QtWindow, self).activate()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Find and return the central widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The central widget defined for this widget, or None if one
            is not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, QtContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtWindow.

        """
        if isinstance(child, QtContainer):
            self.widget().setCentralWidget(self.central_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtWindow.

        """
        if isinstance(child, QtContainer):
            self.widget().setCentralWidget(self.central_widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_closed(self):
        """ The signal handler for the 'closed' signal.

        """
        self.send_action('closed', {})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.close()

    def on_action_maximize(self, content):
        """ Handle the 'maximize' action from the Enaml widget.

        """
        self.maximize()

    def on_action_minimize(self, content):
        """ Handle the 'minimize' action from the Enaml widget.

        """
        self.minimize()

    def on_action_restore(self, content):
        """ Handle the 'restore' action from the Enaml widget.

        """
        self.restore()

    def on_action_set_icon_source(self, content):
        """ Handle the 'set_icon_source' action from the Enaml widget.

        """
        self.set_icon_source(content['icon_source'])

    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_modality(self, content):
        """ Handle the 'set_modality' action from the Enaml widget.

        """
        self.set_modality(content['modality'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget().close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget().showMaximized()

    def minimize(self):
        """ Minimize the window.

        """
        self.widget().showMinimized()

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget().showNormal()

    def set_icon_source(self, icon_source):
        """ Set the window icon source.

        """
        if icon_source:
            loader = self._session.load_resource(icon_source)
            loader.on_load(self._on_icon_load)
        else:
            self._on_icon_load(QIcon())

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget().setWindowTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        if -1 in size:
            return
        self.widget().resize(QSize(*size))

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        self.widget().setWindowModality(MODALITY[modality])

    def set_visible(self, visible):
        """ Set the visibility on the window.

        This is an overridden parent class method to set the visibility
        at a later time, so that layout can be initialized before the
        window is displayed.

        """
        # XXX this could be done better.
        deferredCall(super(QtWindow, self).set_visible, visible)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_icon_load(self, icon):
        """ A private resource loader callback.

        This method is invoked when the requested icon is successfully
        loaded. It will update the icon on the action and issue a size
        hint updated event to the layout system if needed.

        Parameters
        ----------
        icon : QIcon or QImage
            The icon or image that was loaded by the request.

        """
        if isinstance(icon, QImage):
            icon = QIcon(QPixmap.fromImage(icon))
        elif not isinstance(icon, QIcon):
            msg = 'got incorrect type for icon: `%s`'
            logger.error(msg % type(icon).__name__)
            icon = QIcon()
        self.widget().setWindowIcon(icon)

