#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QTime
from .qt_control import QtControl


def as_qtime(iso_time):
    """ Convert an iso time string to a QTime.

    """
    return QTime.fromString(iso_time, Qt.ISODate)


def as_iso_time(qtime):
    """ Convert a QTime object into and iso time string.

    """
    return qtime.toString(Qt.ISODate)


class QtBoundedTime(QtControl):
    """ A base class for implementing Qt-Enaml time widgets.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the underyling time widget.

        """
        super(QtBoundedTime, self).create(tree)
        self.set_min_time(as_qtime(tree['minimum']))
        self.set_max_time(as_qtime(tree['maximum']))
        self.set_time(as_qtime(tree['time']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_time(self, content):
        """ Handle the 'set_time' action from the Enaml widget.

        """
        self.set_time(as_qtime(content['time']))

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_min_time(as_qtime(content['minimum']))

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_max_time(as_qtime(content['maximum']))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_time_changed(self):
        """ A signal handler to connect to the time changed signal of
        the underlying widget.

        This will convert the QTime to iso format and send the Enaml
        widget the 'time_changed' action.

        """
        if 'time' not in self.loopback_guard:
            qtime = self.get_time()
            content = {'time': as_iso_time(qtime)}
            self.send_action('time_changed', content)

    #--------------------------------------------------------------------------
    # Abstract Methods
    #--------------------------------------------------------------------------
    def get_time(self):
        """ Return the current time in the control.

        Returns
        -------
        result : QTime
            The current control time as a QTime object.

        """
        raise NotImplementedError

    def set_time(self, time):
        """ Set the widget's current time.

        Implementations should enter the loopback guard using the key
        'time' before setting the time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the time.

        """
        raise NotImplementedError

    def set_max_time(self, time):
        """ Set the widget's maximum time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the maximum time.

        """
        raise NotImplementedError

    def set_min_time(self, time):
        """ Set the widget's minimum time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the minimum time.

        """
        raise NotImplementedError

