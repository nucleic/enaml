#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A module of utility functions for the Workbench.

This module exists solely to make the workbench module cleaner and easier
to understand for the developer. This module should never be consumed by
user code and is subject to change without notice. We mean it!

"""
import json
import os
import traceback
import warnings

from .extension import Extension
from .extension_object import ExtensionObject
from .extension_point import ExtensionPoint, ExtensionPointEvent
from .plugin import Plugin
from .plugin_manifest import PluginManifest


SCHEMA_URL = os.path.abspath(__file__)
SCHEMA_URL = os.path.dirname(SCHEMA_URL)
SCHEMA_URL = os.path.join(SCHEMA_URL, 'plugins', 'schemas', 'manifest.json')
SCHEMA_URL = 'file://%s' % SCHEMA_URL.replace('\\', '/')


def import_object(path):
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


def create_manifest(url, item):
    """ Create a plugin manifest from a loaded JSON object.

    Parameters
    ----------
    url : unicode
        The url which was used to load the data.

    item : dict
        The dictionary loaded from the plugin JSON file.

    Returns
    -------
    result : PluginManifest
        The plugin manifest object for the given data.

    """
    points = []
    extensions = []
    plugin_id = item[u'id']
    for data in item.get(u'extensionPoints', ()):
        points.append(ExtensionPoint(plugin_id, data))
    for data in item.get(u'extensions', ()):
        extensions.append(Extension(plugin_id, data))
    return PluginManifest(url, item, points, extensions)


def create_plugin(manifest):
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
        plugin_cls = import_object(path)
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


def load_interface(point):
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
        iface = import_object(path)
    except ImportError:
        msg = "failed to load interface class '%s':\n%s"
        warnings.warn(msg % (path, traceback.format_exc()))
        return ExtensionObject

    if not isinstance(iface, type) or not issubclass(iface, ExtensionObject):
        msg = "interface class '%s' does not subclass ExtensionObject"
        warnings.warn(msg % path)
        return ExtensionObject

    return iface


def create_extension_object(point, extension):
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
        object_class = import_object(path)
    except ImportError:
        msg = "failed to load extension class '%s':\n%s"
        warnings.warn(msg % (path, traceback.format_exc()))
        return None

    obj = object_class()
    iface = load_interface(point)
    if not isinstance(obj, iface):
        msg = "extension class '%s' created non-%s type '%s'"
        warnings.warn(msg % (path, iface.__name__, type(obj).__name__))
        return None

    return obj


def filter_extensions(workbench, point, extensions):
    """ Filter a list of extensions for valid configs.

    A warning will be emitted for extensions with invalid configs.

    Parameters
    ----------
    workbench : Workbench
        The workbench for which the extensions are being validated.

    point : ExtensionPoint
        The extension point to which the extensions are contributing.

    extensions : list
        The list of Extension objects with configs to validate.

    Returns
    -------
    result : list
        The list of valid extension objects.

    """
    schema_url = point.schema
    if not schema_url:
        return extensions

    plugin_url = workbench.get_manifest(point.plugin_id).url
    core = workbench.get_plugin('enaml.workbench.core')

    def check_config(extension):
        try:
            core.validate(extension.config, schema_url, plugin_url)
        except Exception:
            ext_id = extension.qualified_id
            msg = "config for extension '%s' is invalid:\n%s"
            warnings.warn(msg % (ext_id, traceback.format_exc()))
            return False
        return True

    return filter(check_config, extensions)


def update_extension_point(workbench, point, to_remove, to_add):
    """ Update an extension point with delta extension objects.

    This will update the extension point's extensions according to
    the deltas and emit an update event on the point. Newly added
    extensions will be validated against the extension point schema
    if one is available.

    Parameters
    ----------
    workbench : Workbench
        The workbench which is updating the extension point. This is
        necessary to validate the newly added extensions to the
        extension point.

    point : ExtensionPoint
        The extension point of interest.

    to_remove : list
        The list of Extension objects to remove from the point.

    to_add : list
        The list of Extension objects to add to the point.

    """
    extensions = set(point._extensions)

    removed = []
    if to_remove:
        to_remove = [ext for ext in to_remove if ext in extensions]
        extensions.difference_update(to_remove)
        removed.extend(to_remove)

    added = []
    if to_add:
        to_add = [ext for ext in to_add if ext not in extensions]
        filtered = filter_extensions(workbench, point, to_add)
        extensions.update(filtered)
        added.extend(filtered)

    if removed or added:
        key = lambda ext: ext.rank
        point._extensions = sorted(extensions, key=key)
        event = ExtensionPointEvent(removed=removed, added=added)
        point.updated(event)


def load_core_manifest():
    """ Load the manifest for the core plugin.

    The extension points declared by the manifest will be automatically
    populated with any relevant extensions declared by the core plugin
    itself. No extension point events will be emitted.

    Returns
    -------
    result : PluginManifest
        The manifest for the core plugin.

    """
    path = os.path.abspath(__file__)
    path = os.path.dirname(path)
    path = os.path.join(path, 'plugins', 'core.json')
    url = 'file://%s' % (path.replace('\\', '/'))

    with open(path, 'rb') as f:
        data = f.read()
    item = json.loads(data)
    manifest = create_manifest(url, item)

    points = {}
    for point in manifest.extension_points:
        point_id = point.qualified_id
        points[point_id] = (point, [])

    for extension in manifest.extensions:
        point_id = extension.point
        if point_id in points:
            points[point_id][1].append(extension)

    key = lambda ext: ext.rank
    for point, exts in points.itervalues():
        point._extensions = sorted(exts, key=key)

    return manifest
