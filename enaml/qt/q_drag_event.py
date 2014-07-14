#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from .QtCore import QMimeData, Qt
from .QtGui import QApplication, QCursor

from ..widgets.drag_event import DragEvent


class QDragEvent(DragEvent):
    """ A Qt wrapper around a DragEvent.

    """
    #: Internal storage for the QMimeData from the drag operation.
    _q_mime_data = Typed(QMimeData)

    def _get_data(self):
        """ Fetch and return the data from the QEvent.

        """
        QApplication.setOverrideCursor(QCursor(Qt.BusyCursor))
        data = self._q_mime_data.data(self.type).data()
        QApplication.restoreOverrideCursor()

        return data
