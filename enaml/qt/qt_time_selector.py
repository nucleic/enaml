#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QTimeEdit
from .qt_bounded_time import QtBoundedTime


class QtTimeSelector(QtBoundedTime):
    """ A Qt implementation of an Enaml TimeSelector.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QTimeEdit widget.

        """
        return QTimeEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtTimeSelector, self).create(tree)
        self.set_time_format(tree['time_format'])
        self.widget().timeChanged.connect(self.on_time_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_time_format(self, content):
        """ Handle the 'set_time_format' action from the Enaml widget.

        """
        self.set_time_format(content['time_format'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_time(self):
        """ Return the current time in the control.

        Returns
        -------
        result : QTime
            The current control time as a QTime object.

        """
        return self.widget().time()

    def set_time(self, time):
        """ Set the widget's current time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the time.

        """
        with self.loopback_guard('time'):
            self.widget().setTime(time)

    def set_max_time(self, time):
        """ Set the widget's maximum time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the maximum time.

        """
        self.widget().setMaximumTime(time)

    def set_min_time(self, time):
        """ Set the widget's minimum time.

        Parameters
        ----------
        time : QTime
            The QTime object to use for setting the minimum time.

        """
        self.widget().setMinimumTime(time)

    def set_time_format(self, time_format):
        """ Set the widget's time format.

        Parameters
        ----------
        time_format : str
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the
        # same, or convert between the two.
        self.widget().setDisplayFormat(time_format)

