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
    """ A class which represents a plugin manifest.

    A PluginManifest and its data should be treated as read-only.

    """
    #: The dict of data loaded from the json declaration.
    data = Typed(dict)

    #: The list of extension points exposed by the plugin.
    extension_points = List(ExtensionPoint)

    #: The list of extensions contributed by the plugin.
    extensions = List(Extension)

    @property
    def id(self):
        """ Get the plugin identifer.

        """
        return self.data[u'id']

    @property
    def cls(self):
        """ Get the path of the class which implements the plugin.

        """
        return self.data.get(u'class', u'')

    @property
    def name(self):
        """ Get the human readable name of the plugin.

        """
        return self.data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the plugin.

        """
        return self.data.get(u'description', u'')


def create_manifest(data):
    """ Create a plugin manifest from JSON data.

    This function should not be used directly by user code.

    Parameters
    ----------
    data : str or unicode
        The json manifest data. If this is a str, it must be encoded
        in UTF-8 or plain ASCII.

    Returns
    -------
    result : PluginManifest
        The manifest object for the given JSON data.

    """
    root = json.loads(data)
    validate(root, SCHEMA_PATH)
    manifest = PluginManifest(data=root)
    plugin_id = manifest.id
    for pt in root.get(u'extensionPoints', ()):
        item = ExtensionPoint(plugin_id=plugin_id, data=pt)
        manifest.extension_points.append(item)
    for ext in root.get(u'extensions', ()):
        item = Extension(plugin_id=plugin_id, data=ext)
        manifest.extensions.append(item)
    return manifest
