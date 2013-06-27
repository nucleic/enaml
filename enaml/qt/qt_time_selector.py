#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.time_selector import ProxyTimeSelector

from .QtGui import QTimeEdit

from .qt_bounded_time import QtBoundedTime, CHANGED_GUARD


class QtTimeSelector(QtBoundedTime, ProxyTimeSelector):
    """ A Qt implementation of an Enaml ProxyTimeSelector.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QTimeEdit)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the QTimeEdit widget.

        """
        self.widget = QTimeEdit(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtTimeSelector, self).init_widget()
        d = self.declaration
        self.set_time_format(d.time_format)
        self.widget.timeChanged.connect(self.on_time_changed)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def get_time(self):
        """ Return the current time in the control.

        Returns
        -------
        result : time
            The current control time as a time object.

        """
        return self.widget.time().toPython()

    def set_minimum(self, time):
        """ Set the widget's minimum time.

        Parameters
        ----------
        time : time
            The time object to use for setting the minimum time.

        """
        self.widget.setMinimumTime(time)

    def set_maximum(self, time):
        """ Set the widget's maximum time.

        Parameters
        ----------
        time : time
            The time object to use for setting the maximum time.

        """
        self.widget.setMaximumTime(time)

    def set_time(self, time):
        """ Set the widget's current time.

        Parameters
        ----------
        time : time
            The time object to use for setting the date.

        """
        self._guard |= CHANGED_GUARD
        try:
            self.widget.setTime(time)
        finally:
            self._guard &= ~CHANGED_GUARD

    def set_time_format(self, format):
        """ Set the widget's time format.

        Parameters
        ----------
        format : string
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the
        # same, or convert between the two.
        self.widget.setDisplayFormat(format)
