#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int

from enaml.widgets.bounded_time import ProxyBoundedTime

from .qt_control import QtControl


# cyclic notification guard flags
CHANGED_GUARD = 0x1


class QtBoundedTime(QtControl, ProxyBoundedTime):
    """ A base class for implementing Qt-Enaml time widgets.

    """
    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Implement in a subclass to create the time widget.

        """
        raise NotImplementedError

    def init_widget(self):
        """ Create and initialize the underlying time widget.

        """
        super(QtBoundedTime, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_time(d.time)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_time_changed(self):
        """ A signal handler for the time changed signal.

        """
        if not self._guard & CHANGED_GUARD:
            self.declaration.time = self.get_time()

    #--------------------------------------------------------------------------
    # Abstract Methods and ProxyBoundedDate API
    #--------------------------------------------------------------------------
    def get_time(self):
        """ Return the current time in the control.

        Returns
        -------
        result : time
            The current control time as a time object.

        """
        raise NotImplementedError

    def set_minimum(self, time):
        """ Set the widget's minimum time.

        Parameters
        ----------
        time : time
            The time object to use for setting the minimum time.

        """
        raise NotImplementedError

    def set_maximum(self, time):
        """ Set the widget's maximum time.

        Parameters
        ----------
        time : time
            The time object to use for setting the maximum time.

        """
        raise NotImplementedError

    def set_time(self, time):
        """ Set the widget's current time.

        Parameters
        ----------
        time : time
            The time object to use for setting the time.

        """
        raise NotImplementedError
