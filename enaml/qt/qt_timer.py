#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.timer import ProxyTimer

from .QtCore import QTimer

from .qt_toolkit_object import QtToolkitObject


class QtTimer(QtToolkitObject, ProxyTimer):
    """ A Qt implementation of an Enaml ProxyTimer.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QTimer)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying timer object.

        """
        self.widget = QTimer()

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtTimer, self).init_widget()
        d = self.declaration
        self.set_interval(d.interval)
        self.set_single_shot(d.single_shot)
        self.widget.timeout.connect(self.on_timeout)

    def destroy(self):
        """ A reimplemented destructor.

        This stops the timer before invoking the superclass destructor.

        """
        self.widget.stop()
        super(QtTimer, self).destroy()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_timeout(self):
        """ Handle the timeout signal for the timer.

        """
        d = self.declaration
        if d is not None:
            d.timeout()

    #--------------------------------------------------------------------------
    # ProxyTimer API
    #--------------------------------------------------------------------------
    def set_interval(self, interval):
        """ Set the interval on the timer.

        """
        self.widget.setInterval(interval)

    def set_single_shot(self, single_shot):
        """ Set the single shot flag on the timer.

        """
        self.widget.setSingleShot(single_shot)

    def start(self):
        """ Start or restart the timer.

        """
        self.widget.start()

    def stop(self):
        """ Stop the timer.

        """
        self.widget.stop()

    def is_running(self):
        """ Get whether or not the timer is running.

        """
        return self.widget.isActive()
