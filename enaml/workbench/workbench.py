#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import json
import warnings

from atom.api import Atom, Event, Typed

from . import wbu


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

    #: The private workbench context.
    _context = Typed(wbu.WorkbenchContext, ())

    def __init__(self, **kwargs):
        """ Initialize a Workbench.

        This intializer bootstraps the core workbench plugin.

        """
        super(Workbench, self).__init__(**kwargs)
        #self._impl.load_core_plugin()

    def register(self, url):
        """ Register a plugin with the workbench.

        Parameters
        ----------
        url : unicode
            A url containing the absolute path to the JSON plugin data.
            The url scheme must be supported by a registered plugin.
            The 'file' scheme is supported by default.

        """
        core = self.get_plugin('enaml.workbench.core')
        data = core.load_url(url)
        if data is None:
            raise RuntimeError('failed to load plugin JSON data')

        item = json.loads(data)
        core.validate(item, wbu.SCHEMA_URL)

        ctxt = self._context
        plugin_id = item[u'id']
        if plugin_id in ctxt.manifests:
            msg = "The plugin '%s' is already registered. "
            msg += "The duplicate plugin will be ignored."
            warnings.warn(msg % plugin_id)
            return

        manifest = wbu.create_manifest(url, item)
        ctxt.manifests[plugin_id] = manifest

        added = wbu.add_extension_points(manifest.extension_points)
            self.extension_point_added(point)

        self._add_extension_points(manifest.extension_points)
        self._add_extensions(manifest.extensions)

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
        ctxt = self._context
        manifest = ctxt.manifests.get(plugin_id)
        if manifest is None:
            msg = "plugin '%s' is not registered"
            warnings.warn(msg % plugin_id)
            return

        plugin = ctxt.plugins.pop(plugin_id, None)
        if plugin is not None:
            plugin.stop()
            plugin.workbench = None
            plugin.manifest = None

        removed = self._remove_extensions(manifest.extensions)
        self._remove_extension_points(manifest.extension_points)
        del ctxt.manifests[plugin_id]

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
        return self._context.manifests.get(plugin_id)

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
        ctxt = self._context
        if plugin_id in ctxt.plugins:
            return ctxt.plugins[plugin_id]

        manifest = ctxt.manifests.get(plugin_id)
        if manifest is None:
            msg = "plugin '%s' is not registered"
            warnings.warn(msg % plugin_id)
            return None

        if not force_create:
            return None

        plugin = wbu.create_plugin(manifest)
        ctxt.plugins[plugin_id] = plugin
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
        ctxt = self._context
        ext_id = extension.qualified_id
        if ext_id not in ctxt.extensions:
            msg = "Cannot create extension object. "\
                  "Extension '%s' is not registered."
            warnings.warn(msg % ext_id)
            return None

        point_id = extension.point
        point = ctxt.extension_points.get(point_id)
        if point is None:
            msg = "Cannot create extension object. "\
                  "Extension point '%s' is not registered."
            warnings.warn(msg % point_id)
            return None

        self.get_plugin(extension.plugin_id)  # ensure plugin is activated
        obj = wbu.create_extension_object(point, extension)
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
        return self._context.extension_points.get(extension_point_id)

    def get_extension_points(self):
        """ Get all of the extension points in the workbench.

        Returns
        -------
        result : list
            A list of all of the extension points in the workbench.

        """
        return self._context.extension_points.values()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    # def _load_core_plugin(self):
    #     """ Bootstrap the plugin manifest for the core plugin.

    #     This bypasses the traditional registration, since that requires
    #     the core plugin to exist. The Core plugin must be assumed to be
    #     correct, since it is the plugin responsible for JSON validation.

    #     """
    #     path = os.path.abspath(__file__)
    #     path = os.path.dirnam(path)
    #     path = os.path.join(path, 'plugins', 'core.json')
    #     url = 'file://%s' % (path.replace('\\', '/'))

    #     with open(path, 'rb') as f:
    #         data = f.read()
    #     item = json.loads(data)

    #     manifest = wbimpl.create_manifest(url, item)
    #     self._manifests[manifest.id] = manifest

    #     for point in manifest.extension_points:
    #         point_id = point.qualified_id
    #         self._extension_points[point_id] = point

    #     for extension in manifest.extensions:
    #         self._extensions[extension.qualified_id] = extension
    #         self._contributions[extension.point].add(extension)

    #     key = lambda ext: ext.rank
    #     for point_id, extensions in self._contributions.iteritems():
    #         point = self._extension_points.get(point_id)
    #         if point is None:
    #             point._extensions = sorted(extensions, key=key)

    # def _update_extension_point(self, point_id, to_remove, to_add):
    #     """ Update an extension point will delta extension objects.

    #     This will update the extension point's extensions according to
    #     the deltas and emit an update event on the point. Newly added
    #     extensions will be validated against the extension point schema
    #     if one is available.

    #     If the given extension point has not yet been added to the
    #     workbench, this method is a no-op.

    #     Parameters
    #     ----------
    #     point_id : unicode
    #         The qualified id of the extension point of interest.

    #     to_remove : list
    #         The list of Extension objects to remove from the point.

    #     to_add : list
    #         The list of Extension objects to add to the point.

    #     """
    #     point = self._extension_points.get(point_id)
    #     if point is None:
    #         return
    #     extensions = set(point._extensions)

    #     removed = []
    #     for ext in to_remove:
    #         if ext in extensions:
    #             extensions.remove(ext)
    #             removed.append(ext)

    #     added = []
    #     for ext in to_add:
    #         if ext not in extensions:
    #             # TODO validate the against the extension point schema
    #             extensions.add(ext)
    #             added.append(ext)

    #     if removed or added:
    #         key = lambda ext: ext.rank
    #         point._extensions = sorted(extensions, key=key)
    #         event = ExtensionPointEvent(removed=removed, added=added)
    #         point.updated(event)
