#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.layout.geometry import Pos
from enaml.widgets.drag_event import DragEvent

from .QtGui import QDropEvent
from .qt_mime_data import QtMimeData


class QtDragEvent(DragEvent):
    """ A Qt implementation of an Enaml DragEvent.

    """
    #: Internal storage for the QDropEvent.
    _q_event = Typed(QDropEvent)

    def __init__(self, event):
        """ Initialize a QtDragEvent.

        Parameters
        ----------
        event : QDropEvent
            The Qt drop event object.

        """
        self._q_event = event

    def pos(self):
        """ Get the current mouse position of the operation.

        Returns
        -------
        result : Pos
            The mouse position of the operation in widget coordinates.

        """
        qpos = self._q_event.pos()
        return Pos(qpos.x(), qpos.y())

    def mime_data(self):
        """ Get the mime data contained in the drag operation.

        Returns
        -------
        result : QtMimeData
            The mime data contained in the drag operation.

        """
        return QtMimeData(self._q_event.mimeData())

    def is_accepted(self):
        """ Test whether the event has been accepted.

        Returns
        -------
        result : bool
            True if the event is accepted, False otherwise.

        """
        return self._q_event.isAccepted()

    def set_accepted(self, accepted):
        """ Set the accepted state of the event.

        Parameters
        ----------
        accepted : bool
            The target accepted state of the event.

        """
        self._q_event.setAccepted(accepted)

    def accept(self):
        """ Accept the drag event action.

        """
        self._q_event.accept()

    def ignore(self):
        """ Ignore the drag event action.

        """
        self._q_event.ignore()
