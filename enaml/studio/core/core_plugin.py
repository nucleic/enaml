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

from enaml.workbench.api import Plugin


URI_READERS_POINT = u'enaml.studio.core.uriReaders'


class CorePlugin(Plugin):
    """ The core plugin class for the Enaml studio.

    The core plugin provides common utility behaviors for a studio
    application such as reading data from an application uri.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._refresh_readers()
        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()
        self._clear_readers()

    def read_uri(self, uri):
        """ Read the data from the given uri.

        Parameters
        ----------
        uri : unicode
            The uri which points to the data which should be loaded.

        Returns
        -------
        result : object or None
            The data returned by the associated uri reader, or None
            if no data could be loaded.

        """
        try:
            parsed = urlparse.urlparse(uri)
        except ValueError:
            msg = "failed to parse uri '%s':\n%s"
            warnings.warn(msg % (uri, traceback.format_exc()))
            return None

        if not parsed.scheme:
            msg = "uri '%s' does not have a valid scheme"
            warnings.warn(msg % uri)
            return None

        reader = self._get_reader(parsed.scheme)
        if reader is None:
            return None

        return reader(parsed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of uri scheme to uri reader instance.
    _readers = Typed(dict, ())

    #: A mapping of uri scheme to ranking extension.
    _reader_extensions = Typed(dict, ())

    def _get_reader(self, scheme):
        """ Get the reader object for the given scheme.

        If an extension is registered for the scheme, the reader
        will only be created once, the first time it is requested.

        Parameters
        ----------
        scheme : unicode
            The scheme of the uri of interest.

        Returns
        -------
        result : URIReader or None
            A uri reader for the given scheme, or None if one could
            not be created.

        """
        if scheme in self._readers:
            return self._readers[scheme]

        if scheme not in self._reader_extensions:
            msg = "no uri reader is registered for '%s' uri scheme"
            warnings.warn(msg % scheme)
            return None

        extension = self._reader_extensions[scheme]
        reader = self.workbench.create_extension_object(extension)
        self._readers[scheme] = reader

        return reader

    def _refresh_readers(self):
        """ Refresh the uri readers for the plugin.

        This method will classify the reader extensions according to
        rank. Instantiating a reader instance is deferred until that
        specific reader is requested.

        """
        point = self.workbench.get_extension_point(URI_READERS_POINT)
        extensions = point.extensions
        if not extensions:
            self._clear_readers()
            return

        new = {}
        for extension in extensions:
            scheme = extension.get_property(u'scheme')
            new[scheme] = extension

        self._readers = {}
        self._reader_extensions = new

    def _clear_readers(self):
        """ Clear the underlying readers and classified extensions.

        """
        del self._readers
        del self._reader_extensions

    def _bind_observers(self):
        """ Bind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(URI_READERS_POINT)
        point.updated.bind(self._on_readers_updated)

    def _unbind_observers(self):
        """ Unbind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(URI_READERS_POINT)
        point.updated.unbind(self._on_readers_updated)

    def _on_readers_updated(self, change):
        """ An observer callback for the uri readers extension point.

        """
        self._refresh_readers()
