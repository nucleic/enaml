#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QDate

from atom.api import Int

from enaml.widgets.bounded_date import ProxyBoundedDate

from .qt_control import QtControl


def as_qdate(pydate):
    """ Convert a Python date into a QDate.

    """
    return QDate(pydate.year, pydate.month, pydate.day)


def as_pydate(qdate):
    """ Convert a QDate object into a Python date.

    """
    return qdate.toPyDate()


# cyclic notification guard flags
CHANGED_GUARD = 0x1


class QtBoundedDate(QtControl, ProxyBoundedDate):
    """ A base class for implementing Qt-Enaml date widgets.

    """
    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Implement in a subclass to create the date widget.

        """
        raise NotImplementedError

    def create(self):
        """ Initialize the date widget.

        """
        super(QtBoundedDate, self).create()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_date(d.date)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ A signal handler to connect to the date changed signal of
        the underlying widget.

        This will convert the QDate to iso format and send the Enaml
        widget the 'date_changed' action.

        """
        if not self._guard & CHANGED_GUARD:
            self.declaration.date = self.get_date()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : date
            The current control date as a date object.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # ProxyBoundedDate API
    #--------------------------------------------------------------------------
    def set_minimum(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the minimum date.

        """
        raise NotImplementedError

    def set_maximum(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the maximum date.

        """
        raise NotImplementedError

    def set_date(self, date):
        """ Set the widget's current date.

        Implementations should enter the loopback guard using the key
        'date' before setting the date.

        Parameters
        ----------
        date : date
            The date object to use for setting the date.

        """
        raise NotImplementedError
