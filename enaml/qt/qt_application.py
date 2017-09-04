#------------------------------------------------------------------------------
# Copyright (c) 2014-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.application import Application, ProxyResolver

from .QtCore import QThread
from .QtWidgets import QApplication

from .q_deferred_caller import deferredCall, timedCall
from .qt_factories import QT_FACTORIES
from .qt_mime_data import QtMimeData


class QtApplication(Application):
    """ A Qt implementation of an Enaml application.

    A QtApplication uses the Qt toolkit to implement an Enaml UI that
    runs in the local process.

    """
    #: The private QApplication instance.
    _qapp = Typed(QApplication)

    def __init__(self):
        """ Initialize a QtApplication.

        """
        super(QtApplication, self).__init__()
        self._qapp = QApplication.instance() or QApplication([])
        self.resolver = ProxyResolver(factories=QT_FACTORIES)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the application's main event loop.

        """
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False

    def stop(self):
        """ Stop the application's main event loop.

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        deferredCall(callback, *args, **kwargs)

    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        timedCall(ms, callback, *args, **kwargs)

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        return QThread.currentThread() == self._qapp.thread()

    def create_mime_data(self):
        """ Create a new mime data object to be filled by the user.

        Returns
        -------
        result : QtMimeData
            A concrete implementation of the MimeData class.

        """
        return QtMimeData()
