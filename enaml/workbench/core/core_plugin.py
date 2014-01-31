#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import json
import os
import traceback
import urlparse
import warnings

from atom.api import Callable, Typed

from enaml.workbench.plugin import Plugin


LOADERS_POINT = u'enaml.workbench.core.loaders'

VALIDATE_ENABLED = bool(os.environ.get('ENAML_WORKBENCH_SCHEMA_VALIDATION'))


class CorePlugin(Plugin):
    """ The core plugin for the Enaml workbench.

    The core plugin provides low level utility behaviors for a workbench
    application such as loading data from urls and validating JSON data.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()
        self._loaders.clear()

    def load_url(self, url, parent=u''):
        """ Load the data from the given url.

        Parameters
        ----------
        url : unicode
            The url which points to the data which should be loaded.

        parent : unicode, optional
            A parent url to use when resolving a relative url.

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

        if not loader.isabs(url):
            url = loader.absurl(url, parent)
        return loader(url)

    def validate(self, item, url, parent=u''):
        """ Validate the given item against a JSON schema.

        Parameters
        ----------
        item : object
            The Python object loaded from a JSON file.

        url : unicode
            A url pointing to the schema to use for validating the
            json object. A scheme handler for the url should already
            be registered before calling this method.

        parent : unicode, optional
            A parent url to use when resolving a relative url.

        """
        if not VALIDATE_ENABLED:
            return

        key = (url, parent)
        if key not in self._schemas:
            schema = self._load_schema(url, parent)
            self._schemas[key] = schema

        schema = self._schemas[key]
        if schema is not None:
            self._get_validator()(item, schema)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of url scheme to url loader instance.
    _loaders = Typed(dict, ())

    #: A mapping of url to loaded schema object.
    _schemas = Typed(dict, ())

    #: The callable which implements schema validation.
    _validator = Callable()

    def _get_loader(self, scheme):
        """ Get the loader object for the given scheme.

        If an extension is registered for the scheme, the loader will
        only be created once, the first time it is requested.

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
        scheme = scheme.lower()
        if scheme in self._loaders:
            return self._loaders[scheme]

        extension = self._get_loader_extension(scheme)
        if extension is None:
            msg = "no url loader is registered for the '%s' url scheme"
            warnings.warn(msg % scheme)
            return None

        loader = self.workbench.create_extension_object(extension)
        self._loaders[scheme] = loader
        return loader

    def _get_loader_extension(self, scheme):
        """ Get the ranking loader extension for the given url scheme.

        Parameters
        ----------
        scheme : unicode
            The scheme of the url of interest.

        Returns
        -------
        result : Extension or None
            The highest ranked loader Extension for the given scheme,
            or None if there is no such registered Extension.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        for extension in reversed(point.extensions):
            ext_scheme = extension.config[u'scheme']
            if ext_scheme.lower() == scheme:
                return extension
        return None

    def _get_validator(self):
        """ Get the callable for validating json schema.

        Returns
        -------
        result : callable
            A callable which takes the item and a schema and validates
            that the item adheres to the schema. It returns None on
            success and raises on failure.

        """
        validator = self._validator
        if validator is not None:
            return validator

        try:
            import jsonschema
        except ImportError:
            msg = "The 'jsonschema' package is not installed. "
            msg += "Schema validation will be skipped."
            warnings.warn(msg)
            validator = lambda item, scheme: None
        else:
            validator = jsonschema.validate

        self._validator = validator
        return validator

    def _load_schema(self, url, parent):
        """ Load the JSON schema object from the given url.

        url : unicode
            A url pointing to the JSON schema.

        parent : unicode
            A parent url to use when resolving a relative url.

        """
        data = self.load_url(url, parent)
        if data is None:
            return None

        try:
            schema = json.loads(data)
        except ValueError:
            msg = "failed to load json schema '%s':\n%s"
            warnings.warn(msg % (url, traceback.format_exc()))
            schema = None

        return schema

    def _bind_observers(self):
        """ Bind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        point.updated.bind(self._on_loaders_point_updated)

    def _unbind_observers(self):
        """ Unbind the observers to the plugin extension points.

        """
        point = self.workbench.get_extension_point(LOADERS_POINT)
        point.updated.unbind(self._on_loaders_point_updated)

    def _on_loaders_point_updated(self, change):
        """ An observer callback for the url loaders extension point.

        This observer clears the loaders map of any stale scheme.

        """
        event = change['value']
        for extension in event.removed + event.added:
            scheme = extension.config[u'scheme']
            self._loaders.pop(scheme.lower(), None)
