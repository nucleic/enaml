#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QDateTime
from .qt_control import QtControl


def as_qdatetime(iso_datetime):
    """ Convert an iso datetime string to a QDateTime.

    """
    return QDateTime.fromString(iso_datetime, Qt.ISODate)


def as_iso_datetime(qdatetime):
    """ Convert a QDateTime object into an iso datetime string.

    """
    return qdatetime.toString(Qt.ISODate)


class QtBoundedDatetime(QtControl):
    """ A base class for implementing Qt-Enaml datetime widgets.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, create):
        """ Create and initialize the underlying datetime widget.

        """
        super(QtBoundedDatetime, self).create(create)
        self.set_min_datetime(as_qdatetime(create['minimum']))
        self.set_max_datetime(as_qdatetime(create['maximum']))
        self.set_datetime(as_qdatetime(create['datetime']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_datetime(self, content):
        """ Handle the 'set_datetime' action from the Enaml widget.

        """
        self.set_datetime(as_qdatetime(content['datetime']))

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_min_datetime(as_qdatetime(content['minimum']))

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_max_datetime(as_qdatetime(content['maximum']))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_datetime_changed(self):
        """ A signal handler to connect to the datetime changed signal
        of the underlying widget.

        This will convert the QDateTime to iso format and send the Enaml
        widget the 'event-changed' action.

        """
        if 'datetime' not in self.loopback_guard:
            qdatetime = self.get_datetime()
            content = {'datetime': as_iso_datetime(qdatetime)}
            self.send_action('datetime_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control.

        Returns
        -------
        result : QDateTime
            The current control datetime as a QDateTime object.

        """
        raise NotImplementedError

    def set_datetime(self, datetime):
        """ Set the widget's current datetime.

        Implementations should enter the loopback guard using the key
        'datetime' before setting the datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the datetime.

        """
        raise NotImplementedError

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the maximum datetime.

        """
        raise NotImplementedError

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the minimum datetime.

        """
        raise NotImplementedError

