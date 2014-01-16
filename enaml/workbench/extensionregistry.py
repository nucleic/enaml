#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import bisect

from atom.api import Atom, List, Typed

from .extensionpoint import ExtensionPoint, ExtensionPointEvent


class ExtensionRecord(Atom):
    """ A data record for an extension point in an extension registry.

    Instances of this class are created by an ExtensionRegistry.
    It should not normally be used directly by user code.

    """
    #: The extension point associated with the record.
    extension_point = Typed(ExtensionPoint)

    #: The list of callable objects to invoke when extensions are
    #: added or removed from the extension point. This value is
    #: updated by the registry when listeners are added or removed.
    listeners = List()

    #: The tuple of extensions which have been contributed to the
    #: extension point. This value is updated by the registry when
    #: extensions are added or removed.
    extensions = List()


class ExtensionRegistry(Atom):
    """ A registry class for extensions points and extensions.

    Instances of this class are created by a workbench to manage plugin
    extension points and extensions. It should not be used directly by
    user code.

    """
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_extension_point(self, extension_point):
        """ Add an extension point to the registry.

        If the extension point has already been added to the registry,
        an exception will be raised. This ensures that extension point
        identifiers are unique for each instance of a registry.

        Parameters
        ----------
        extension_point : ExtensionPoint
            The extension point to add to the registry.

        """
        record = self._get_record(extension_point.identifier)
        if record.extension_point is not None:
            msg = "extension point '%s' is already registered"
            raise TypeError(msg % extension_point.identifier)
        record.extension_point = extension_point
        # formally add extensions contributed before registration
        if record.extensions:
            extensions = record.extensions
            record.extensions = []
            self.add_extensions(extension_point.identifier, extensions)

    def remove_extension_point(self, extension_point_id):
        """ Remove an extension point from the registry.

        If the specified extension point has not been added to the
        registry, this method is a no-op.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        """
        record = self._get_record(extension_point_id)
        if record.extension_point is not None:
            self._invoke_listeners(record, record.extensions, [])
            record.extension_point = None

    def get_extensions(self, extension_point_id):
        """ Get the extensions contributed to an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        Returns
        -------
        result : list
            A copy of the list of extensions contributed to the
            extension point.

        """
        record = self._get_record(extension_point_id)
        return record.extensions[:]

    def add_extensions(self, extension_point_id, extensions):
        """ Add extensions to an extension point.

        If the specified extension point has not yet been registered,
        the extensions will be added as soon as it becomes available.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        extensions : iterable
            An iterable of the extension objects. These objects will
            be validated against the allowed type(s) specified by the
            extension point. The extensions are maintained in sorted
            order.

        """
        # If the extension point is not yet registered, store away
        # the extensions and bail. This method will be invoked again
        # when the extension point is finally registered.
        record = self._get_record(extension_point_id)
        if record.extension_point is None:
            record.extensions = list(extensions)
            return
        kind = record.extension_point.kind
        extensions = list(extensions)
        for ext in extensions:
            if not isinstance(ext, kind):
                msg = "invalid extension type for '%s': '%s'"
                args = (extension_point_id, type(ext).__name__)
                raise TypeError(msg % args)
            bisect.insort(record.extensions, ext)
        self._invoke_listeners(record, [], extensions)

    def remove_extensions(self, extension_point_id, extensions):
        """ Remove extensions from an extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        extensions : iterable
            An iterable of the extension objects to remove.

        """
        record = self._get_record(extension_point_id)
        if not record.extensions:
            return
        removed = []
        for ext in extensions:
            idx = bisect.bisect_left(record.extensions, ext)
            if record.extensions[idx] == ext:
                del record.extensions[idx]
                removed.append(ext)
        self._invoke_listeners(record, removed, [])

    def add_extension_point_listener(self, extension_point_id, listener):
        """ Add a listener to the specified extension point.

        The listener will be invoked when extensions are added or
        removed from the extension point. If a listener is registered
        before an extension point is registered, the listener will be
        invoked when the extension point becomes available. Listeners
        are maintained and invoked in sorted order.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        listener : callable
            A callable which accepts a single argument which is an
            instance of ExtensionPointEvent. The callable is tested
            for boolean truth before being invoked. A callable which
            tests false will not be invoked and will be removed from
            the list of listeners.

        """
        record = self._get_record(extension_point_id)
        bisect.insort(record.listeners, listener)

    def remove_extension_point_listener(self, extension_point_id, listener):
        """ Remove a listener from the specified extension point.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier of the extension point.

        listener : callable
            The listener to remove from the extension point.

        """
        record = self._get_record(extension_point_id)
        if record.listeners:
            idx = bisect.bisect_left(record.listeners, listener)
            if record.listeners[idx] == listener:
                del record.listeners[idx]

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The registry dict which maps identifier to record
    _registry = Typed(dict, ())

    def _get_record(self, extension_point_id):
        """ Get the record for the given extension point id.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier for the extension point.

        force : bool, optional
            Whether to automatically create the extension record if
            one does not already exist.

        """
        record = self._registry.get(extension_point_id)
        if record is None:
            record = self._registry[extension_point_id] = ExtensionRecord()
        return record

    def _invoke_listeners(self, record, removed, added):
        """ Invoke the extension point listeners for a given record.

        Parameters
        ----------
        record : ExtensionRecord
            The extension record of interest.

        removed : list
            The list of extensions removed from the extension point.

        added : list
            The list of extensions added to the extension point.

        """
        if not record.extension_point:
            return
        if not record.listeners:
            return
        if not removed and not added:
            return

        event = ExtensionPointEvent()
        event.extension_point_id = record.extension_point.identifier
        event.removed = removed
        event.added = added

        # iterate a copy to protect against mutations during dispatch
        dead_listeners = False
        for listener in record.listeners[:]:
            if listener:
                listener(event)
            else:
                dead_listeners = True

        if dead_listeners:
            record.listeners = filter(None, record.listeners)
