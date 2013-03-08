#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from atom.api import Enum, Str, Coerced

from enaml.layout.geometry import Size

from .resource import Resource


class Image(Resource):
    """ A resource object representing an image.

    Instances of this class are created by an `ImageProvider` when it
    handles a request for an image. Instances of this class should be
    treated as read-only once they are created.

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
    size = Coerced(Size, factory=lambda: Size(-1, -1))

    # XXX this needs to be augmented to support arrays.
    #: The bytestring holding the data for the image.
    data = Str()

    def snapshot(self):
        """ Get a snapshot dictionary for this image.

        """
        snap = super(Image, self).snapshot()
        snap['format'] = self.format
        snap['size'] = self.size
        snap['data'] = self.data
        return snap


class ImageProvider(object):
    """ An abstract API definition for an image provider object.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def request_image(self, path, size, callback):
        """ Request an image from this provider.

        Parameters
        ----------
        path : str
            The requested path of the image, with the provider prefix
            removed. For example, if the full image source path was:
            `image://myprovider/icons/foo` then the path passed to
            this method will be `icons/foo`.

        size : tuple
            A tuple of (width, height) which is the requested size of
            the image. If this value is (-1, -1), then the image should
            be loaded in its original size. Otherwise, the image should
            be loaded in the requested size if possible.

        callback : callable
            A callable which should be invoked when the image is loaded.
            It accepts a single argument, which is the loaded `Image`
            object. It is safe to invoke this callable from a thread.

        """
        raise NotImplementedError

