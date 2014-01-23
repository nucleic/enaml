#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed

from .extension import Extension
from .extension_point import ExtensionPoint


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
