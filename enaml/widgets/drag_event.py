#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom


class DragEvent(Atom):
    """ An abstract class for defining a drag event.

    Concrete implementations of this class will be created by a
    toolkit backend and passed to the relevant frontend handlers.

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
        """ Accept the drag event action.

        """
        raise NotImplementedError

    def ignore(self):
        """ Ignore the drag event action.

        """
        raise NotImplementedError
