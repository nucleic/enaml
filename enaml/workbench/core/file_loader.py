#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import re
import traceback
import warnings

from .url_loader import URLLoader


file_rgx = re.compile(ur'^file://')


class FileLoader(URLLoader):
    """ A url loader which loads data from the local filesystem.

    This loader supports the 'file' scheme with urls of the form:

        file://C:/path/to/file.txt

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
        path = file_rgx.sub(u'', url)
        return os.path.isabs(path)

    def absurl(self, url, parent=u''):
        """ Get the absolute path of a relative url.

        Parameters
        ----------
        url : unicode
            A relative url for which 'isabs' returned False.

        parent : unicode, optional
            The parent url of the relative url.

        Returns
        -------
        result : unicode
            The absolute url for the given relative url.

        """
        path = file_rgx.sub(u'', parent)
        dirname = os.path.dirname(path)
        path = file_rgx.sub(u'', url)
        path = os.path.join(dirname, url)
        path = os.path.abspath(path)
        return u'file://'+ path.replace(u'\\', u'/')

    def __call__(self, url):
        """ Load the data specified by the url.

        Parameters
        ----------
        url : unicode
            The url pointing to the data which should be loaded. The
            url is guaranteed to be absolute.

        Returns
        -------
        result : str
            The file data loaded from the given url.

        """
        path = file_rgx.sub(u'', url)
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except IOError:
            msg = "failed to read file '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            data = ''
        return data
