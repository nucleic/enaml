#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.compat import coerce_to_qevent_type
from enaml.qt.QtCore import QEvent


#: An event type which indicates the contents of a dock area changed.
DockAreaContentsChanged = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was docked.
DockItemDocked = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was undock.
DockItemUndocked = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was extended.
DockItemExtended = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was retracted.
DockItemRetracted = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was shown.
DockItemShown = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was hidden.
DockItemHidden = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates the dock item was closed.
DockItemClosed = coerce_to_qevent_type(QEvent.registerEventType())


#: An event type which indicates a dock tab was selected.
DockTabSelected = coerce_to_qevent_type(QEvent.registerEventType())


class QDockItemEvent(QEvent):
    """ An event class for defining QDockItem events.

    """
    def __init__(self, type, name):
        """ Initialize a QDockItemEvent.

        Parameters
        ----------
        type : coerce_to_qevent_type
            The event type for the event.

        name : unicode
            The object name of the dock item of interest.

        """
        super(QDockItemEvent, self).__init__(type)
        self._name = name

    def name(self):
        """ Get the object name of the dock item of the event.

        Returns
        -------
        result : unicode
            The object name of the dock item for the event.

        """
        return self._name
