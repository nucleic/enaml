#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.datetime_selector import ProxyDatetimeSelector

from .QtWidgets import QDateTimeEdit

from .qt_bounded_datetime import QtBoundedDatetime, CHANGED_GUARD


class QtDatetimeSelector(QtBoundedDatetime, ProxyDatetimeSelector):
    """ A Qt implementation of an Enaml ProxyDatetimeSelector.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDateTimeEdit)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QDateTimeEdit widget.

        """
        self.widget = QDateTimeEdit(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtDatetimeSelector, self).init_widget()
        d = self.declaration
        self.set_datetime_format(d.datetime_format)
        self.set_calendar_popup(d.calendar_popup)
        self.widget.dateTimeChanged.connect(self.on_datetime_changed)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control.

        Returns
        -------
        result : datetime
            The current control datetime as a datetime object.

        """
        return self.widget.dateTime().toPython()

    def set_minimum(self, datetime):
        """ Set the widget's minimum datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the minimum datetime.

        """
        self.widget.setMinimumDateTime(datetime)

    def set_maximum(self, datetime):
        """ Set the widget's maximum datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the maximum datetime.

        """
        self.widget.setMaximumDateTime(datetime)

    def set_datetime(self, datetime):
        """ Set the widget's current datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the datetime.

        """
        self._guard |= CHANGED_GUARD
        try:
            self.widget.setDateTime(datetime)
        finally:
            self._guard &= ~CHANGED_GUARD

    def set_datetime_format(self, format):
        """ Set the widget's datetime format.

        Parameters
        ----------
        format : string
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the
        # same, or convert between the two.
        self.widget.setDisplayFormat(format)

    def set_calendar_popup(self, popup):
        """ Set whether a calendar popup is available on the widget.

        Parameters
        ----------
        popup : bool
            Whether the calendar popup is enabled.

        """
        self.widget.setCalendarPopup(popup)
