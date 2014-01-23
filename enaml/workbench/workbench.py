#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
try:
    import simplejson as json  # stdlib json is slow in py2.6
except ImportError:
    import json

import warnings

from atom.api import Atom, Typed

from .extension_registry import ExtensionRegistry
from .plugin import Plugin


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class is used for managing the lifecycle of plugins. It does
    not provide any UI functionality. Such behavior must be supplied
    by a subclass, such as the enaml.studio.Studio class.

    """
    def register(self, data):
        """ Register a plugin with the workbench.

        Parameters
        ----------
        data : str or unicode
            The string of json data for the plugin manifest. If this
            is not a unicode string, it must be encoded in UTF-8.

        """
        pass

    def unregister(self, plugin_id):
        """ Remove a plugin from the workbench.

        This will remove the extension points and extensions from the
        workbench, and stop the plugin if it was activated.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        """
        pass

    def get_manifest(self, plugin_id):
        """ Get the plugin manifest for a given plugin id.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        Returns
        -------
        result : PluginManifest or None
            The manifest for the plugin of interest, or None if it does
            not exist.

        """
        return self._manifests.get(plugin_id)

    def get_plugin(self, plugin_id, force_create=True):
        """ Get the plugin object for a given plugin id.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        force_create : bool, optional
            Whether to automatically import and start the plugin object
            if it is not already active. The default is True.

        Returns
        -------
        result : Plugin or None
            The plugin of interest, or None if it does not exist and/or
            could not be created.

        """
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]
        manifest = self._manifests.get(plugin_id)
        if manifest is None:
            msg = "manifest for plugin '%s' is not registered"
            warnings.warn(msg % plugin_id)
            return None
        if not force_create:
            return None
        plugin = self._create_plugin(manifest)
        self._plugins[plugin_id] = plugin
        return plugin

    def import_object(self, path):
        """ Import an object from a dot separated path.

        Parameters
        ----------
        path : unicode
            A dot separated path of the form 'pkg.module.item' which
            represents the import path to the object.

        Returns
        -------
        result : object
            The item pointed to by the path. An import error will be
            raised if the item cannot be imported.

        """
        if u'.' not in path:
            return __import__(path)
        path, item = path.rsplit(u'.', 1)
        mod = __import__(path, globals(), {}, [item])
        try:
            result = getattr(mod, item)
        except AttributeError:
            raise ImportError(u'cannot import name %s' % item)
        return result

    def load_extension_object(self, extension):
        """ Load the implementation object for a given extension.

        This will cause the extension's plugin class to be imported
        and activated unless the plugin is already active.

        Parameters
        ----------
        extension : Extension
            The extension which contains the path to the implementation
            object to load.

        Returns
        -------
        result : object or None
            The implementation object defined by the extension, or
            None if it could not be loaded.

        """
        # ensure the extension's plugin is activated
        self.get_plugin(extension.plugin_id)
        try:
            result = self.import_object(extension.object)
        except ImportError:
            msg = "failed to load extension object '%s'"
            warnings.warn(msg % extension.object)
            result = None
        return result

    def get_extension_point(self, extension_point_id):
        """ Get the extension point associated with an id.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        Returns
        -------
        result : ExtensionPoint or None
            The desired ExtensionPoint or None if it does not exist.

        """
        return self._registry.get_extension_point(extension_point_id)

    def get_extension_points(self):
        """ Get all of the extension points in the registry.

        Returns
        -------
        result : list
            A list of all of the extension points in the registry.

        """
        return self._registry.get_extension_points()

    def get_extension(self, extension_point_id, extension_id):
        """ Get a specific extension contributed to an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        extension_id : unicode
            The fully qualified id of the extension.

        Returns
        -------
        result : Extension or None
            The requested Extension, or None if it does not exist.

        """
        return self._registry.get_extension(extension_point_id, extension_id)

    def get_extensions(self, extension_point_id):
        """ Get the extensions contributed to an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        Returns
        -------
        result : list
            A list of Extensions contributed to the extension point.

        """
        return self._registry.get_extensions(extension_point_id)

    def add_listener(self, extension_point_id, listener):
        """ Add a listener to the specified extension point.

        Listeners are maintained and invoked in sorted order.

        Parameters
        ----------
        extension_point_id : unicode or None
            The fully qualified id of the extension point of interest,
            or None to install the listener for all extension points.

        listener : RegistryEventListener
            The registry listener to add to the registry.

        """
        self._registry.add_listener(extension_point_id, listener)

    def remove_listener(self, extension_point_id, listener):
        """ Remove a listener from the specified extension point.

        Parameters
        ----------
        extension_point_id : unicode or None
            The same identifier used when the listener was added.

        listener : RegistryEventListener
            The listener to remove from the registry.

        """
        self._registry.remove_listener(extension_point_id, listener)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The registry of extension points and extensions.
    _registry = Typed(ExtensionRegistry, ())

    #: A mapping of plugin id to PluginManifest.
    _manifests = Typed(dict, ())

    #: A mapping of plugin id to Plugin instance.
    _plugins = Typed(dict, ())

    def _create_plugin(self, manifest):
        """ Create a plugin instance for the given manifest.

        Parameters
        ----------
        manifest : PluginManifest
            The manifest which describes the plugin to create.

        Returns
        -------
        result : Plugin or None
            A new Plugin instance or None if one could not be created.

        """
        class_path = manifest.cls
        if not class_path:
            return Plugin()
        try:
            plugin_cls = self.import_object(class_path)
        except ImportError:
            msg = "failed to import plugin class '%s'"
            warnings.warn(msg % class_path)
            return None
        plugin = plugin_cls()
        if not isinstance(plugin, Plugin):
            msg = "plugin class '%s' created non-Plugin type '%s'"
            warnings.warn(msg % (class_path, type(plugin).__name__))
            return None
        return plugin
