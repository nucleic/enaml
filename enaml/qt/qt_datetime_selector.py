#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateTimeEdit
from .qt_bounded_datetime import QtBoundedDatetime


class QtDatetimeSelector(QtBoundedDatetime):
    """ A Qt implementation of an Enaml DatetimeSelector.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying datetime widget.

        """
        return QDateTimeEdit(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtDatetimeSelector, self).create(tree)
        self.set_datetime_format(tree['datetime_format'])
        self.set_calendar_popup(tree['calendar_popup'])
        self.widget().dateTimeChanged.connect(self.on_datetime_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_datetime_format(self, content):
        """ Handle the 'set_datetime_format' action from the Enaml
        widget.

        """
        self.set_datetime_format(content['datetime_format'])

    def on_action_set_calendar_popup(self, content):
        """ Handle the 'set_calendar_popup' action from the Enaml widget.

        """
        self.set_calendar_popup(content['calendar_popup'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control.

        Returns
        -------
        result : QDateTime
            The current control datetime as a QDateTime object.

        """
        return self.widget().dateTime()

    def set_datetime(self, datetime):
        """ Set the widget's current datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the datetime.

        """
        with self.loopback_guard('datetime'):
            self.widget().setDateTime(datetime)

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the maximum datetime.

        """
        self.widget().setMaximumDateTime(datetime)

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the minimum datetime.

        """
        self.widget().setMinimumDateTime(datetime)

    def set_datetime_format(self, datetime_format):
        """ Set the widget's datetime format.

        Parameters
        ----------
        datetime_format : str
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the
        # same, or convert between the two.
        self.widget().setDisplayFormat(datetime_format)

    def set_calendar_popup(self, popup):
        """ Set whether a calendar popup is available on the widget.

        Parameters
        ----------
        popup : bool
            Whether the calendar popup is enabled.

        """
        self.widget().setCalendarPopup(popup)

