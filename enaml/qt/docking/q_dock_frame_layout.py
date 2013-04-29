#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QLayout


class QDockFrameLayout(QLayout):
    """ A QLayout subclass which handles layout for dock frames.

    This class is used by the docking framework and is not intended for
    direct use by user code.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockFrameLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget owner of the layout.

        """
        super(QDockFrameLayout, self).__init__(parent)
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()
        self._dock_widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockWidget(self):
        """ Get the dock widget for the layout.

        Returns
        -------
        result : QWidget
            The dock widget set in the layout.

        """
        return self._dock_widget

    def setDockWidget(self, dock_widget):
        """ Set the dock widget for the layout.

        The old dock widget will be hidden and unparented, but not
        destroyed.

        Parameters
        ----------
        dock_widget : QWidget
            The primary dock widget to use in the layout.

        """
        old_widget = self._dock_widget
        if old_widget is not None:
            old_widget.hide()
            old_widget.setParent(None)
        self._dock_widget = dock_widget
        if dock_widget is not None:
            dock_widget.setParent(self.parentWidget())
            dock_widget.show()
        self.invalidate()

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockFrameLayout, self).invalidate()
        size = QSize()
        self._size_hint = size
        self._min_size = size
        self._max_size = size

    def setGeometry(self, rect):
        """ Set the geometry for the items in the layout.

        """
        super(QDockFrameLayout, self).setGeometry(rect)
        dock_widget = self._dock_widget
        if dock_widget is not None:
            dock_widget.setGeometry(self.contentsRect())

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        hint = self._size_hint
        if hint.isValid():
            return hint
        dock_widget = self._dock_widget
        if dock_widget is not None:
            hint = dock_widget.sizeHint()
        else:
            hint = QSize(256, 192)
        m = self.contentsMargins()
        hint.setWidth(hint.width() + m.left() + m.right())
        hint.setHeight(hint.height() + m.top() + m.bottom())
        self._size_hint = hint
        return hint

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        size = self._min_size
        if size.isValid():
            return size
        dock_widget = self._dock_widget
        if dock_widget is not None:
            size = dock_widget.minimumSizeHint()
        else:
            size = QSize(256, 192)
        m = self.contentsMargins()
        size.setWidth(size.width() + m.left() + m.right())
        size.setHeight(size.height() + m.top() + m.bottom())
        self._min_size = size
        return size

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        size = self._max_size
        if size.isValid():
            return size
        dock_widget = self._dock_widget
        if dock_widget is not None:
            size = dock_widget.maximumSize()
        else:
            size = QSize(16777215, 16777215)
        self._max_size = size
        return size

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        """
        raise NotImplementedError('Use `setDockWidget` instead.')

    def count(self):
        """ A required virtual method implementation.

        """
        return 0

    def itemAt(self, idx):
        """ A required virtual method implementation.

        """
        return None

    def takeAt(self, idx):
        """ A required virtual method implementation.

        """
        return None
