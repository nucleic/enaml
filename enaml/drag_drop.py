#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, IntEnum, Typed, Coerced, Tuple, Int

from .application import Application
from .image import Image
from .mime_data import MimeData


class DropAction(IntEnum):
    """ An enum defining the possible drop actions.

    """
    #: The action is ignored.
    Ignore = 0x0

    #: The data is copied to the target.
    Copy = 0x1

    #: The data is moved from the source to the target.
    Move = 0x2

    #: Create a link from the source to the target.
    Link = 0x4


def mime_data_factory():
    """ Create a new MimeData object for a drag operation.

    Returns
    -------
    result : MimeData
        A toolkit specific mime data object.

    """
    return Application.instance().create_mime_data()


class DragData(Atom):
    """ An object which initialize the data for a drag operation.

    """
    #: The mime data to use for the drag operation. This is created
    #: automatically, but can be reassigned by the user if necessary.
    mime_data = Typed(MimeData, factory=mime_data_factory)

    #: The default drop action for the drag data. If not provided,
    #: the toolkit will choose a suitable default from among the
    #: supported action.
    default_drop_action = Coerced(DropAction, (DropAction.Ignore,))

    #: The supported drop actions of the drag data. This is an OR'd
    #: combination of the available DropAction flags.
    supported_actions = Coerced(DropAction.Flags, (DropAction.Move,))

    #: The image to use for the drag. If this is not provided, the
    #: toolkit will choose a suitable default value.
    image = Typed(Image)

    #: The x,y position the drag image appears under the cursor.
    #: If not provided, this is the last position of the cursor in the widget.
    hotspot = Tuple(item=Int())


class DropEvent(Atom):
    """ An abstract class for defining a drag event.

    Concrete implementations of this class will be created by a
    toolkit backend and passed to the relevant frontend handlers.

    Instances of this class will never be created by the user.

    """
    def pos(self):
        """ Get the current mouse position of the operation.

        Returns
        -------
        result : Pos
            The mouse position of the operation in widget coordinates.

        """
        raise NotImplementedError

    def mime_data(self):
        """ Get the mime data contained in the drag operation.

        Returns
        -------
        result : MimeData
            The mime data contained in the drag operation.

        """
        raise NotImplementedError

    def drop_action(self):
        """ Get the action to be performed by the drop target.

        Returns
        -------
        result : DropAction
            A drop action enum value.

        """
        raise NotImplementedError

    def possible_actions(self):
        """ Get the OR'd combination of possible drop actions.

        Returns
        -------
        result : DropAction.Flags
            The combination of possible drop actions.

        """
        raise NotImplementedError

    def proposed_action(self):
        """ Get the action proposed to be taken by the drop target.

        Returns
        -------
        result : DropAction
            The proposed action for the drop target.

        """
        raise NotImplementedError

    def accept_proposed_action(self):
        """ Accept the event using the proposed drop action.

        """
        raise NotImplementedError

    def set_drop_action(self, action):
        """ Set the drop action to one of the possible actions.

        Parameters
        ----------
        action : DropAction
            The drop action to be performed by the target.

        """
        raise NotImplementedError

    def is_accepted(self):
        """ Test whether the event has been accepted.

        Returns
        -------
        result : bool
            True if the event is accepted, False otherwise.

        """
        raise NotImplementedError

    def set_accepted(self, accepted):
        """ Set the accepted state of the event.

        Parameters
        ----------
        accepted : bool
            The target accepted state of the event.

        """
        raise NotImplementedError

    def accept(self):
        """ Accept the current drop event action.

        """
        raise NotImplementedError

    def ignore(self):
        """ Ignore the current drop event action.

        """
        raise NotImplementedError
