#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import traceback
import warnings

from enaml.icon import Icon, IconImage
from enaml.image import Image

from .resource_loader import ResourceLoader


class FileLoader(ResourceLoader):
    """ A resource loader which will load objects from files.

    This loader can handle types 'raw', 'text', 'image', and 'icon'.

    """
    def __call__(self, kind, uri):
        """ Load the resource specified by the uri.

        Parameters
        ----------
        kind : unicode
            The type of the object to load from the give uri. This
            will be one of the types declared to be handled by the
            extension.

        uri : urlparse.ParseResult
            The parsed uri pointing to the data object which should be
            loaded.

        Returns
        -------
        result : str, Icon, or None
            For the 'raw' and 'text' data types, a string will be
            returned. An Icon will be returned for the 'icon' data
            type. If the resource fails to load, a warning will be
            emitted and None will be returned.

        """
        handler = getattr(self, '_load_%s' % kind, None)
        if not handler:
            msg = "FileLoader cannot handle object type '%s'"
            warnings.warn(msg % kind)
            return None

        try:
            result = handler(uri)
        except IOError:
            msg = "failed to load file data:\n%s"
            warnings.warn(msg % traceback.format_exc())
            return None

        return result

    def _load_raw(self, uri):
        """ Load the raw binary data for the provided uri.

        """
        path = os.path.join(uri.netloc, uri.path)
        with open(path, 'rb') as f:
            data = f.read()
        return data

    def _load_text(self, uri):
        """ Load the text data for the provided uri.

        """
        path = os.path.join(uri.netloc, uri.path)
        with open(path, 'r') as f:
            text = f.read()
        return text

    def _load_image(self, uri):
        """ Load the Image for the provided uri.

        """
        # TODO support size and format query parameters
        data = self._load_raw(uri)
        return Image(data=data)

    def _load_icon(self, uri):
        """ Load the Icon for the provided uri.

        """
        # TODO support size and format query parameters
        image = self._load_image(uri)
        return Icon(images=[IconImage(image=image)])
