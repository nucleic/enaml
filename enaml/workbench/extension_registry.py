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
    def add_extension_points(self, extension_points):
        """ Add an extension points to the registry.

        Parameters
        ----------
        extension_points : list
            The list of ExtensionPoints to add to the registry.

        """
        # TODO validate the extensions against the schema
        for point in extension_points:
            point_id = point.qualified_id
            if point_id in self._extension_points:
                msg = "The extension point '%s' is already registered. "
                msg += "The duplicate extension point will be ignored."
                warnings.warn(msg % point_id)
            else:
                self._extension_points[point_id] = point
                #method_name = 'extension_point_added'
                #self._invoke_listeners(point_id, method_name, point)

    def remove_extension_points(self, extension_points):
        """ Remove an extension point from the registry.

        Parameters
        ----------
        extension_points : list
            The list of ExtensionPoints to remove from the registry.

        """
        for point in extension_points:
            point_id = point.qualified_id
            point = self._extension_points.pop(point_id, None)
            if point is None:
                msg = "The extension point '%s' is not registered."
                warnings.warn(msg % point_id)
            # else:
            #     method_name = 'extension_point_removed'
            #     self._invoke_listeners(point_id, method_name, point)

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
        # TODO validate the extensions against the schema
        key = lambda ext: ext.point
        for point_id, extensioniter in groupby(extensions, key):
            added = []
            for extension in extensioniter:
                ext_id = extension.qualified_id
                if ext_id and ext_id in self._extension_ids:
                    msg = "The extension '%s' is already registered. "
                    msg += "The duplicate extension will be ignored."
                    warnings.warn(msg % ext_id)
                else:
                    if ext_id:
                        self._extension_ids.add(ext_id)
                    added.append(extension)
            if added:
                self._contributions[point_id].extend(added)
                # method_name = 'extensions_added'
                # self._invoke_listeners(point_id, method_name, added)

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
                    msg = "The extension '%s' is not registered."
                    warnings.warn(msg % ext_id)
                else:
                    self._extension_ids.discard(ext_id)
                    removed.append(extension)
            # if removed:
            #     method_name = 'extensions_removed'
            #     self._invoke_listeners(point_id, method_name, removed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A mapping of extension point id to extension point.
    _extension_points = Typed(dict, ())

    #: A mapping of extension point id to list of extensions.
    _contributions = Typed(defaultdict, (list,))
