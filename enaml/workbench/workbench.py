#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
import json
import warnings

from atom.api import Atom, Event, Typed

from . import wbu


CORE_PLUGIN = u'enaml.workbench.core'


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class is used for managing the lifecycle of plugins. It does
    not provide any UI functionality. Such behavior must be supplied
    by a subclass, such as the enaml.studio.Studio class.

    """
    #: An event fired when a plugin is added to the workbench. The
    #: payload will be the plugin id.
    plugin_added = Event(unicode)

    #: An event fired when a plugin is removed from the workbench. The
    #: payload will be the plugin id.
    plugin_removed = Event(unicode)

    #: An event fired when an extension point is added to the
    #: workbench. The payload will be the fully qualified id of the
    #: extension point.
    extension_point_added = Event(unicode)

    #: An event fired when an extension point is removed from the
    #: workbench. The payload will be the fully qualified id of the
    #: extension point.
    extension_point_removed = Event(unicode)

    def __init__(self, **kwargs):
        """ Initialize a Workbench.

        This intializer bootstraps the core workbench plugin.

        """
        super(Workbench, self).__init__(**kwargs)
        self._init_core_plugin()

    def register(self, url):
        """ Register a plugin with the workbench.

        Parameters
        ----------
        url : unicode
            A url containing the absolute path to the JSON plugin data.
            The url scheme must be supported by a registered plugin.

        """
        core = self.get_plugin(CORE_PLUGIN)
        data = core.load_url(url)
        if data is None:
            raise RuntimeError('failed to load plugin JSON data')

        item = json.loads(data)
        core.validate(item, wbu.SCHEMA_URL)

        plugin_id = item[u'id']
        if plugin_id in self._manifests:
            msg = "The plugin '%s' is already registered. "
            msg += "The duplicate plugin will be ignored."
            warnings.warn(msg % plugin_id)
            return

        manifest = wbu.create_manifest(url, item)
        self._manifests[plugin_id] = manifest
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
            warnings.warn(msg % plugin_id)
            return

        plugin = self._plugins.pop(plugin_id, None)
        if plugin is not None:
            plugin.stop()
            plugin.workbench = None
            plugin.manifest = None

        self._remove_extensions(manifest.extensions)
        self._remove_extension_points(manifest.extension_points)
        del self._manifests[plugin_id]

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
            warnings.warn(msg % plugin_id)
            return None

        if not force_create:
            return None

        plugin = wbu.create_plugin(manifest)
        self._plugins[plugin_id] = plugin
        if plugin is None:
            return None

        plugin.manifest = manifest
        plugin.workbench = self
        plugin.start()
        return plugin

    def create_extension_object(self, extension):
        """ Create the implementation object for a given extension.

        The relevant ExtensionObject class will be imported using the
        'class' property of the extension, so this must exist. It will
        then be instatiated using the default constructor and validated
        against the interface defined by the relevant extension point.

        This will cause the extension's plugin class to be imported and
        activated unless the plugin is already active.

        Parameters
        ----------
        extension : Extension
            The extension which contains the path to the object class.

        Returns
        -------
        result : ExtensionObject or None
            The newly created extension object, or None if one could
            not be created.

        """
        ext_id = extension.qualified_id
        if ext_id not in self._extensions:
            msg = "Cannot create extension object. "\
                  "Extension '%s' is not registered."
            warnings.warn(msg % ext_id)
            return None

        point_id = extension.point
        point = self._extension_points.get(point_id)
        if point is None:
            msg = "Cannot create extension object. "\
                  "Extension point '%s' is not registered."
            warnings.warn(msg % point_id)
            return None

        if not extension.cls:
            msg = "Cannot create extension object. "\
                  "Extension '%s' does not declare a class path."
            warnings.warn(msg % ext_id)
            return None

        self.get_plugin(extension.plugin_id)  # ensure plugin is activated
        ext_obj = wbu.create_extension_object(point, extension)
        if ext_obj is None:
            return None

        ext_obj.workbench = self
        ext_obj.extension = extension
        ext_obj.initialize()
        return ext_obj

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
        return self._extension_points.values()

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

    def _init_core_plugin(self):
        """ Initialize and register the core plugin manifest.

        This bypasses the traditional registration, since that requires
        the core plugin to exist. The Core plugin must be assumed to be
        correct, since that plugin is responsible for JSON validation.

        """
        manifest = wbu.load_core_manifest()
        self._manifests[manifest.id] = manifest
        for point in manifest.extension_points:
            self._extension_points[point.qualified_id] = point
        for extension in manifest.extensions:
            self._extensions[extension.qualified_id] = extension
            self._contributions[extension.point].add(extension)

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
            msg = "The extension point '%s' is already registered. "
            msg += "The duplicate extension point will be ignored."
            warnings.warn(msg % point_id)
            return

        self._extension_points[point_id] = point
        if point_id in self._contributions:
            to_add = list(self._contributions[point_id])
            wbu.update_extension_point(point, [], to_add)

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
            msg = "The extension point '%s' is not registered."
            warnings.warn(msg % point_id)
            return

        del self._extension_points[point_id]
        if point_id in self._contributions:
            to_remove = list(self._contributions.pop(point_id))
            wbu.update_extension_point(point, to_remove, [])

        self.extension_point_removed(point_id)

    def _add_extensions(self, extensions):
        """ Add extensions to the workbench.

        Parameters
        ----------
        extensions : list
            The list of Extensions to add to the workbench.

        """
        grouped = defaultdict(list)
        for extension in extensions:
            ext_id = extension.qualified_id
            if ext_id in self._extensions:
                msg = "The extension '%s' is already registered. "
                msg += "The duplicate extension will be ignored."
                warnings.warn(msg % ext_id)
                continue
            self._extensions[ext_id] = extension
            grouped[extension.point].append(extension)

        for point_id, exts in grouped.iteritems():
            self._contributions[point_id].update(exts)
            if point_id in self._extension_points:
                point = self._extension_points[point_id]
                wbu.update_extension_point(point, [], exts)

    def _remove_extensions(self, extensions):
        """ Remove extensions from a workbench.

        Parameters
        ----------
        extensions : list
            The list of Extensions to remove from the workbench.

        """
        grouped = defaultdict(list)
        for extension in extensions:
            ext_id = extension.qualified_id
            if ext_id not in self._extensions:
                msg = "The extension '%s' is not registered."
                warnings.warn(msg % ext_id)
                continue
            del self._extensions[ext_id]
            grouped[extension.point].append(extension)

        for point_id, exts in grouped.iteritems():
            self._contributions[point_id].difference_update(exts)
            if point_id in self._extension_points:
                point = self._extension_points[point_id]
                wbu.update_extension_point(point, exts, [])
