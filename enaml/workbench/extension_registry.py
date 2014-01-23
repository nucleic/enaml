#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from bisect import insort
from collections import defaultdict
from itertools import groupby
import warnings

from atom.api import Atom, Typed


class RegistryEventListener(Atom):
    """ A base class for defining extension registry listeners.

    A registry listener is used to listen for changes to an extension
    point in the extension registry. It will be notified when a point
    is added or removed, or when extensions are added or removed from
    a point. Subclasses should reimplement the needed listener methods
    to react to changes to an extension point.

    """
    def extension_point_added(self, extension_point):
        """ Called when an extension point is added to the registry.

        Parameters
        ----------
        extension_point : ExtensionPoint
            The extension point which was added to the registry.

        """
        pass

    def extension_point_removed(self, extension_point):
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

        Parameters
        ----------
        point : ExtensionPoint
            The extension point to add to the registry.

        """
        point_id = point.qualified_id
        if point_id in self._extension_points:
            msg = "The extension point '%s' is already registered. "
            msg += "The duplicate extension point will be ignored."
            warnings.warn(msg % point_id)
            return
        self._extension_points[point_id] = point
        self._invoke_listeners(point_id, 'extension_point_added', point)

    def remove_extension_point(self, extension_point_id):
        """ Remove an extension point from the registry.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point to remove.

        """
        point_id = extension_point_id
        point = self._extension_points.pop(point_id, None)
        if point is None:
            msg = "The extension point '%s' does not exist in the registry."
            warnings.warn(msg % point_id)
            return
        self._invoke_listeners(point_id, 'extension_point_removed', point)

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
        """ Get all of the extension points in the registry.

        Returns
        -------
        result : list
            A list of all of the extension points in the registry.

        """
        return self._extension_points.values()

    def add_extensions(self, extensions):
        """ Add extensions to the registry.

        Parameters
        ----------
        extensions : list
            The list of Extensions to add to the registry.

        """
        key = lambda ext: ext.point
        for point_id, extensioniter in groupby(extensions, key):
            added = []
            for extension in extensioniter:
                ext_id = extension.qualified_id
                if ext_id and ext_id in self._extensions:
                    msg = "The extension '%s' is already registered. "
                    msg += "The duplicate extension will be ignored."
                    warnings.warn(msg % ext_id)
                else:
                    self._extensions[ext_id] = extension
                    added.append(extension)
            if added:
                self._contributions[point_id].extend(added)
                self._invoke_listeners(point_id, 'extensions_added', added)

    def remove_extensions(self, extensions):
        """ Remove extensions from the registry.

        Parameters
        ----------
        extensions : list
            The list of the Extensions to remove from the registry.

        """
        key = lambda ext: ext.point
        for point_id, extensioniter in groupby(extensions, key):
            current = self._contributions.get(point_id, [])
            removed = []
            for extension in extensioniter:
                ext_id = extension.qualified_id
                try:
                    current.remove(extension)
                except ValueError:
                    msg = "The extension '%s' does not exist in the registry."
                    warnings.warn(msg % ext_id)
                else:
                    self._extensions.pop(ext_id, None)
                    removed.append(extension)
            if removed:
                self._invoke_listeners(point_id, 'extensions_removed', removed)

    def get_extension(self, extension_point_id, extension_id):
        """ Get a specific extension contributed to an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point to of interest.

        extension_id : unicode
            The fully qualified id of the extension.

        Returns
        -------
        result : Extension or None
            The requested Extension, or None if it does not exist.

        """
        for extension in self._contributions.get(extension_point_id, ()):
            if extension.qualified_id == extension_id:
                return extension

    def get_extensions(self, extension_point_id):
        """ Get the extensions contributed to an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        Returns
        -------
        result : list
            A list of Extensions contributed to the extension point.

        """
        extensions = self._contributions.get(extension_point_id)
        return extensions[:] if extensions else []

    def add_listener(self, extension_point_id, listener):
        """ Add a listener to the specified extension point.

        Listeners are maintained and invoked in sorted order.

        Parameters
        ----------
        extension_point_id : unicode or None
            The fully qualified id of the extension point of interest,
            or None to install the listener for all extension points.

        listener : RegistryEventListener
            The registry listener to add to the registry.

        """
        insort(self._listeners[extension_point_id], listener)

    def remove_listener(self, extension_point_id, listener):
        """ Remove a listener from the specified extension point.

        Parameters
        ----------
        extension_point_id : unicode or None
            The same identifier used when the listener was added.

        listener : RegistryEventListener
            The listener to remove from the registry.

        """
        listeners = self._listeners.get(extension_point_id, [])
        try:
            listeners.remove(listener)
        except ValueError:
            warnings.warn("The listener does not exist in the registry.")

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of extension point id to extension point.
    _extension_points = Typed(dict, ())

    #: A mapping of extension id to extension.
    _extensions = Typed(dict, ())

    #: A mapping of extension point id to list of extensions.
    _contributions = Typed(defaultdict, (list,))

    #: A mapping of extension point id to list of registry listeners.
    _listeners = Typed(defaultdict, (list,))

    def _invoke_listeners(self, extension_point_id, method_name, arg):
        """ Invoke the listeners for a given extension point.

        This method automatically invokes the registry-wide listeners
        before invoking the extension point specific listeners.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        method_name : str
            The name of the listener method to invoke on the listeners.

        arg : object
            The argument to pass to the listener method.

        """
        rg_lsnrs = self._listeners.get(None, [])
        pt_lsnrs = self._listeners.get(extension_point_id, [])
        for listener in rg_lsnrs + pt_lsnrs:
            getattr(listener, method_name)(arg)
