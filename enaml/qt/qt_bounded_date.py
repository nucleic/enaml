#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int

from enaml.widgets.bounded_date import ProxyBoundedDate

from .qt_control import QtControl


# cyclic notification guard flags
CHANGED_GUARD = 0x1


class QtBoundedDate(QtControl, ProxyBoundedDate):
    """ A base class for implementing Qt Enaml date widgets.

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
        """ Initialize the date widget.

        """
        super(QtBoundedDate, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_date(d.date)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ A signal handler for the date changed signal.

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
