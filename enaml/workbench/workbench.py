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
import warnings

from atom.api import Atom, Typed

from .extension import Extension
from .extension_object import ExtensionObject
from .extension_point import ExtensionPoint
from .plugin import Plugin
from .plugin_manifest import PluginManifest
from .validation import validate


SCHEMA_PATH = os.path.abspath(__file__)
SCHEMA_PATH = os.path.dirname(SCHEMA_PATH)
SCHEMA_PATH = os.path.join(SCHEMA_PATH, 'schema.json')


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
            The JSON plugin manifest data. If this is a str, it must be
            encoded in UTF-8 or plain ASCII.

        """
        root = json.loads(data)
        validate(root, SCHEMA_PATH)

        plugin_id = root[u'id']
        if plugin_id in self._manifests:
            msg = "The plugin '%s' is already registered. "
            msg += "The duplicate plugin will be ignored."
            warnings.warn(msg % plugin_id)
            return

        points = []
        extensions = []
        for data in root.get(u'extensionPoints', ()):
            points.append(ExtensionPoint(plugin_id, data))
        for data in root.get(u'extensions', ()):
            extensions.append(Extension(plugin_id, data))
        manifest = PluginManifest(root, points, extensions)

        self._manifests[plugin_id] = manifest
        self._add_extension_points(points)
        self._add_extensions(extensions)

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
            msg = "plugin manifest for plugin '%s' is not registered"
            warnings.warn(msg % plugin_id)
            return None

        if not force_create:
            return None

        plugin = self._create_plugin(manifest)
        self._plugins[plugin_id] = plugin
        if plugin is None:
            return None

        plugin.manifest = manifest
        plugin.workbench = self
        plugin.start()
        return plugin

    def create_extension_object(self, extension):
        """ Create the implementation object for a given extension.

        This will cause the extension's plugin class to be imported
        and activated unless the plugin is already active.

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
        self.get_plugin(extension.plugin_id)  # ensure plugin is activated
        obj = self._create_extension_object(extension)
        if obj is None:
            return None

        obj.workbench = self
        obj.extension = extension
        obj.initialize()
        return obj

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

    #: A mapping of extension point id to extension point.
    _extension_points = Typed(dict, ())

    #: A mapping of extension point id to list of extensions.
    _contributions = Typed(dict, ())

    @staticmethod
    def _import_object(path):
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
        mod = __import__(path, {}, {}, [item])
        try:
            result = getattr(mod, item)
        except AttributeError:
            raise ImportError(u'cannot import name %s' % item)
        return result

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

        # TODO add any registered extensions to the point.
        self._extension_points[point_id] = point

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

        # TODO remove any extensions from the point.
        del self._extension_points[point_id]

    def _add_extensions(self, extensions):
        """ Add extensions to the workbench.

        Parameters
        ----------
        extensions : list
            The list of Extensions to add to the workbench.

        """
        # TODO validate the extensions against the schema
        # key = lambda ext: ext.point
        # for point_id, extensioniter in groupby(extensions, key):
        #     added = []
        #     for extension in extensioniter:
        #         ext_id = extension.qualified_id
        #         if ext_id and ext_id in self._extension_ids:
        #             msg = "The extension '%s' is already registered. "
        #             msg += "The duplicate extension will be ignored."
        #             warnings.warn(msg % ext_id)
        #         else:
        #             if ext_id:
        #                 self._extension_ids.add(ext_id)
        #             added.append(extension)
        #     if added:
        #         self._contributions[point_id].extend(added)
        #         # method_name = 'extensions_added'
        #         # self._invoke_listeners(point_id, method_name, added)

    def _remove_extensions(self, extensions):
        """ Remove extensions from the workbench.

        Parameters
        ----------
        extensions : list
            The list of the Extensions to remove from the workbench.

        """
        # key = lambda ext: ext.point
        # for point_id, extensioniter in groupby(extensions, key):
        #     current = self._contributions.get(point_id, [])
        #     removed = []
        #     for extension in extensioniter:
        #         ext_id = extension.qualified_id
        #         try:
        #             current.remove(extension)
        #         except ValueError:
        #             msg = "The extension '%s' is not registered."
        #             warnings.warn(msg % ext_id)
        #         else:
        #             self._extension_ids.discard(ext_id)
        #             removed.append(extension)
        #     # if removed:
        #     #     method_name = 'extensions_removed'
        #     #     self._invoke_listeners(point_id, method_name, removed)

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
        path = manifest.cls
        if not path:
            return Plugin()

        try:
            plugin_cls = self._import_object(path)
        except ImportError:
            msg = "failed to import plugin class '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            return None

        plugin = plugin_cls()
        if not isinstance(plugin, Plugin):
            msg = "plugin '%s' created non-Plugin type '%s'"
            warnings.warn(msg % (path, type(plugin).__name__))
            return None

        return plugin

    def _create_extension_object(self, extension):
        """ Create the implementation object for a given extension.

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
        path = extension.cls
        try:
            extension_class = self._import_object(path)
        except ImportError:
            msg = "failed to load extension class '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            return None

        obj = extension_class()
        if not isinstance(obj, ExtensionObject):
            msg = "extension '%s' created non-ExtensionObject type '%s'"
            warnings.warn(msg % (path, type(obj).__name__))
            return None

        return obj
