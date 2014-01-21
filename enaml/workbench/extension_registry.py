#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import bisect

from atom.api import Atom, Dict


class RegistryListener(Atom):
    """ A base class for defining extension registry listeners.

    A registry listener is used to listen for changes to an extension
    point in the extension registry. It will be notified when the point
    is added or removed, or when extensions are added or removed from
    the point. Subclasses should reimplement the listener methods as
    needed to react to changes for an extension point.

    """
    def extension_point_added(self, extension_point):
        """ Called when an extension point is added to the registry.

        Parameters
        ----------
        extension_point : ExtensionPoint
            The extension point which was added to the registry.

        """
        pass

    def extension_point_removed(self, plugin_id, extension_point):
        """ Called when an extension point is removed from the registry.

        Parameters
        ----------
        extension_point : ExtensionPoint
            The extension point which was removed from the registry.

        """
        pass

    def extensions_added(self, extensions):
        """ Called when extensions are added to the extension point.

        Parameters
        ----------
        extensions : list
            A list of Extensions added to the extension point.

        """
        pass

    def extensions_removed(self, extensions):
        """ Called when extensions are removed from the extension point.

        Parameters
        ----------
        extensions : list
            A list of Extensions removed from the extension point.

        """
        pass


class ExtensionRegistry(Atom):
    """ A registry class which manages extensions points and extensions.

    """
    def add_extension_point(self, point):
        """ Add an extension point to the registry.

        If an extension point with the same id has already been added
        to the registry, an exception will be raised.

        Parameters
        ----------
        point : ExtensionPoint
            The extension point to add to the registry.

        """
        pass

    def remove_extension_point(self, extension_point_id):
        """ Remove an extension point from the registry.

        If no extension point with the given id has been added to the
        registry, this method is a no-op.

        Parameters
        ----------
        extension_point_id : unicode
            The identifier of the extension point to remove.

        """
        pass

    def add_extensions(self, extensions):
        """ Add extensions to the registry.

        Parameters
        ----------
        extensions : list
            The list of Extensions to add to the registry.

        """
        pass

    def remove_extensions(self, extensions):
        """ Remove extensions from the registry.

        Parameters
        ----------
        identifier : unicode
            The globally unique identifier of the extension point.

        extensions : list
            An list of the Extensions to remove from the registry.

        """
        pass

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
        pass

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
        pass

    def add_listener(self, extension_point_id, listener):
        """ Add a listener to the specified extension point.

        Listeners are maintained and invoked in sorted order.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        listener : RegistryListener
            The registry listener to add to the registry.

        """
        pass

    def remove_listener(self, identifier, listener):
        """ Remove a listener from the specified extension point.

        Parameters
        ----------
        identifier : unicode
            The globally unique identifier of the extension point.

        listener : callable
            The listener to remove from the extension point.

        """
        pass

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of extension point id to extension point.
    _extension_points = Dict()

    #: A mapping of extension point id to list of extensions.
    _extensions = Dict()

    #: A mapping of extension point id to list of registry listeners.
    _listeners = Dict()

    def _invoke_listeners(self, record, removed, added):
        """ Invoke the extension point listeners for a given record.

        Parameters
        ----------
        record : ExtensionPointRecord
            The registry record of interest.

        removed : list
            The list of extensions removed from the extension point.

        added : list
            The list of extensions added to the extension point.

        """
        # if not record.extension_point:
        #     return
        # if not record.listeners:
        #     return
        # if not removed and not added:
        #     return

        # event = ExtensionPointEvent()
        # event.identifier = record.extension_point.identifier
        # event.removed = removed
        # event.added = added

        # # iterate a copy to protect against mutations during dispatch
        # has_dead_listeners = False
        # for listener in record.listeners[:]:
        #     if listener:
        #         listener(event)
        #     else:
        #         has_dead_listeners = True

        # if has_dead_listeners:
        #     record.listeners = filter(None, record.listeners)
