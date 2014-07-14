#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Property, Typed, Unicode

from enaml.layout.geometry import Pos


class DragEvent(Atom):
    """ A drag event that lazily fetches data.

    """
    #: The type of the specified data.
    type = Unicode()

    #: The position of the drag event.
    position = Typed(Pos)

    #: The data represented by the drag operation.
    data = Property()

    def _get_data(self):
        """ Fetches and returns the data for the drag operation. This method
        should be implemented by toolkit specific subclasses.

        """
        raise NotImplementedError
