#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.extension_object import ExtensionObject


class URLLoader(ExtensionObject):
    """ An interface for creating url loaders.

    Plugins which contribute to the 'enaml.workbench.core.loaders'
    extension point should subclass this class to create custom url
    loader objects.

    A loader instance should be able to handle multiple load requests
    during its lifetime. That is, the core plugin will optimize loads
    by creating an instance of a loader when first needed, and then
    reusing it for future requests.

    """
    def isabs(self, url):
        """ Get whether the given url represents an absolute path.

        Parameters
        ----------
        url : unicode
            A url with a scheme which matches the loader.

        Returns
        -------
        result : bool
            True if the url is an absolute path, False otherwise.

        """
        raise NotImplementedError

    def absurl(self, url, parent=u''):
        """ Get the absolute path of a relative url.

        Parameters
        ----------
        url : unicode
            A url for which 'isabs' returned False.

        parent : unicode, optional
            The parent url of the relative url.

        Returns
        -------
        result : unicode
            The absolute url for the given relative url.

        """
        raise NotImplementedError

    def __call__(self, url):
        """ Load the data specified by the url.

        Parameters
        ----------
        url : unicode
            The url pointing to the data which should be loaded. The
            url is guaranteed to be absolute.

        Returns
        -------
        result : object
            The data loaded by the given url. This will typically be
            binary data in the form of a string, but a url scheme may
            specify a location which contains data in a different form.

        """
        raise NotImplementedError
