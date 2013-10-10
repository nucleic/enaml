#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QObject, QTimer, QEvent, QThread
from .QtGui import QApplication


class DeferredCallEvent(QEvent):
    """ A custom event type for deferred call events.

    """
    __slots__ = ('callback', 'args', 'kwargs')

    Type = QEvent.registerEventType()

    def __init__(self, callback, args, kwargs):
        super(DeferredCallEvent, self).__init__(self.Type)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs


class QDeferredCaller(QObject):
    """ A QObject subclass which handles deferred call events.

    """
    def __init__(self):
        """ Initialize a QDeferredCaller.

        """
        super(QDeferredCaller, self).__init__()
        self.moveToThread(QApplication.instance().thread())

    def customEvent(self, event):
        """ Handle the custom deferred call events.

        """
        if event.type() == DeferredCallEvent.Type:
            event.callback(*event.args, **event.kwargs)

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
        event = DeferredCallEvent(callback, args, kwargs)
        QApplication.postEvent(self, event)


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
    if QThread.currentThread() != QApplication.instance().thread():
        deferredCall(timedCall, ms, callback, *args, **kwargs)
    else:
        QTimer.singleShot(ms, lambda: callback(*args, **kwargs))
