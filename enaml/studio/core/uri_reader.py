#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.api import ExtensionObject


class URIReader(ExtensionObject):
    """ An ExtensionObject for creating uri readers.

    Plugins which contribute to the 'enaml.studio.core.uriReaders'
    extension point should subclass this class to create custom
    uri reader objects.

    A reader instance should be able to handle multiple load requests
    during its lifetime. That is, the core plugin will optimize reads
    by creating an instance of a reader when first needed, and then
    reusing it for future requests.

    """
    def __call__(self, uri):
        """ Load the data specified by the uri.

        Parameters
        ----------
        uri : urlparse.ParseResult
            The parsed uri pointing to the data which should be loaded.

        Returns
        -------
        result : object
            The data loaded by the given uri. This will typically be
            binary data in the form of a string, but a uri scheme may
            specify data in a different form.

        """
        return None
