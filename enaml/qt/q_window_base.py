#------------------------------------------------------------------------------
# Copyright (c) 2013-2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from enaml.widgets.close_event import CloseEvent

from .QtCore import Qt, QSize
from .QtWidgets import QLayout, QWidget

from .q_single_widget_layout import QSingleWidgetLayout


class QWindowLayout(QSingleWidgetLayout):
    """ A single widget layout for use with window classes.

    This class extends the single widget layout to add support for
    QWindowBase classes and their use of explicit min and max sizes.

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


# =============================================================================
# --- Base window implenmentation ---------------------------------------------
# =============================================================================


def add_base_window_methods(window_class):
    """ Add methods to a window class.

    The patching provides support for a central widget as well as
    explicitly specified min and max sizes which override what would
    normally be computed by the layout.

    We use patching rather than a mixing class to avoid multiple inheritance
    which causes an issue in PySide2 that affects dialogs. Since this is the
    only blocker to support Pyside2 it is worth it.

    """

    # This will appear as a cell var to
    __class__ = window_class

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
            self.accept_closing(event, d)
        else:
            event.ignore()

    def centralWidget(self):
        """ Get the central widget installed on the window.

        Returns
        -------
        result : QWidget or None
            The central widget of the window, or None if no widget
            was provided.

        """
        return self.layout().getWidget()

    def setCentralWidget(self, widget):
        """ Set the central widget for this window.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the content of the window.

        """
        self.layout().setWidget(widget)

    def explicitMinimumSize(self):
        """ Get the explicit minimum size for this widget.

        Returns
        -------
        result : QSize
            If the user has explitly set the minimum size of the
            widget, that size will be returned. Otherwise, an
            invalid QSize will be returned.

        """
        return self._expl_min_size

    def explicitMaximumSize(self):
        """ Get the explicit maximum size for this widget.

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
        super().setMinimumSize(size)
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
        super().setMaximumSize(size)
        if size == QSize(16777215, 16777215):
            self._expl_max_size = QSize()
        else:
            self._expl_max_size = size
        self.layout().update()

    for func in (closeEvent, centralWidget, setCentralWidget,
                explicitMinimumSize, explicitMaximumSize, setMinimumSize,
                setMaximumSize):
        setattr(window_class, func.__name__, func)

    return window_class
