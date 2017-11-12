#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import QSize
from enaml.qt.q_single_widget_layout import QSingleWidgetLayout


class QDockFrameLayout(QSingleWidgetLayout):
    """ A single widget layout for dock frames.

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

    #--------------------------------------------------------------------------
    # QLayout API
    #--------------------------------------------------------------------------
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockFrameLayout, self).invalidate()
        self._size_hint = QSize()
        self._min_size = QSize()
        self._max_size = QSize()

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        hint = self._size_hint
        if hint.isValid():
            return hint
        hint = super(QDockFrameLayout, self).sizeHint()
        if not hint.isValid():
            hint = QSize(256, 192)
        self._size_hint = hint
        return hint

    def minimumSize(self):
        """ Get the minimum size for the layout.

        """
        size = self._min_size
        if size.isValid():
            return size
        size = super(QDockFrameLayout, self).minimumSize()
        if not size.isValid():
            size = QSize(256, 192)
        self._min_size = size
        return size

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        size = self._max_size
        if size.isValid():
            return size
        size = super(QDockFrameLayout, self).maximumSize()
        self._max_size = size
        return size
