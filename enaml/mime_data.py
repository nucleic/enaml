#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom


class MimeData(Atom):
    """ An abstract class for defining mime data.

    Concrete implementations of this class will be created by a
    toolkit backend and passed to the relevant frontend methods.

    This will never be instantiated directly by user code. A concrete
    version can be created by calling the `create_mime_data` factory
    method of an Application instance.

    """
    def formats(self):
        """ Get a list of the supported mime type formats.

        Returns
        -------
        result : list
            A list of mime types supported by the data.

        """
        raise NotImplementedError

    def has_format(self, mime_type):
        """ Test whether the data supports the given mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        Returns
        -------
        result : bool
            True if there is data for the given type, False otherwise.

        """
        raise NotImplementedError

    def remove_format(self, mime_type):
        """ Remove the data entry for the given mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        """
        raise NotImplementedError

    def data(self, mime_type):
        """ Get the data for the specified mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        Returns
        -------
        result : str
            The data for the specified mime type.

        """
        raise NotImplementedError

    def set_data(self, mime_type, data):
        """ Set the data for the specified mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        data : str
            The serialized data for the given type.

        """
        raise NotImplementedError
