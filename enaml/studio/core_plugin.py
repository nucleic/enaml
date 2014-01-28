#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import traceback
import urlparse
import warnings

from atom.api import List, Typed, atomref

from enaml.workbench.api import Plugin

from .refresh_listener import RefreshListener
from .resource_loader import ResourceLoader
from .utils import rank_sort


LOADERS_POINT = u'enaml.studio.core.loaders'


class CorePlugin(Plugin):
    """ The core plugin class for the Enaml studio.

    The core plugin provides common utility behaviors for a studio
    application, such as loading a resource from a uri.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._refresh_loaders()
        self._install_listeners()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._remove_listeners()
        self._release_loaders()

    def load_resource(self, kind, uri):
        """ Load a resource of a given kind from a given uri.

        Parameters
        ----------
        kind : unicode
            The type of the object to load from the give uri.

        uri : unicode
            The full uri which points to the resource to load.

        Returns
        -------
        result : object or None
            The loaded object or None if it could not be loaded.

        """
        try:
            parsed = urlparse.urlparse(uri)
        except ValueError:
            msg = "failed to parse uri:\n%s"
            warnings.warn(msg % traceback.format_exc())
            return None

        if not parsed.scheme:
            msg = "uri '%s' does not have a valid scheme"
            warnings.warn(msg % uri)
            return None

        loader = self._get_loader(parsed.scheme, kind)
        if loader is None:
            return None

        return loader(kind, parsed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of (scheme, kind) to the ranking (extension, loader)
    _loaders = Typed(dict, ())

    #: The registry listeners installed for the for plugin.
    _registry_listeners = List()

    def _get_loader(self, scheme, kind):
        """ Get the loader object for the given pair.

        If an extension is registered for the pair, the extension object
        will only be created once, the first time it is requested.

        Parameters
        ----------
        scheme : unicode
            The loader scheme for the uri of interest.

        kind : unicode
            The data type which should be handled by the loader.

        Returns
        -------
        result : ResourceLoader or None
            A resource loader for the given pair, or None if one could
            not be created.

        """
        key = (scheme, kind)
        if key not in self._loaders:
            msg = "no loader extension is registered for scheme '%s' "\
                  "with data type '%s'"
            warnings.warn(msg % key)
            return None

        extension, loader = self._loaders[key]
        if loader is None:
            loader = self.workbench.create_extension_object(extension)
            if not isinstance(loader, ResourceLoader):
                msg = "extension '%s' created non-ResourceLoader type '%s'"
                warnings.warn(msg % (extension.cls, type(loader).__name__))
                loader = ResourceLoader()
            self._loaders[key] = (extension, loader)

        return loader

    def _refresh_loaders(self):
        """ Create the resource loaders for the plugin.

        This method will classify the loader extensions according to
        rank. Instantiating a loader instance is deferred until that
        specific loader is requested.

        """
        extensions = self.workbench.get_extensions(LOADERS_POINT)
        if not extensions:
            del self._loaders
            return

        old = self._loaders
        new = {}

        # TODO validate the extensions against a schema
        extensions = rank_sort(extensions)
        for ext in extensions:
            scheme = ext.get_property(u'scheme')
            types = ext.get_property(u'types')
            for kind in types:
                key = (scheme, kind)
                old_ext, loader = old.get(key, (None, None))
                new[key] = (ext, loader) if ext is old_ext else (ext, None)

        self._loaders = new

    def _release_loaders(self):
        """ Release the underlying resource loaders.

        """
        del self._loaders

    def _install_listeners(self):
        """ Install the registry event listeners for the plugin.

        """
        listeners = []
        ref = atomref(self)
        workbench = self.workbench
        pairs = ((LOADERS_POINT, '_refresh_loaders'),)

        for point, name in pairs:
            listener = RefreshListener(plugin_ref=ref, method_name=name)
            workbench.add_listener(point, listener)
            listeners.append((point, listener))

        self._registry_listeners = listeners

    def _remove_listeners(self):
        """ Remove the registry event listeners installed by the plugin.

        """
        workbench = self.workbench
        for point, listener in self._registry_listeners:
            workbench.remove_listener(point, listener)
        self._registry_listeners = []
