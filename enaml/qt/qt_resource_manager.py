#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging
from urlparse import urlparse

from enaml.utils import id_generator

from .q_deferred_caller import deferredCall
from .qt_resource import convert_resource


logger = logging.getLogger(__name__)


#: An id generator for making requests to the server.
req_id_generator = id_generator('r_')


class DeferredResource(object):
    """ An deferred resource object returned by a `QtURLRequestManager`.

    Instances of this class are provided to widgets when they request a
    resource url. Since the url may need to be retrieved from a server,
    Loading occurs asynchronously. This object allows a widget to supply
    a callback to be invoked when the resource is loaded.

    """
    __slots__ = ('_callback')

    def __init__(self):
        """ Initialize a DeferredResource.

        """
        self._callback = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _notify(self, resource):
        """ Notify the consumer that the resource is available.

        This method is invoked directly by a `QtResourceManager`. It
        should not be called by user code.

        Parameters
        ----------
        resource : object
            An object of the appropriate type for the requested resource.

        """
        callback = self._callback
        self._callback = None
        if callback is not None:
            callback(resource)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def on_load(self, callback):
        """ Register a callback to be invoked on resource load.

        Parameters
        ----------
        callback : callable
            A callable which accepts a single argument, which is the
            resource object loaded for the requested resource.

        """
        self._callback = callback


class QtResourceManager(object):
    """ An object which manages requesting urls from the server session.

    """
    def __init__(self):
        """ Initialize a QtResourceManager.

        """
        self._handles = {}
        self._pending = {}

    def load(self, url, metadata, request):
        """ Load the resource handle for the given url.

        This method will asynchronously load the resource for the given
        url, requesting it from the server side session if needed.

        Parameters
        ----------
        url : str
            The url pointing to the resource to load.

        metadata : dict
            Additional metadata required by the session to load the
            requested resource. See the individual load handlers for
            the supported metadata.

        request : URLRequest
            An URLRequest instance to use for making requests from the
            server side session, if such requests are required.

        Returns
        -------
        result : DeferredResource
            A deferred resource object which will invoke a callback on
            resource load.

        """
        loader = DeferredResource()
        scheme = urlparse(url).scheme
        key_handler = getattr(self, '_make_%s_key' % scheme, None)
        if key_handler is None:
            msg = 'unhandled request scheme for url: `%s`'
            logger.error(msg % url)
            return loader
        keyval = key_handler(metadata)
        key = (url, keyval)
        handles = self._handles
        if key in handles:
            deferredCall(loader._notify, handles[key])
            return loader
        pending = self._pending
        if key in pending:
            pending[key].append(loader)
            return loader
        req_id = req_id_generator.next()
        pending[req_id] = key
        pending[key] = [loader]
        request(req_id, url, metadata)
        return loader

    def on_load(self, req_id, url, resource):
        """ Handle the loading of a requested resource.

        This method is called by the QtSession object when it receives
        a reply for a previously requested resource.

        Parameters
        ----------
        req_id : str
            The unique identifier for the request.

        url : str
            The resource url which was requested.

        resource : dict
            The dictionary representation of the loaded resource.

        """
        pending = self._pending
        if req_id in pending:
            key = pending.pop(req_id)
            if key in pending:
                loaders = pending.pop(key)
            else:
                loaders = ()
            qt_resource = convert_resource(resource)
            if qt_resource is not None:
                self._handles[key] = qt_resource
                for loader in loaders:
                    loader._notify(qt_resource)

    def on_fail(self, req_id, url):
        """ Handle the failed loading of a requested resource.

        This method is called by the QtSession object when it receives
        a reply for a previously requested resource which failed to
        properly load.

        Parameters
        ----------
        req_id : str
            The unique identifier for the request.

        url : str
            The resource url which was requested.

        resource : dict
            The dictionary representation of the resrouce

        """
        # TODO use something like a failed-to-load image here?
        pending = self._pending
        if req_id in pending:
            key = pending.pop(req_id)
            if key in pending:
                del pending[key]

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _make_image_key(self, metadata):
        """ Make a key value for the image metadata.

        Parameters
        ----------
        metadata : dict
            The image accepts optional 'size' metadata which is the
            desired size with which to load the image. The default is
            (-1, -1) which indicates the natural size should be used.

        Returns
        -------
        result : tuple
            The size with which to load the image.

        """
        return metadata.get('size', (-1, -1))

    def _make_icon_key(self, metatdata):
        """ Make a key value for the icon metadata.

        Parameters
        ----------
        metadata : dict
            The icon accepts no metadata. Any data in this dict will be
            ignored.

        Returns
        -------
        result : None
            This method always returns None.

        """
        return None

