#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, GetAttr, List, Member, SetAttr, Unicode


class ExtensionPointEvent(Atom):
    """ An object which holds the state of an extension point event.

    """
    #: The globally unique identifier of the extension point.
    extension_point_id = Unicode()

    #: The list of extensions removed from the extension point.
    removed = List()

    #: The list of extensions added to the extension point.
    added = List()


class ExtensionPoint(Member):
    """ A custom member class for defining plugin extension points.

    An ExtensionPoint provides a well-defined interface on a plugin
    which allows other plugins to contribute additional functionality
    through extensions. It is a programming error to define an instance
    of ExtensionPoint on a class which does not inherit from 'Plugin'.

    """
    __slots__ = ('kind', 'identifier', 'description')

    def __init__(self, kind=object, identifier=u'', description=u''):
        """ Initialize an ExtensionPoint

        Parameters
        ----------
        kind : type or tuple of types, optional
            The allow type(s) for contributed extensions. The default
            is object and will allow any type of extension object.

        identifier : unicode, required
            A globally unique identifier for the extension point.

        description : unicode, optional
            A long-form description of the extension point.

        """
        if not identifier:
            raise TypeError('an extension point id must be provided')
        self.kind = kind
        self.identifier = unicode(identifier)
        self.description = unicode(description)
        self.set_getattr_mode(GetAttr.MemberMethod_Object, 'get')
        self.set_setattr_mode(SetAttr.MemberMethod_ObjectValue, 'set')

    def get(self, plugin):
        """ Get the extensions contributed to the extension point.

        Returns
        -------
        result : list
            The list of extensions contributed to the extension point.

        """
        workbench = plugin.workbench
        if workbench is not None:
            return workbench.get_extensions(self.identifier)
        return []

    def set(self, plugin, value):
        """ The setter for the extension point.

        It is an error to directly assign extension point contributors.

        """
        raise TypeError('cannot directly assign extension point contributors')
