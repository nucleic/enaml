#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, IntEnum, Typed, Unicode


class DockEvent(Atom):
    """ A sentinel base class for events which occur in a dock area.

    """
    pass


class DockItemEvent(DockEvent):
    """ A DockEvent for events which involve a single dock item.

    """
    class Type(IntEnum):
        """ An IntEnum which defines the dock item event types.

        """
        #: The dock item was docked in a dock area.
        Docked = 0

        #: The dock item was undocked from a dock area.
        Undocked = 1

        #: The dock item was extended from a dock bar.
        Extended = 2

        #: The dock item was retracted into a dock bar.
        Retracted = 3

        #: The dock item was shown on the screen.
        Shown = 4

        #: The dock item was hidden from the screen.
        Hidden = 5

        #: The dock item was closed.
        Closed = 6

        #: The dock item became the selected tab in a tab group.
        TabSelected = 7

    # Proxy out the enum values for simpler access.
    Docked = Type.Docked
    Undocked = Type.Undocked
    Extended = Type.Extended
    Retracted = Type.Retracted
    Shown = Type.Shown
    Hidden = Type.Hidden
    Closed = Type.Closed
    TabSelected = Type.TabSelected

    #: The type of the dock item event.
    type = Typed(Type)

    #: The name of the relevant dock item.
    name = Unicode()
