#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.api import ExtensionObject


class ResourceLoader(ExtensionObject):
    """ An ExtensionObject for creating ResourceLoader instances.

    Plugins which contribute to the 'enaml.studio.core.loaders'
    extension point should subclass this factory to create custom
    ResourceLoader objects.

    A loader instance should be able to handle multiple load requests
    during its lifetime. That is, the core plugin will optimize loads
    by creating an instance of a loader when first needed, and then
    reusing it for future requests.

    """
    def __call__(self, kind, uri):
        """ Load the resource specified by a uri.

        Parameters
        ----------
        kind : unicode
            The type of the object to load from the give uri. This
            will be one of the types declared to be handled by the
            extension.

        uri : urlparse.ParseResult
            The parsed uri pointing to the data object which should
            be loaded.

        Returns
        -------
        result : object
            An object of an appropriate type for the extension point
            to which the extension is registered.

        """
        return None
