#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import QEvent


#: An event type which indicates the contents of a dock area changed.
DockAreaContentsChanged = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was docked.
DockItemDocked = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was undock.
DockItemUndocked = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was extended.
DockItemExtended = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was retracted.
DockItemRetracted = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was shown.
DockItemShown = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates the dock item was hidden.
DockItemHidden = QEvent.Type(QEvent.registerEventType())


#: An event type which indicates a dock tab was selected.
DockTabSelected = QEvent.Type(QEvent.registerEventType())


class QDockItemEvent(QEvent):
    """ An event class for defining QDockItem events.

    """
    def __init__(self, type, name):
        """ Initialize a QDockItemEvent.

        Parameters
        ----------
        type : QEvent.Type
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


class QDockTabSelectionEvent(QEvent):
    """ An event class for specifying a dock tab selection event.

    """
    def __init__(self, current, previous):
        """ Initialize a QDockTabSelectionEvent.

        Parameters
        ----------
        current : unicode
            The object name of the currently selected tab item.

        previous : unicode
            The object name of the previously selected tab item. This
            may be an empty string if there was no previous selection.

        """
        super(QDockTabSelectionEvent, self).__init__(DockTabSelected)
        self._current = current
        self._previous = previous

    def current(self):
        """ Get the name of the currently selected tab item.

        Returns
        -------
        result : unicode
            The object name of the currently selected tab item.

        """
        return self._current

    def previous(self):
        """ Get the name of the previously selected tab item.

        Returns
        -------
        result : unicode
            The object name of the previously selected tab item.

        """
        return self._previous
