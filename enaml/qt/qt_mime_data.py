#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.mime_data import MimeData

from .QtCore import QMimeData


class QtMimeData(MimeData):
    """ A Qt implementation of an Enaml MimeData object.

    """
    #: Internal storage for the QMimeData.
    _q_data = Typed(QMimeData)

    def __init__(self, data=None):
        """ Initialize a QtMimeData object.

        Parameters
        ----------
        data : QMimeData, optional
            The mime data to wrap. If not provided, one will be created.

        """
        self._q_data = data or QMimeData()

    def q_data(self):
        """ Get the internal QMimeData object.

        This method is for toolkit backend use only.

        Returns
        -------
        result : QMimeData
            The Qt specific mime data object.

        """
        return self._q_data

    def formats(self):
        """ Get a list of the supported mime type formats.

        Returns
        -------
        result : list
            A list of mime types supported by the data.

        """
        return self._q_data.formats()

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
        return self._q_data.hasFormat(mime_type)

    def remove_format(self, mime_type):
        """ Remove the data entry for the given mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        """
        self._q_data.removeFormat(mime_type)

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
        return self._q_data.data(mime_type).data()

    def set_data(self, mime_type, data):
        """ Set the data for the specified mime type.

        Parameters
        ----------
        mime_type : unicode
            The mime type of interest.

        data : str
            The serialized data for the given type.

        """
        self._q_data.setData(mime_type, data)
