#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.date_selector import ProxyDateSelector

from .QtWidgets import QDateEdit

from .qt_bounded_date import QtBoundedDate, CHANGED_GUARD


class QtDateSelector(QtBoundedDate, ProxyDateSelector):
    """ A Qt implementation of an Enaml ProxyDateSelector.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDateEdit)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QDateEdit widget.

        """
        self.widget = QDateEdit(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtDateSelector, self).init_widget()
        d = self.declaration
        self.set_date_format(d.date_format)
        self.set_calendar_popup(d.calendar_popup)
        self.widget.dateChanged.connect(self.on_date_changed)

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
        return self.widget.date().toPython()

    def set_minimum(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the minimum date.

        """
        self.widget.setMinimumDate(date)

    def set_maximum(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : date
            The date object to use for setting the maximum date.

        """
        self.widget.setMaximumDate(date)

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : date
            The date object to use for setting the date.

        """
        self._guard |= CHANGED_GUARD
        try:
            self.widget.setDate(date)
        finally:
            self._guard &= ~CHANGED_GUARD

    def set_date_format(self, format):
        """ Set the widget's date format.

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
