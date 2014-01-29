#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed


class PluginManifest(Atom):
    """ A class which represents a JSON plugin manifest.

    """
    #: The dict of data loaded from the json declaration.
    _data = Typed(dict)

    #: The list of extension points exposed by the plugin.
    _extension_points = List()

    #: The list of extensions contributed by the plugin.
    _extensions = List()

    def __init__(self, data, points, extensions):
        """ Initialize a PluginManifest.

        Parameters
        ----------
        data : dict
            The dict loaded from the JSON file which describes
            the plugin.

        points : list
            The list of ExtensionPoints declared for the plugin.

        extensions : list
            The list of Extensions declared for the plugin.

        """
        self._data = data
        self._extension_points = points
        self._extensions = extensions

    @property
    def id(self):
        """ Get the plugin identifer.

        """
        return self._data[u'id']

    @property
    def cls(self):
        """ Get the path of the class which implements the plugin.

        """
        return self._data.get(u'class', u'')

    @property
    def name(self):
        """ Get the human readable name of the plugin.

        """
        return self._data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the plugin.

        """
        return self._data.get(u'description', u'')

    @property
    def extension_points(self):
        """ Get the list of extensions points defined by the plugin.

        """
        return self._extension_points[:]

    @property
    def extensions(self):
        """ Get the list of extensions defined by the plugin.

        """
        return self._extensions[:]
