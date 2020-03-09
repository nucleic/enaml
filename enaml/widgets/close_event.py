#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Bool


class CloseEvent(Atom):
    """ An payload object carried by a widget 'closing' event.

    User code can manipulate this object to veto a close event.

    """
    #: The internal accepted state.
    _accepted = Bool(True)

    def is_accepted(self):
        """ Get whether or not the event is accepted.

        Returns
        -------
        result : bool
            True if the event is accepted, False otherwise. The
            default is True.

        """
        return self._accepted

    def accept(self):
        """ Accept the close event and allow the widget to be closed.

        """
        self._accepted = True

    def ignore(self):
        """ Reject the close event and prevent the widget from closing.

        """
        self._accepted = False
