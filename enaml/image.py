#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, Bytes, Value, Coerced

from enaml.layout.geometry import Size


class Image(Atom):
    """ An object representing an image.

    Once an image is created it should be treated as read only. User
    code should create a new image object if the parameters need to
    be changed.

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
        'argb32',   # Raw data in the 0xAARRGGBB format.
                    # The `raw_size` of the image must be provided.
    )

    #: The (width, height) raw size of the image. This must be provided
    #: for images where the size is not encoded in the data stream.
    raw_size = Coerced(Size, (0, 0))

    #: The (width, height) size of the image. An invalid size indicates
    #: that the size of the image should be automatically inferred. A
    #: valid size indicates that the toolkit image should be scaled to
    #: the specified size.
    size = Coerced(Size, (-1, -1))

    #: The aspect ratio mode to use when the toolkit scales the image.
    aspect_ratio_mode = Enum('ignore', 'keep', 'keep_by_expanding')

    #: The transform mode to use when the toolkit scales the image.
    transform_mode = Enum('smooth', 'fast')

    # XXX this needs to be augmented to support arrays.
    #: The bytestring holding the data for the image.
    data = Bytes()

    #: Storage space for use by a toolkit backend to use as needed.
    #: This should not typically be manipulated by user code.
    _tkdata = Value()
