#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A collection of workbench utility classes and functions.

This module should not be used directly by user code. It exists solely
to keep the primary Workbench namespace clean and easy to understand
for the developer.

"""
from collections import defaultdict
import os
import traceback
import warnings

from atom.api import Atom, Typed

from .extension import Extension
from .extension_object import ExtensionObject
from .extension_point import ExtensionPoint
from .plugin import Plugin
from .plugin_manifest import PluginManifest


SCHEMA_URL = os.path.abspath(__file__)
SCHEMA_URL = os.path.dirname(SCHEMA_URL)
SCHEMA_URL = os.path.join(SCHEMA_URL, 'plugins', 'schemas', 'plugin.json')
SCHEMA_URL = 'file://%s' % SCHEMA_URL.replace('\\', '/')


class WorkbenchContext(Atom):
    """ A class which stores the workbench state.

    """
    #: A mapping of plugin id to PluginManifest.
    manifests = Typed(dict, ())

    #: A mapping of plugin id to Plugin instance.
    plugins = Typed(dict, ())

    #: A mapping of extension point id to ExtensionPoint.
    extension_points = Typed(dict, ())

    #: A mapping of extension id to Extension.
    extensions = Typed(dict, ())

    #: A mapping of extension point id to set of Extensions.
    contributions = Typed(defaultdict, (set,))


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


def add_extension_points(ctxt, extension_points):
    """ Add extension points to the workbench context.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context to which to add the extension points.

    extension_points : list
        The list of ExtensionPoints to add to the context.

    Returns
    -------
    result : list
        The list of ExtensionPoints which were successfully added.

    """
    added = []
    for point in extension_points:
        if add_extension_point(ctxt, point):
            added.append(point)
    return added


def add_extension_point(ctxt, point):
    """ Add an extension point to the workbench.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context to which to add the extension point.

    point : ExtensionPoint
        The ExtensionPoint to add to the context.

    Returns
    -------
    result : bool
        True if the point was added successfully, False otherwise.

    """
    point_id = point.qualified_id
    if point_id in ctxt.extension_points:
        msg = "The extension point '%s' is already registered. "
        msg += "The duplicate extension point will be ignored."
        warnings.warn(msg % point_id)
        return False

    ctxt.extension_points[point_id] = point
    if point_id in ctxt.contributions:
        to_add = list(ctxt.contributions[point_id])
        #update_extension_point(point, [], to_add)

    return True


def remove_extension_points(ctxt, extension_points):
    """ Remove extension points from the workbench context.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context which holds the extension points.

    extension_points : list
        The list of ExtensionPoints to remove from the context.

    Returns
    -------
    result : list
        The list of ExtensionPoints which were successfully removed.

    """
    removed = []
    for point in extension_points:
        if remove_extension_point(ctxt, point):
            removed.append(point)
    return removed


def remove_extension_point(ctxt, point):
    """ Remove an extension point from the workbench.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context which holds the extension point.

    point : ExtensionPoint
        The ExtensionPoint to remove from the context.

    Returns
    -------
    result : bool
        True if the point was removed successfully, False otherwise.

    """
    point_id = point.qualified_id
    if point_id not in ctxt.extension_points:
        msg = "The extension point '%s' is not registered."
        warnings.warn(msg % point_id)
        return False

    del ctxt.extension_points[point_id]
    if point_id in ctxt.contributions:
        to_remove = list(ctxt.contributions.pop(point_id))
        #update_extension_point(point_id, to_remove, [])

    return True


def add_extensions(ctxt, extensions):
    """ Add extensions to a workbench context.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context to which to add the extensions.

    extensions : list
        The list of Extensions to add to the workbench.

    """
    grouped = defaultdict(list)
    for extension in extensions:
        ext_id = extension.qualified_id
        if ext_id in ctxt.extensions:
            msg = "The extension '%s' is already registered. "
            msg += "The duplicate extension will be ignored."
            warnings.warn(msg % ext_id)
            continue
        ctxt.extensions[ext_id] = extension
        grouped[extension.point].append(extension)

    for point_id, exts in grouped.iteritems():
        ctxt.contributions[point_id].update(exts)
        #self._update_extension_point(point_id, [], exts)


def remove_extensions(ctxt, extensions):
    """ Remove extensions from a workbench context.

    Parameters
    ----------
    ctxt : WorkbenchContext
        The context to which to add the extensions.

    extensions : list
        The list of Extensions to remove from the context.

    """
    grouped = defaultdict(list)
    for extension in extensions:
        ext_id = extension.qualified_id
        if ext_id not in ctxt.extensions:
            msg = "The extension '%s' is not registered."
            warnings.warn(msg % ext_id)
            continue
        del ctxt.extensions[ext_id]
        grouped[extension.point].append(extension)

    for point_id, exts in grouped.iteritems():
        ctxt.contributions[point_id].difference_update(exts)
        #self._update_extension_point(point_id, exts, [])

def update_extension_point(point, to_remove, to_add):
    pass
