#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import datetime

from dateutil import parser as isoparser
import wx

from .wx_control import WxControl


def as_wx_date(iso_date):
    """ Convert an iso date string to a wxDateTime.

    """
    # wx doesn't have iso date parsing until version 2.9
    py_date = isoparser.parse(iso_date)
    day = py_date.day
    month = py_date.month - 1  # wx peculiarity!
    year = py_date.year
    return wx.DateTimeFromDMY(day, month, year)


def as_iso_date(wx_date):
    """ Convert a QDate object into and iso date string.

    """
    day = wx_date.GetDay()
    month = wx_date.GetMonth() + 1  # wx peculiarity!
    year = wx_date.GetYear()
    return datetime.date(year, month, day).isoformat()


class WxBoundedDate(WxControl):
    """ A base class for use with Wx widgets implementing behavior
    for subclasses of BoundedDate.

    """
     #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the bounded date widget.

        """
        super(WxBoundedDate, self).create(tree)
        self.set_min_date(as_wx_date(tree['minimum']))
        self.set_max_date(as_wx_date(tree['maximum']))
        self.set_date(as_wx_date(tree['date']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_date(self, content):
        """ Handle the 'set_date' action from the Enaml widget.

        """
        self.set_date(as_wx_date(content['date']))

    def on_action_set_minimum(self, content):
        """ Hanlde the 'set_minimum' action from the Enaml widget.

        """
        self.set_min_date(as_wx_date(content['minimum']))

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_max_date(as_wx_date(content['maximum']))

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self, event):
        """ An event handler to connect to the date changed signal of
        the underlying widget.

        This will convert the wxDateTime to iso format and send the Enaml
        widget the 'date_changed' action.

        """
        wx_date = self.get_date()
        content = {'date': as_iso_date(wx_date)}
        self.send_action('date_changed', content)

    #--------------------------------------------------------------------------
    # Abstract Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : wxDateTime
            The current control date as a wxDateTime object.

        """
        raise NotImplementedError

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the date.

        """
        raise NotImplementedError

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the maximum date.

        """
        raise NotImplementedError

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the minimum date.

        """
        raise NotImplementedError

