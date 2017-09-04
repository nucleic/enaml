#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import Qt, QSize
from .QtWidgets import QWidget, QLayout

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


class QWindowBase(QWidget):
    """ A QWidget which forms the base for derived window classes.

    The window base provides support for a central widget as well as
    explicitly specified min and max sizes which override what would
    normally be computed by the layout.

    """
    def __init__(self, parent=None, flags=Qt.WindowFlags(0)):
        """ Initialize a QWindowBase.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the window.

        flags : Qt.WindowFlags, optional
            The window flags to pass to the parent constructor.

        """
        super(QWindowBase, self).__init__(parent, flags)
        self._expl_min_size = QSize()
        self._expl_max_size = QSize()
        layout = QWindowLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

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
        super(QWindowBase, self).setMinimumSize(size)
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
        super(QWindowBase, self).setMaximumSize(size)
        if size == QSize(16777215, 16777215):
            self._expl_max_size = QSize()
        else:
            self._expl_max_size = size
        self.layout().update()
