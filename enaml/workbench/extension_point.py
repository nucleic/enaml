#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Tuple, Str

from enaml.core.declarative import Declarative, d_


class ExtensionPoint(Declarative):
    """ A declarative class which represents a plugin extension point.

    An ExtensionPoint must be declared as a child of a PluginManifest.

    """
    #: The globally unique identifier for the extension point.
    id = d_(Str())

    #: The tuple of extensions contributed to this extension point. The
    #: tuple is updated by the framework as needed. It is kept in sorted
    #: order from lowest to highest extension rank. This should never be
    #: modified directly by user code.
    extensions = Tuple()

    #: An optional description of the extension point.
    description = d_(Str())

    @property
    def plugin_id(self):
        """ Get the plugin id from the parent plugin manifest.

        """
        return self.parent.id

    @property
    def qualified_id(self):
        """ Get the fully qualified extension point identifer.

        """
        this_id = self.id
        if '.' in this_id:
            return this_id
        return '%s.%s' % (self.plugin_id, this_id)
