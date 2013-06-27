#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QObject, QTimer, Qt, Signal
from .QtGui import QApplication


class QDeferredCaller(QObject):
    """ A QObject subclass which facilitates executing callbacks on the
    main application thread.

    """
    _posted = Signal(object)

    def __init__(self):
        """ Initialize a QDeferredCaller.

        """
        super(QDeferredCaller, self).__init__()
        app = QApplication.instance()
        if app is not None:
            self.moveToThread(app.thread())
        self._posted.connect(self._onPosted, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onPosted(self, callback):
        """ A private signal handler for the '_callbackPosted' signal.

        This handler simply executes the callback.

        """
        callback()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def deferredCall(self, callback, *args, **kwargs):
        """ Execute the callback on the main gui thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute on the main thread.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        f = lambda: callback(*args, **kwargs)
        self._posted.emit(f)

    def timedCall(self, ms, callback, *args, **kwargs):
        """ Execute a callback on a timer in the main gui thread.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at on the timer.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        f = lambda: callback(*args, **kwargs)
        f2 = lambda: QTimer.singleShot(ms, f)
        self._posted.emit(f2)


#: A globally available caller instance. This will be created on demand
#: by the globally available caller functions.
_caller = None


def deferredCall(callback, *args, **kwargs):
    """ Execute the callback on the main gui thread.

    This is a convenience wrapper around QDeferredCaller.deferredCall.
    This should only be called after the QApplication is created.

    """
    global _caller
    c = _caller
    if c is None:
        c = _caller = QDeferredCaller()
    c.deferredCall(callback, *args, **kwargs)


def timedCall(ms, callback, *args, **kwargs):
    """ Execute a callback on a timer in the main gui thread.

    This is a convenience wrapper around QDeferredCaller.timedCall.
    This should only be called after the QApplication is created.

    """
    global _caller
    c = _caller
    if c is None:
        c = _caller = QDeferredCaller()
    c.timedCall(ms, callback, *args, **kwargs)
