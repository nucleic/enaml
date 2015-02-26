#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Tuple, Unicode

from enaml.core.declarative import Declarative, d_


class ExtensionPoint(Declarative):
    """ A declarative class which represents a plugin extension point.

    An ExtensionPoint must be declared as a child of a PluginManifest.

    """
    #: The globally unique identifier for the extension point.
    id = d_(Unicode())

    #: The tuple of extensions contributed to this extension point. The
    #: tuple is updated by the framework as needed. It is kept in sorted
    #: order from lowest to highest extension rank. This should never be
    #: modified directly by user code.
    extensions = Tuple()

    #: An optional description of the extension point.
    description = d_(Unicode())

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
        if u'.' in this_id:
            return this_id
        return u'%s.%s' % (self.plugin_id, this_id)
