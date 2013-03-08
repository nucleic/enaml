#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, Str, Coerced

from enaml.layout.geometry import Size


class Image(Atom):
    """ An object representing an image.

    """
    #: The format of the image. By default, the consumer of the image
    #: will probe the header to automatically infer a type.
    format = Enum(
        'auto',     # Automatically determine the image format
        'png',      # Portable Network Graphics
        'jpg',      # Joint Photographic Experts Group
        'gif',      # Graphics Interchange Format
        'bmp',      # Windows Bitmap
        'xpm',      # X11 Pixmap
        'xbm',      # X11 Bitmap
        'pbm',      # Portable Bitmap
        'pgm',      # Portable Graymap
        'ppm',      # Portable Pixmap
        'tiff',     # Tagged Image File Format
        # 'array',    # A numpy array with an appropriate image dtype.
    )

    #: The (width, height) size of the image. An invalid size indicates
    #: that the size of the image should be automatically inferred.
    size = Coerced(Size, (-1, -1))

    # XXX this needs to be augmented to support arrays.
    #: The bytestring holding the data for the image.
    data = Str()
