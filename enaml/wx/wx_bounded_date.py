#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import datetime

import wx

from atom.api import Int

from enaml.widgets.bounded_date import ProxyBoundedDate

from .wx_control import WxControl


def as_wx_date(py_date):
    """ Convert an iso date string to a wxDateTime.

    """
    day = py_date.day
    month = py_date.month - 1  # wx peculiarity!
    year = py_date.year
    return wx.DateTimeFromDMY(day, month, year)


def as_py_date(wx_date):
    """ Convert a QDate object into and iso date string.

    """
    day = wx_date.GetDay()
    month = wx_date.GetMonth() + 1  # wx peculiarity!
    year = wx_date.GetYear()
    return datetime.date(year, month, day)


# cyclic notification guard flags
CHANGED_GUARD = 0x1


class WxBoundedDate(WxControl, ProxyBoundedDate):
    """ A base class for use with Wx widgets implementing behavior
    for subclasses of BoundedDate.

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

    def init_widget(self):
        """ Create and initialize the bounded date widget.

        """
        super(WxBoundedDate, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_date(d.date)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self, event):
        """ An event handler to connect to the date changed signal of
        the underlying widget.

        This will convert the wxDateTime to iso format and send the Enaml
        widget the 'date_changed' action.

        """
        if not self._guard & CHANGED_GUARD:
            self.declaration.date = self.get_date()

    #--------------------------------------------------------------------------
    # Abstract Methods and ProxyBoundedDate API
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : date
            The current control date as a date object.

        """
        raise NotImplementedError

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

        Parameters
        ----------
        date : date
            The date object to use for setting the date.

        """
        raise NotImplementedError
