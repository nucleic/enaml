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

from .uri_reader import URIReader


class FileLoader(URIReader):
    """ A uri reader which loads data from the local filesystem.

    """
    def __call__(self, uri):
        """ Load the data specified by the uri.

        Parameters
        ----------
        uri : urlparse.ParseResult
            The parsed uri pointing to the data which should be loaded.
            This should represent the absolute path to the local file.

        Returns
        -------
        result : str
            The file data loaded from the given uri.

        """
        path = os.path.join(uri.netloc, uri.path)
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except IOError:
            msg = "failed to read file '%s':\n%s"
            warnings.warn(msg % (path, traceback.format_exc()))
            data = ''
        return data
