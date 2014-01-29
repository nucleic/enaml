#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
import json
import os
import traceback
import warnings

from atom.api import Atom, Event, Typed

from .extension import Extension
from .extension_object import ExtensionObject
from .extension_point import ExtensionPoint, ExtensionPointEvent
from .plugin import Plugin
from .plugin_manifest import PluginManifest
from .validation import validate


SCHEMA_PATH = os.path.abspath(__file__)
SCHEMA_PATH = os.path.dirname(SCHEMA_PATH)
SCHEMA_PATH = os.path.join(SCHEMA_PATH, 'plugin_schema.json')


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


def _create_plugin(manifest):
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
        plugin_cls = _import_object(path)
    except ImportError:
        msg = "failed to import plugin class '%s':\n%s"
        warnings.warn(msg % (path, traceback.format_exc()))
        return None

    plugin = plugin_cls()
    if not isinstance(plugin, Plugin):
        msg = "plugin class '%s' created non-Plugin type '%s'"
        warnings.warn(msg % (path, type(plugin).__name__))
        return None

    return plugin


def _load_interface(point):
    """ Load the interface declared by an extension point.

    If the extension point does not declare an interface, the base
    ExtensionObject class will be returned.

    Parameters
    ----------
    point : ExtensionPoint
        The extension point of interest.

    Returns
    -------
    result : ExtensionObject subclass
        The interface declared by the extension point.

    """
    path = point.interface
    if not path:
        return ExtensionObject

    try:
        iface = _import_object(path)
    except ImportError:
        msg = "failed to load interface class '%s':\n%s"
        warnings.warn(msg % (path, traceback.format_exc()))
        return ExtensionObject

    if not isinstance(iface, type) or not issubclass(iface, ExtensionObject):
        msg = "interface class '%s' does not subclass ExtensionObject"
        warnings.warn(msg % path)
        return ExtensionObject

    return iface


def _create_extension_object(point, extension):
    """ Create the implementation object for a given extension.

    Parameters
    ----------
    point : ExtensionPoint
        The extension point to which the extension contributes.

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
        object_class = _import_object(path)
    except ImportError:
        msg = "failed to load extension class '%s':\n%s"
        warnings.warn(msg % (path, traceback.format_exc()))
        return None

    obj = object_class()
    iface = _load_interface(point)
    if not isinstance(obj, iface):
        msg = "extension class '%s' created non-%s type '%s'"
        warnings.warn(msg % (path, iface.__name__, type(obj).__name__))
        return None

    return obj


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

    def register(self, data):
        """ Register a plugin with the workbench.

        Parameters
        ----------
        data : str or unicode
            The JSON plugin manifest data. If this is a str, it must
            be encoded in UTF-8 or plain ASCII.

        """
        # TODO unify validation
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

        plugin = _create_plugin(manifest)
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

        self.get_plugin(extension.plugin_id)  # ensure plugin is activated
        obj = _create_extension_object(point, extension)
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
            msg = "The extension point '%s' is already registered. "
            msg += "The duplicate extension point will be ignored."
            warnings.warn(msg % point_id)
            return

        self._extension_points[point_id] = point
        if point_id in self._contributions:
            to_add = list(self._contributions[point_id])
            self._update_extension_point(point_id, [], to_add)

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
            self._update_extension_point(point_id, to_remove, [])

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
            self._update_extension_point(point_id, [], exts)

    def _remove_extensions(self, extensions):
        """ Remove extensions from the workbench.

        Parameters
        ----------
        extensions : list
            The list of the Extensions to remove from the workbench.

        """
        grouped = defaultdict(list)
        for extension in extensions:
            ext_id = extension.qualified_id
            if ext_id not in self._extension:
                msg = "The extension '%s' is not registered."
                warnings.warn(msg % ext_id)
                continue
            del self._extensions[ext_id]
            grouped[extension.point].append(extension)

        for point_id, exts in grouped.iteritems():
            self._contributions[point_id].difference_update(exts)
            self._update_extension_point(point_id, exts, [])

    def _update_extension_point(self, point_id, to_remove, to_add):
        """ Update an extension point will delta extension objects.

        This will update the extension point's extensions according to
        the deltas and emit an update event on the point. Newly added
        extensions will be validated against the extension point schema
        if one is available.

        If the given extension point has not yet been added to the
        workbench, this method is a no-op.

        Parameters
        ----------
        point_id : unicode
            The qualified id of the extension point of interest.

        to_remove : list
            The list of Extension objects to remove from the point.

        to_add : list
            The list of Extension objects to add to the point.

        """
        point = self._extension_points.get(point_id)
        if point is None:
            return
        extensions = set(point._extensions)

        removed = []
        for ext in to_remove:
            if ext in extensions:
                extensions.remove(ext)
                removed.append(ext)

        added = []
        for ext in to_add:
            if ext not in extensions:
                # TODO validate the against the extension point schema
                extensions.add(ext)
                added.append(ext)

        if removed or added:
            key = lambda ext: ext.rank
            point._extensions = sorted(extensions, key=key)
            event = ExtensionPointEvent(removed=removed, added=added)
            point.updated(event)
