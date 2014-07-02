#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode, Typed, Coerced

from layout.geometry import Pos
from image import Image


class Drag(Atom):
    """ An object representing a drag operation.

    """
    #: The data that the drag operation represents.
    data = Typed(bytearray)

    #: The type of data being dragged.
    type = Unicode()

    #: The image that should be displayed under the cursor.
    image = Typed(Image)

    #: The mouse position of the drag operation. This should not be changed
    #: by user code.
    position = Coerced(Pos, (-1, -1))
