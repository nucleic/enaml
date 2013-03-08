#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_bounded_date import WxBoundedDate


class WxDateSelector(WxBoundedDate):
    """ A Wx implementation of an Enaml DateSelector.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wx.DatePickerCtrl.

        """
        return wx.DatePickerCtrl(parent)

    def create(self, tree):
        """ Create and initialize the date selector control.

        """
        super(WxDateSelector, self).create(tree)
        self.set_date_format(tree['date_format'])
        self.widget().Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_date_format(self, content):
        """ Handle the 'set_date_format' action from the Enaml widget.

        """
        self.set_date_format(content['date_format'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : wxDateTime
            The current control date as a wxDateTime object.

        """
        return self.widget().GetValue()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the date.

        """
        self.widget().SetValue(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the maximum date.

        """
        widget = self.widget()
        widget.SetRange(widget.GetLowerLimit(), date)

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the minimum date.

        """
        widget = self.widget()
        widget.SetRange(date, widget.GetUpperLimit())

    def set_date_format(self, date_format):
        """ Set the widget's date format.

        Parameters
        ----------
        date_format : str
            A Python time formatting string.

        .. note:: Changing the format on wx is not supported.
                  See http://trac.wxwidgets.org/ticket/10988

        """
        pass

