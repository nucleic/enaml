#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging
from urlparse import urlparse

from atom.api import Atom, Dict, Str

from .icon_provider import IconProvider
from .image_provider import ImageProvider


logger = logging.getLogger(__name__)


class ResourceManager(Atom):
    """ A class which manages resource loading for a `Session`.

    A `ResourceManager` is used by a `Session` object to load resources
    when a url resource request is made by a client session. Users work
    with the manager by assigning provider objects associated with a
    host name. For example, a user can provide an image for the url
    `image://filesystem/c:/foo/bar.png` by assigning an `ImageProvider`
    instace to the `image_providers` dict with the key `filesystem`.

    """
    #: A dict mapping provider location to image provider object. When
    #: a resource `image://foo/bar/baz` is requested, the image provider
    #: provider `foo` is use to request path `/bar/baz`.
    image_providers = Dict(Str(), ImageProvider)

    #: A dict of icon providers for the `icon://...` scheme.
    icon_providers = Dict(Str(), IconProvider)

    def load(self, url, metadata, reply):
        """ Load a resource from the manager.

        Parameters
        ----------
        url : str
            The url pointing to the resource to load.

        metadata : dict
            Additional metadata required to load the resource of the
            given type. See the individual loading handlers for the
            supported metadata.

        reply : URLReply
            A url reply which will be invoked with the loaded resource
            object, or None if the loading fails. It must be safe to
            invoke this reply from a thread.

        """
        scheme = urlparse(url).scheme
        handler = getattr(self, '_load_' + scheme, None)
        if handler is None:
            msg = 'unhandled url resource scheme: `%s`'
            logger.error(msg % url)
            reply(None)
            return
        handler(url, metadata, reply)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _load_image(self, url, metadata, reply):
        """ Load an image resource.

        This is a private handler method called by the `load` method.
        It should not be called directly by user code.

        Parameters
        ----------
        url : str
            The url pointing to the image to load.

        metadata : dict
            The image loader accepts optional 'size' metadata which
            is the desired size with which to load the image. The
            default is (-1, -1) which indicates the images natural
            size should be used.

        reply : URLReply
            A url reply which will be invoked with the loaded image
            object, or None if the loading fails. It must be safe to
            invoke this reply from a thread.

        """
        spec = urlparse(url)
        provider = self.image_providers.get(spec.netloc)
        if provider is None:
            msg = 'no image provider registered for url: `%s`'
            logger.error(msg % url)
            reply(None)
            return
        size = metadata.get('size', (-1, -1))
        provider.request_image(spec.path, size, reply)

    def _load_icon(self, url, metadata, reply):
        """ Load an icon resource.

        This is a private handler method called by the `load` method.
        It should not be called directly by user code.

        Parameters
        ----------
        url : str
            The url pointing to the icon to load.

        metadata : dict
            The icon loader does not accept any metadata. Any data
            in this dict will be ignored.

        reply : URLReply
            A url reply which will be invoked with the loaded icon
            object, or None if the loading fails. It must be safe to
            invoke this reply from a thread.

        """
        spec = urlparse(url)
        provider = self.icon_providers.get(spec.netloc)
        if provider is None:
            msg = 'no icon provider registered for url: `%s`'
            logger.error(msg % url)
            reply(None)
            return
        provider.request_icon(spec.path, reply)

