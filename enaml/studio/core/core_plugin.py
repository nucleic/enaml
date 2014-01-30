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

from atom.api import Typed

from enaml.workbench.plugin import Plugin


LOADERS_POINT = u'enaml.studio.core.loaders'


class CorePlugin(Plugin):
    """ The core plugin class for the Enaml studio.

    The core plugin provides common utility behaviors for a studio
    application such as loading data from an application url.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._refresh_loaders()
        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()
        self._clear_loaders()

    def load_url(self, url):
        """ Load the data from the given url.

        Parameters
        ----------
        url : unicode
            The url which points to the data which should be loaded.

        Returns
        -------
        result : object or None
            The data returned by the associated url loader, or None
            if no data could be loaded.

        """
        try:
            parsed = urlparse.urlparse(url)
        except ValueError:
            msg = "failed to parse url '%s':\n%s"
            warnings.warn(msg % (url, traceback.format_exc()))
            return None

        if not parsed.scheme:
            msg = "url '%s' does not have a valid scheme"
            warnings.warn(msg % url)
            return None

        loader = self._get_loader(parsed.scheme)
        if loader is None:
            return None

        return loader(parsed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of url scheme to url loader instance.
    _loaders = Typed(dict, ())

    #: A mapping of url scheme to ranking extension.
    _loader_extensions = Typed(dict, ())

    def _get_loader(self, scheme):
        """ Get the loader object for the given scheme.

        If an extension is registered for the scheme, the loader
        will only be created once, the first time it is requested.

        Parameters
        ----------
        scheme : unicode
            The scheme of the url of interest.

        Returns
        -------
        result : URLLoader or None
            A url loader for the given scheme, or None if one could
            not be created.

        """
        if scheme in self._loaders:
            return self._loaders[scheme]

        if scheme not in self._loader_extensions:
            msg = "no url loader is registered for '%s' url scheme"
            warnings.warn(msg % scheme)
            return None

        extension = self._loader_extensions[scheme]
        loader = self.workbench.create_extension_object(extension)
        self._loaders[scheme] = loader

        return loader

    def _refresh_loaders(self):
        """ Refresh the url loaders for the plugin.

        This method will classify the loader extensions according to
        rank. Instantiating a loader instance is deferred until that
        specific loader is requested.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        extensions = point.extensions
        if not extensions:
            self._clear_loaders()
            return

        new = {}
        for extension in extensions:
            scheme = extension.get_property(u'scheme')
            new[scheme] = extension

        self._loaders = {}
        self._loader_extensions = new

    def _clear_loaders(self):
        """ Clear the underlying loaders and classified extensions.

        """
        del self._loaders
        del self._loader_extensions

    def _bind_observers(self):
        """ Bind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        point.updated.bind(self._on_loaders_updated)

    def _unbind_observers(self):
        """ Unbind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        point.updated.unbind(self._on_loaders_updated)

    def _on_loaders_updated(self, change):
        """ An observer callback for the url loaders extension point.

        """
        self._refresh_loaders()
