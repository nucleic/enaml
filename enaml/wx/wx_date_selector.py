#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.date_selector import ProxyDateSelector

from .wx_bounded_date import (
    WxBoundedDate, CHANGED_GUARD, as_wx_date, as_py_date
)


class WxDateSelector(WxBoundedDate, ProxyDateSelector):
    """ A Wx implementation of an Enaml ProxyDateSelector.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wx.DatePickerCtrl)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the wx.DatePickerCtrl widget.

        """
        self.widget = wx.DatePickerCtrl(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(WxDateSelector, self).init_widget()
        d = self.declaration
        self.set_date_format(d.date_format)
        self.set_calendar_popup(d.calendar_popup)
        self.widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : date
            The current control date as a date object.

        """
        return as_py_date(self.widget.GetValue())

    def set_minimum(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the minimum date.

        """
        widget = self.widget
        widget.SetRange(as_wx_date(date), widget.GetUpperLimit())


    def set_maximum(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the maximum date.

        """
        widget = self.widget
        widget.SetRange(widget.GetLowerLimit(), as_wx_date(date))

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : date
            The date object to use for setting the date.

        """
        self._guard |= CHANGED_GUARD
        try:
            self.widget.SetValue(as_wx_date(date))
        finally:
            self._guard &= ~CHANGED_GUARD

    def set_date_format(self, format):
        """ Set the widget's date format.

        Parameters
        ----------
        format : string
            A Python time formatting string.

        .. note:: Changing the format on wx is not supported.
                  See http://trac.wxwidgets.org/ticket/10988

        """
        pass

    def set_calendar_popup(self, popup):
        """ This is not supported on Wx.

        """
        pass
