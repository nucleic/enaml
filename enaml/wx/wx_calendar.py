#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from wx.calendar import CalendarCtrl, EVT_CALENDAR

from .wx_bounded_date import WxBoundedDate


class WxCalendar(WxBoundedDate):
    """ A Wx implementation of an Enaml Calendar.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the wx.calendar.CalendarCtrl widget.

        """
        return CalendarCtrl(parent)

    def create(self, tree):
        """ Create and initialize the the calendar widget.

        """
        super(WxCalendar, self).create(tree)
        self.widget().Bind(EVT_CALENDAR, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Abstract Method Implementations
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : wxDateTime
            The current control date as a wxDateTime object.

        """
        return self.widget().GetDate()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the date.

        """
        self.widget().SetDate(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the maximum date.

        """
        self.widget().SetUpperDateLimit(date)

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the minimum date.

        """
        self.widget().SetLowerDateLimit(date)

