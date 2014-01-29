#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import json
import os

from atom.api import Atom, List, Typed

from .extension import Extension
from .extension_point import ExtensionPoint
from .validation import validate


SCHEMA_PATH = os.path.abspath(__file__)
SCHEMA_PATH = os.path.dirname(SCHEMA_PATH)
SCHEMA_PATH = os.path.join(SCHEMA_PATH, 'schema.json')


class PluginManifest(Atom):
    """ A class which represents a JSON plugin manifest.

    """
    #: The dict of data loaded from the json declaration.
    _data = Typed(dict)

    #: The list of extension points exposed by the plugin.
    _extension_points = List()

    #: The list of extensions contributed by the plugin.
    _extensions = List()

    def __init__(self, data):
        """ Initialize a PluginManifest.

        Parameters
        ----------
        data : str or unicode
            The json manifest data. If this is a str, it must be
            encoded in UTF-8 or plain ASCII.

        """
        root = json.loads(data)
        validate(root, SCHEMA_PATH)
        self._data = root
        this_id = self.id
        for data in root.get(u'extensionPoints', ()):
            point = ExtensionPoint(this_id, data)
            self._extension_points.append(point)
        for data in root.get(u'extensions', ()):
            ext = Extension(this_id, data)
            self._extensions.append(ext)

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
