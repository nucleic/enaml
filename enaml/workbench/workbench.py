#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from .extension_registry import ExtensionRegistry


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class is used for managing the lifecycle of plugins. It does
    not provide any UI functionality. Such behavior must be supplied
    by a subclass, such as the enaml.studio.Studio class.

    """
    #: The registry of extension points and extensions.
    _registry = Typed(ExtensionRegistry, ())

    #: A mapping of plugin id to tuple of (manifest, plugin).
    _plugins = Typed(dict, ())

    def add_plugin(self, manifest):
        """ Add a plugin with the workbench.

        If a plugin with the same plugin identifier has already been
        added to the workbench, a ValueError will be raised.

        Parameters
        ----------
        manifest : PluginManifest
            The manifest for the plugin to add to the workbench.

        """
        if manifest.id in self._plugins:
            msg = "plugin '%s' already registered"
            raise ValueError(msg % manifest.id)
        self._plugins[manifest.id] = (manifest, None)

    def remove_plugin(self, plugin_id):
        """ Remove a plugin from the workbench.

        This will stop the plugin and remove its extension points and
        extensions. If the plugin was not previously added to the
        workbench, this method is a no-op.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin.

        """
        item = self._plugins.pop(plugin_id, None)
        if item is None:
            return
        manifest, plugin = item
        # XXX

    def get_plugin(self, plugin_id, force=True):
        """ Get the plugin object for a given plugin id.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        force : bool, optional
            Whether to force create the plugin object from the factory
            provided by the manifest. The default is True and will cause
            the plugin to be created and started the first time it is
            requested.

        Returns
        -------
        result : Plugin None
            The plugin of interest, or None if it does not exist and
            could not be created.

        """

    def get_extension_point(self, extension_point_id):
        """ Get the extension point associated with an id.

        Parameters
        ----------
        extension_point_id : unicode
            The unique identifier for the extension point of interest.

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
            The identifier of the extension point to of interest.

        extension_id : unicode
            The identifier of the extension of interest.

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
            The identifier of the extension point to of interest.

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
            The globally unique identifier of the extension point, or
            None to install the listener for all extension points.

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

        listener : callable
            The listener to remove from the registry.

        """
        self._registry.remove_listener(extension_point_id, listener)
