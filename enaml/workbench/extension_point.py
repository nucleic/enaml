#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, Unicode


class ExtensionPoint(Atom):
    """ A class which represents an extension point declaration.

    An ExtensionPoint and its data should be treated as read-only.

    """
    #: The identifier of the plugin which declared the extension point.
    plugin_id = Unicode()

    #: The dict of data loaded from the json declaration.
    data = Typed(dict)

    @property
    def id(self):
        """ Get the extension point identifer.

        """
        return self.data[u'id']

    @property
    def qualified_id(self):
        """ Get the fully qualified extension point identifer.

        """
        this_id = self.data[u'id']
        if u'.' in this_id:
            return this_id
        return u'%s.%s' % (self.plugin_id, this_id)

    @property
    def name(self):
        """ Get the human readable name of the extension point.

        """
        return self.data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the extension point.

        """
        return self.data.get(u'description', u'')
