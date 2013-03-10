#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, Typed, List, Value

from .image import Image


class IconImage(Atom):
    """ An object representing an image in an icon.

    Instances of this class are used to populate the 'images' list of
    an 'Icon' instance. Instances of this class should be treated as
    read only once they are created.

    """
    #: The widget mode for which this icon should apply.
    mode = Enum('normal', 'active', 'disabled', 'selected')

    #: The widget state for which this icon should apply.
    state = Enum('off', 'on')

    #: The image to use for this icon image.
    image = Typed(Image)


class Icon(Atom):
    """ An object object representing an icon.

    Once an image is created it should be treated as read only. User
    code should create a new icon object if the parameters need to
    be changed.

    """
    #: The list of icon images which compose this icon.
    images = List(IconImage)

    #: Storage space for use by a toolkit backend to use as needed.
    #: This should not typically be manipulated by user code.
    _tkdata = Value()
