#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from future.builtins import str
from atom.api import Atom, Event, Typed

from .plugin import Plugin


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class is used for managing the lifecycle of plugins. It does
    not provide any plugins of its own. The UIWorkbench subclass adds
    the 'core' and 'ui' workbench plugins by default.

    """
    #: An event fired when a plugin is added to the workbench. The
    #: payload will be the plugin id.
    plugin_added = Event(str)

    #: An event fired when a plugin is removed from the workbench. The
    #: payload will be the plugin id.
    plugin_removed = Event(str)

    #: An event fired when an extension point is added to the
    #: workbench. The payload will be the fully qualified id of the
    #: extension point.
    extension_point_added = Event(str)

    #: An event fired when an extension point is removed from the
    #: workbench. The payload will be the fully qualified id of the
    #: extension point.
    extension_point_removed = Event(str)

    def register(self, manifest):
        """ Register a plugin with the workbench.

        Parameters
        ----------
        manifest : PluginManifest
            The plugin manifest to register with the workbench.

        """
        plugin_id = manifest.id
        if plugin_id in self._manifests:
            msg = "plugin '%s' is already registered"
            raise ValueError(msg % plugin_id)

        self._manifests[plugin_id] = manifest
        manifest.workbench = self
        if not manifest.is_initialized:
            manifest.initialize()

        self._add_extensions(manifest.extensions)
        self._add_extension_points(manifest.extension_points)

        self.plugin_added(plugin_id)

    def unregister(self, plugin_id):
        """ Remove a plugin from the workbench.

        This will remove the extension points and extensions from the
        workbench, and stop the plugin if it was activated.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        """
        manifest = self._manifests.get(plugin_id)
        if manifest is None:
            msg = "plugin '%s' is not registered"
            raise ValueError(msg % plugin_id)

        plugin = self._plugins.pop(plugin_id, None)
        if plugin is not None:
            plugin.stop()
            plugin.manifest = None

        self._remove_extensions(manifest.extensions)
        self._remove_extension_points(manifest.extension_points)

        del self._manifests[plugin_id]
        manifest.workbench = None
        if manifest.is_initialized:
            manifest.destroy()

        self.plugin_removed(plugin_id)

    def get_manifest(self, plugin_id):
        """ Get the plugin manifest for a given plugin id.

        Parameters
        ----------
        plugin_id : unicode
            The identifier of the plugin of interest.

        Returns
        -------
        result : PluginManifest or None
            The manifest for the plugin of interest, or None if it
            does not exist.

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
            msg = "plugin '%s' is not registered"
            raise ValueError(msg % plugin_id)

        if not force_create:
            return None

        plugin = manifest.factory()
        if not isinstance(plugin, Plugin):
            msg = "plugin '%s' factory created non-Plugin type '%s'"
            raise TypeError(msg % (plugin_id, type(plugin).__name__))

        self._plugins[plugin_id] = plugin
        plugin.manifest = manifest
        plugin.start()
        return plugin

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
        return self._extension_points.get(extension_point_id)

    def get_extension_points(self):
        """ Get all of the extension points in the workbench.

        Returns
        -------
        result : list
            A list of all of the extension points in the workbench.

        """
        return list(self._extension_points.values())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of plugin id to PluginManifest.
    _manifests = Typed(dict, ())

    #: A mapping of plugin id to Plugin instance.
    _plugins = Typed(dict, ())

    #: A mapping of extension point id to ExtensionPoint.
    _extension_points = Typed(dict, ())

    #: A mapping of extension id to Extension.
    _extensions = Typed(dict, ())

    #: A mapping of extension point id to set of Extensions.
    _contributions = Typed(defaultdict, (set,))

    def _add_extension_points(self, extension_points):
        """ Add extension points to the workbench.

        Parameters
        ----------
        extension_points : list
            The list of ExtensionPoints to add to the workbench.

        """
        for point in extension_points:
            self._add_extension_point(point)

    def _add_extension_point(self, point):
        """ Add an extension point to the workbench.

        Parameters
        ----------
        point : ExtensionPoint
            The ExtensionPoint to add to the workbench.

        """
        point_id = point.qualified_id
        if point_id in self._extension_points:
            msg = "extension point '%s' is already registered"
            raise ValueError(msg % point_id)

        self._extension_points[point_id] = point
        if point_id in self._contributions:
            to_add = self._contributions[point_id]
            self._update_extension_point(point, [], to_add)

        self.extension_point_added(point_id)

    def _remove_extension_points(self, extension_points):
        """ Remove extension points from the workbench.

        Parameters
        ----------
        extension_points : list
            The list of ExtensionPoints to remove from the workbench.

        """
        for point in extension_points:
            self._remove_extension_point(point)

    def _remove_extension_point(self, point):
        """ Remove an extension point from the workbench.

        Parameters
        ----------
        point : ExtensionPoint
            The ExtensionPoint to remove from the workbench.

        """
        point_id = point.qualified_id
        if point_id not in self._extension_points:
            msg = "extension point '%s' is not registered"
            raise ValueError(msg % point_id)

        del self._extension_points[point_id]
        if point_id in self._contributions:
            to_remove = self._contributions.pop(point_id)
            self._update_extension_point(point, to_remove, [])

        self.extension_point_removed(point_id)

    def _add_extensions(self, extensions):
        """ Add extensions to the workbench.

        Parameters
        ----------
        extensions : list
            The list of Extensions to add to the workbench.

        """
        grouped = defaultdict(set)
        for extension in extensions:
            ext_id = extension.qualified_id
            if ext_id in self._extensions:
                msg = "extension '%s' is already registered"
                raise ValueError(msg % ext_id)
            self._extensions[ext_id] = extension
            grouped[extension.point].add(extension)

        for point_id, exts in grouped.items():
            self._contributions[point_id].update(exts)
            if point_id in self._extension_points:
                point = self._extension_points[point_id]
                self._update_extension_point(point, (), exts)

    def _remove_extensions(self, extensions):
        """ Remove extensions from a workbench.

        Parameters
        ----------
        extensions : list
            The list of Extensions to remove from the workbench.

        """
        grouped = defaultdict(set)
        for extension in extensions:
            ext_id = extension.qualified_id
            if ext_id not in self._extensions:
                msg = "extension '%s' is not registered"
                raise ValueError(msg % ext_id)
            del self._extensions[ext_id]
            grouped[extension.point].add(extension)

        for point_id, exts in grouped.items():
            self._contributions[point_id].difference_update(exts)
            if point_id in self._extension_points:
                point = self._extension_points[point_id]
                self._update_extension_point(point, exts, ())

    def _update_extension_point(self, point, to_remove, to_add):
        """ Update an extension point with delta extension objects.

        Parameters
        ----------
        point : ExtensionPoint
            The extension point of interest.

        to_remove : iterable
            The Extension objects to remove from the point.

        to_add : iterable
            The Extension objects to add to the point.

        """
        if to_remove or to_add:
            extensions = set(point.extensions)
            extensions.difference_update(to_remove)
            extensions.update(to_add)
            key = lambda ext: ext.rank
            point.extensions = tuple(sorted(extensions, key=key))
