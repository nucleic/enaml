#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from os.path import abspath, isabs, join
import traceback
import warnings

from .url_loader import URLLoader


class FileLoader(URLLoader):
    """ A url loader which loads data from the local filesystem.

    """
    def __call__(self, url, root):
        """ Load the data specified by the url.

        Parameters
        ----------
        url : urlparse.ParseResult
            The parsed url pointing to the data which should be loaded.

        root : unicode
            The root path to use when resolving a relative url.

        Returns
        -------
        result : str
            The file data loaded from the given url.

        """
        path = join(url.netloc, url.path)
        if not isabs(path):
            path = abspath(join(root, path))
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except IOError:
            msg = "failed to read file '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            data = ''
        return data
