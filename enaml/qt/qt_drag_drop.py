#------------------------------------------------------------------------------
# Copyright (c) 2014-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.drag_drop import DropAction, DropEvent
from enaml.layout.geometry import Pos

from .QtCore import Qt
from .QtGui import QDropEvent
from .qt_mime_data import QtMimeData


class QtDropEvent(DropEvent):
    """ A Qt implementation of an Enaml DragEvent.

    """
    #: Internal storage for the QDropEvent.
    _q_event = Typed(QDropEvent)

    def __init__(self, event):
        """ Initialize a QtDropEvent.

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

    def drop_action(self):
        """ Get the action to be performed by the drop target.

        Returns
        -------
        result : DropAction
            A drop action enum value.

        """
        return DropAction(int(self._q_event.dropAction()))

    def possible_actions(self):
        """ Get the OR'd combination of possible drop actions.

        Returns
        -------
        result : DropAction.Flags
            The combination of possible drop actions.

        """
        return DropAction.Flags(int(self._q_event.possibleActions()))

    def proposed_action(self):
        """ Get the action proposed to be taken by the drop target.

        Returns
        -------
        result : DropAction
            The proposed action for the drop target.

        """
        return DropAction(int(self._q_event.proposedAction()))

    def accept_proposed_action(self):
        """ Accept the event using the proposed drop action.

        """
        self._q_event.acceptProposedAction()

    def set_drop_action(self, action):
        """ Set the drop action to one of the possible actions.

        Parameters
        ----------
        action : DropAction
            The drop action to be performed by the target.

        """
        self._q_event.setDropAction(Qt.DropAction(action))

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
