#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, Unicode


class Extension(Atom):
    """ A class which represents an extension point declaration.

    An Extension and its data should be treated as read-only.

    """
    #: The identifier of the plugin which declared the extension point.
    plugin_id = Unicode()

    #: The dict of data loaded from the json declaration.
    data = Typed(dict)

    @property
    def point(self):
        """ Get the identifier of the contribution extension point.

        """
        return self.data[u'point']

    @property
    def cls(self):
        """ Get the path of the class which implements the extension.

        """
        return self.data.get(u'class', u'')

    @property
    def id(self):
        """ Get the extension identifer.

        """
        return self.data.get(u'id', u'')

    @property
    def qualified_id(self):
        """ Get the fully qualified extension identifer.

        """
        this_id = self.data.get(u'id', u'')
        if not this_id:
            return u''
        if u'.' in this_id:
            return this_id
        return u'%s.%s' % (self.plugin_id, this_id)

    @property
    def name(self):
        """ Get the human readable name of the extension.

        """
        return self.data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the extension.

        """
        return self.data.get(u'description', u'')

    def has_property(self, name):
        """ Get whether the extension has a property.

        Parameters
        ----------
        name : unicode
            The name of the property of interest.

        Returns
        -------
        result : bool
            True if the extension has the named property. False
            otherwise.

        """
        return name in self.data

    def get_property(self, name, default=None):
        """ Get the named property from the extension.

        Parameters
        ----------
        name : unicode
            The name of the property of interest.

        default : object, optional
            The value to return if the property does not exist in
            the extension.

        Returns
        -------
        result : object
            The value for the named property.

        """
        return self.data.get(name, default)
