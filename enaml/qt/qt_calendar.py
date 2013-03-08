#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QCalendarWidget
from .qt_bounded_date import QtBoundedDate


class QtCalendar(QtBoundedDate):
    """ A Qt implementation of an Enaml Calendar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying calender widget.

        """
        return QCalendarWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtCalendar, self).create(tree)
        self.widget().activated.connect(self.on_date_changed)

    #--------------------------------------------------------------------------
    # Abstract Method Implementations
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : QDate
            The current control date as a QDate object.

        """
        return self.widget().selectedDate()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the date.

        """
        with self.loopback_guard('date'):
            self.widget().setSelectedDate(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the maximum date.

        """
        self.widget().setMaximumDate(date)

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the minimum date.

        """
        self.widget().setMinimumDate(date)

