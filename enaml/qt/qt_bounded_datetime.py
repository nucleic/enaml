#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int

from enaml.widgets.bounded_datetime import ProxyBoundedDatetime

from .qt_control import QtControl


# cyclic notification guard flags
CHANGED_GUARD = 0x1


class QtBoundedDatetime(QtControl, ProxyBoundedDatetime):
    """ A base class for implementing Qt Enaml datetime widgets.

    """
    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Implement in a subclass to create the datetime widget.

        """
        raise NotImplementedError

    def init_widget(self):
        """ Create and initialize the underlying datetime widget.

        """
        super(QtBoundedDatetime, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_datetime(d.datetime)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_datetime_changed(self):
        """ A signal handler for the datetime changed signal.

        """
        if not self._guard & CHANGED_GUARD:
            self.declaration.datetime = self.get_datetime()

    #--------------------------------------------------------------------------
    # Abstract Methods and ProxyBoundedDate API
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control.

        Returns
        -------
        result : datetime
            The current control datetime as a datetime object.

        """
        raise NotImplementedError

    def set_minimum(self, datetime):
        """ Set the widget's minimum datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the minimum datetime.

        """
        raise NotImplementedError

    def set_maximum(self, datetime):
        """ Set the widget's maximum datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the maximum datetime.

        """
        raise NotImplementedError

    def set_datetime(self, datetime):
        """ Set the widget's current datetime.

        Parameters
        ----------
        datetime : datetime
            The datetime object to use for setting the datetime.

        """
        raise NotImplementedError
