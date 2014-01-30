#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import traceback
import warnings

from .url_loader import URLLoader


class FileLoader(URLLoader):
    """ A url loader which loads data from the local filesystem.

    """
    def __call__(self, url):
        """ Load the data specified by the url.

        Parameters
        ----------
        url : urlparse.ParseResult
            The parsed url pointing to the data which should be loaded.
            This should represent the absolute path to the local file.

        Returns
        -------
        result : str
            The file data loaded from the given url.

        """
        path = os.path.join(url.netloc, url.path)
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except IOError:
            msg = "failed to read file '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            data = ''
        return data
