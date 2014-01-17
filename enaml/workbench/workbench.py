#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Bool, Dict, List, Typed

from .extension_point_listener import ExtensionPointListener
from .plugin import Plugin


class PluginRecord(Atom):
    """

    """
    plugin = Typed(Plugin)

    started = Bool(False)

    stopped = Bool(False)

    extension_points = List()

    extensions = Dict()

    listeners = List()


def _get_extension_points(plugin):
    """

    """


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class is used for managing the lifecycle of plugins. It does
    not provide any UI functionality. Such behavior must be supplied
    by a subclass, such as the enaml.studio.Studio class.

    """
    #: A private dict mapping plugin id to plugin record.
    _plugins = Dict()

    #: A private list storing the plugin records in the order in which
    #: they were added to the workbench.
    _ordered_plugins = List()

    def add_plugin(self, plugin):
        """ Add a plugin to the workbench.

        If a plugin with the same identifier has already been added to
        the workbench, an exception will be raised. The plugin will be
        initialized and its extension points and extensions registered
        with the workbench.

        If a plugin is added dynamically after the workbench has been
        started. The callee is responsible for starting the plugin at
        the appropriate time, by calling the 'start_plugin' method.

        Parameters
        ----------
        plugin : Plugin
            The plugin object to add to the workbench.

        """
        if plugin.identifier in self._plugins:
            msg = "plugin '%s' has already been added to the workbench"
            raise ValueError(msg % plugin.identifier)
        record = PluginRecord(plugin=plugin)
        self._plugins[plugin.identifier] = record
        self._ordered_plugins.append(record)

        # initialize the plugin
        plugin.workbench = self
        plugin.initialize()

        # add the extension points
        registry = self._extension_registry
        record.extension_points = _get_extension_points(plugin)
        for point in record.extension_points:
            registry.add_extension_point(point)

        # add the plugin extensions
        record.extensions = plugin.get_extensions()
        for identifier, extensions in record.extensions.iteritems():
            registry.add_extensions(identifier, extensions)

        # add the extension point listeners
        for point in record.extension_points:
            listener = ExtensionPointListener()
            listener.extension_point = point
            listener.plugin = plugin
            record.listeners.append(listener)
            registry.add_extension_point_listener(point.identifier, listener)

    def remove_plugin(self, identifier):
        """ Remove a plugin from the workbench.

        If a plugin with the specified identifier has not been added to
        the workbench, an exception will be raised. The plugin will be
        stopped if needed, and then destroyed.

        Parameters
        ----------
        identifier : unicode
            The globally unique identifier for the plugin.

        """
        if identifier not in self._plugins:
            msg = "plugin '%s' has not been added to the workbench"
            raise ValueError(msg % identifier)
        record = self._plugins.pop(identifier)
        self._ordered_plugins.remove(record)

        # stop the plugin if needed
        if record.started and not record.stopped:
            record.stopped = True
            record.plugin.stop()

        # XXX not sure about the order here

        # remove the plugin's extension point listeners
        registry = self._extension_registry
        for listener in record.listeners:
            listener.plugin = None
            identifier = listener.extension_point.identifier
            registry.remove_extension_point_listener(identifier, listener)

        # remove the plugin's extensions
        for identifier, extensions in record.extensions.iteritems():
            registry.remove_extensions(identifier, extensions)

        # remove the plugin's extension points
        for point in record.extension_points:
            registry.remove_extension_point(point.identifier)

        # destroy the plugin
        record.plugin.destroy()

    def get_plugin(self, identifier):
        """ Get the plugin with the given identifier.

        Parameters
        ----------
        identifier : unicode
            The globally unique identifier for the plugin.

        Returns
        -------
        result : Plugin or None
            The plugin with the specified identifier, or None if there
            is no plugin with the given identifier.

        """
        record = self._plugins.get(identifier)
        if record is not None:
            return record.plugin

    def get_extensions(self, identifier):
        """ Get the extensions for the specified extension point.

        Parameters
        ----------
        identifier : unicode
            The globally unique identifier of the extension point.

        Returns
        -------
        result : list
            The list of Extension objects contributed to the specified
            extension point. The returned list will be an independent
            copy. In-place changes to the list will have no effect on
            the framework.

        """
        return self._extension_registry.get_extensions(identifier)

    def start(self):
        """ Initialize the workbench.

        This method should be called by user code after all initial
        plugins have been added to the workbench. It will initialize
        all of the current plugins in the order in which they were
        added.

        """
        if not self._initialized:
            # Flip the initialized flag so that plugins added during
            # initialization are automatically initialized, and to
            # protect against intialization recursion.
            self._initialized = True
            self.initializing()
            # Iterate over a copy of the plugins to protect against
            # modifications to the list during initialization.
            for plugin in self._ordered_plugins[:]:
                plugin.initialize()
            self.initialized()


    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

