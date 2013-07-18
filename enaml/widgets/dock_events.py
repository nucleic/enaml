#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode


class DockEvent(Atom):
    """ A base class for defining events which occur in a dock area.

    """
    pass


class ItemDocked(DockEvent):
    """ A dock event emitted when an item is docked in a dock area.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class ItemUndocked(DockEvent):
    """ A dock event emitted when an item is undocked from an area.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class ItemExtended(DockEvent):
    """ A dock event emitted when an item is extended from a dock bar.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class ItemRetracted(DockEvent):
    """ A dock event emitted when an item is retracted into a dock bar.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class ItemShown(DockEvent):
    """ A dock even emitted when an item becomes visible on the screen.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class ItemHidden(DockEvent):
    """ A dock even emitted when an item is hidden from the screen.

    """
    #: The name of the relevant dock item.
    name = Unicode()


class TabSelected(DockEvent):
    """ A dock event emitted when a tab in tab group is selected.

    """
    #: The name of the currently selected dock item.
    current = Unicode()

    #: The name of the previously selected dock item.
    previous = Unicode()
