#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QDate
from .qt_control import QtControl


def as_qdate(iso_date):
    """ Convert an iso date string to a QDate

    """
    return QDate.fromString(iso_date, Qt.ISODate)


def as_iso_date(qdate):
    """ Convert a QDate object into and iso date string.

    """
    return qdate.toString(Qt.ISODate)


class QtBoundedDate(QtControl):
    """ A base class for implementing Qt-Enaml date widgets.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the underyling date widget.

        """
        super(QtBoundedDate, self).create(tree)
        self.set_min_date(as_qdate(tree['minimum']))
        self.set_max_date(as_qdate(tree['maximum']))
        self.set_date(as_qdate(tree['date']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_date(self, content):
        """ Handle the 'set_date' action from the Enaml widget.

        """
        self.set_date(as_qdate(content['date']))

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_min_date(as_qdate(content['minimum']))

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_max_date(as_qdate(content['maximum']))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ A signal handler to connect to the date changed signal of
        the underlying widget.

        This will convert the QDate to iso format and send the Enaml
        widget the 'date_changed' action.

        """
        if 'date' not in self.loopback_guard:
            qdate = self.get_date()
            content = {'date': as_iso_date(qdate)}
            self.send_action('date_changed', content)

    #--------------------------------------------------------------------------
    # Abstract Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : QDate
            The current control date as a QDate object.

        """
        raise NotImplementedError

    def set_date(self, date):
        """ Set the widget's current date.

        Implementations should enter the loopback guard using the key
        'date' before setting the date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the date.

        """
        raise NotImplementedError

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the maximum date.

        """
        raise NotImplementedError

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the minimum date.

        """
        raise NotImplementedError

