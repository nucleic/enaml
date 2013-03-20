#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from wx.calendar import CalendarCtrl, EVT_CALENDAR

from atom.api import Typed

from enaml.widgets.calendar import ProxyCalendar

from .wx_bounded_date import (
    WxBoundedDate, CHANGED_GUARD, as_wx_date, as_py_date
)


class WxCalendar(WxBoundedDate, ProxyCalendar):
    """ A Wx implementation of an Enaml ProxyCalendar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(CalendarCtrl)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the calender widget.

        """
        self.widget = CalendarCtrl(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(WxCalendar, self).init_widget()
        self.widget.Bind(EVT_CALENDAR, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Abstract Method Implementation
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : date
            The current control date as a Python date object.

        """
        return as_py_date(self.widget.GetDate())

    def set_minimum(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the minimum date.

        """
        self.widget.SetLowerDateLimit(as_wx_date(date))

    def set_maximum(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the maximum date.

        """
        self.widget.SetUpperDateLimit(as_wx_date(date))

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : date
            The date object to use for setting the date.

        """
        self._guard |= CHANGED_GUARD
        try:
            self.widget.SetDate(as_wx_date(date))
        finally:
            self._guard &= ~CHANGED_GUARD
