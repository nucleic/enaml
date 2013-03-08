#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateEdit
from .qt_bounded_date import QtBoundedDate


class QtDateSelector(QtBoundedDate):
    """ A Qt implementation of an Enaml DateSelector.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QDateEdit widget.

        """
        return QDateEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtDateSelector, self).create(tree)
        self.set_date_format(tree['date_format'])
        self.set_calendar_popup(tree['calendar_popup'])
        self.widget().dateChanged.connect(self.on_date_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_date_format(self, content):
        """ Handle the 'set_date_format' action from the Enaml widget.

        """
        self.set_date_format(content['date_format'])

    def on_action_set_calendar_popup(self, content):
        """ Handle the 'set_calendar_popup' action from the Enaml widget.

        """
        self.set_calendar_popup(content['calendar_popup'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : QDate
            The current control date as a QDate object.

        """
        return self.widget().date()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the date.

        """
        with self.loopback_guard('date'):
            self.widget().setDate(date)

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

    def set_date_format(self, date_format):
        """ Set the widget's date format.

        Parameters
        ----------
        date_format : str
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the
        # same, or convert between the two.
        self.widget().setDisplayFormat(date_format)

    def set_calendar_popup(self, popup):
        """ Set whether a calendar popup is available on the widget.

        Parameters
        ----------
        popup : bool
            Whether the calendar popup is enabled.

        """
        self.widget().setCalendarPopup(popup)

