#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import unicode_literals
from atom.api import Callable, Int, Unicode

from enaml.core.declarative import Declarative, d_


class Extension(Declarative):
    """ A declarative class which represents a plugin extension.

    An Extension must be declared as a child of a PluginManifest.

    """
    #: The globally unique identifier for the extension.
    id = d_(Unicode())

    #: The fully qualified id of the target extension point.
    point = d_(Unicode())

    #: An optional rank to use for order the extension among others.
    rank = d_(Int())

    #: A callable which will create the implementation object for the
    #: extension point. The call signature and return type are defined
    #: by the extension point plugin which invokes the factory.
    factory = d_(Callable())

    #: An optional description of the extension.
    description = d_(Unicode())

    @property
    def plugin_id(self):
        """ Get the plugin id from the parent plugin manifest.

        """
        return self.parent.id

    @property
    def qualified_id(self):
        """ Get the fully qualified extension identifer.

        """
        this_id = self.id
        if u'.' in this_id:
            return this_id
        return u'%s.%s' % (self.plugin_id, this_id)

    def get_child(self, kind, reverse=False):
        """ Find a child by the given type.

        Parameters
        ----------
        kind : type
            The declarative type of the child of interest.

        reverse : bool, optional
            Whether to search in reversed order. The default is False.

        Returns
        -------
        result : child or None
            The first child found of the requested type.

        """
        it = reversed if reverse else iter
        for child in it(self.children):
            if isinstance(child, kind):
                return child
        return None

    def get_children(self, kind):
        """ Get all the children of the given type.

        Parameters
        ----------
        kind : type
            The declarative type of the children of interest.

        Returns
        -------
        result : list
            The list of children of the request type.

        """
        return [c for c in self.children if isinstance(c, kind)]
