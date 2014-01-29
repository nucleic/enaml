#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Event, List, Typed, Unicode


class ExtensionPointEvent(Atom):
    """ The payload class for an ExtensionPoint updated event.

    """
    #: The list of extensions added to the extension point.
    added = List()

    #: The list of extensions removed from the extension point.
    removed = List()


class ExtensionPoint(Atom):
    """ A class which represents an extension point declaration.

    """
    #: An event emitted by the framework when extensions contributed to
    #: the extension point have been added or removed.
    updated = Event(ExtensionPointEvent)

    #: The identifier of the plugin which declared the extension point.
    #: This is assigned by the framework when it creates the point.
    _plugin_id = Unicode()

    #: The dict of data loaded from the json declaration. This is
    #: assigned by the framework when it creates the point.
    _data = Typed(dict)

    #: The list of extensions contributed to this extension point.
    #: This is updated by the framework as plugins are registered
    #: an maintained in sorted order according to extension rank.
    _extensions = List()

    @property
    def plugin_id(self):
        """ Get the identifer of the extension point's plugin.

        """
        return self._plugin_id

    @property
    def id(self):
        """ Get the extension point identifer.

        """
        return self._data[u'id']

    @property
    def qualified_id(self):
        """ Get the fully qualified extension point identifer.

        """
        this_id = self._data[u'id']
        if u'.' in this_id:
            return this_id
        return u'%s.%s' % (self._plugin_id, this_id)

    @property
    def name(self):
        """ Get the human readable name of the extension point.

        """
        return self._data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the extension point.

        """
        return self._data.get(u'description', u'')

    @property
    def extensions(self):
        """ Get the list of extensions contributed to the point.

        The extensions will be ordered from least to highest rank.

        """
        return self._extensions[:]
