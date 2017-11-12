#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .QtCore import QObject, QTimer, QEvent, QThread
from .QtWidgets import QApplication


class DeferredCallEvent(QEvent):
    """ A custom event type for deferred call events.

    """
    # Explicitly coerce to QEvent.Type for PySide compatibility.
    Type = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback, args, kwargs):
        super(DeferredCallEvent, self).__init__(self.Type)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs


class DeferredCaller(QObject):
    """ A QObject subclass which handles deferred call events.

    """
    def __init__(self):
        """ Initialize a DeferredCaller.

        """
        super(DeferredCaller, self).__init__()
        self.moveToThread(QApplication.instance().thread())

    def customEvent(self, event):
        """ Handle the custom deferred call events.

        """
        if event.type() == DeferredCallEvent.Type:
            event.callback(*event.args, **event.kwargs)


#: A globally available caller instance. This will be created on demand
#: by the globally available caller functions.
__caller = None


def deferredCall(callback, *args, **kwargs):
    """ Execute the callback on the main gui thread.

    This should only be called after the QApplication is created.

    """
    global __caller
    caller = __caller
    if caller is None:
        caller = __caller = DeferredCaller()
    event = DeferredCallEvent(callback, args, kwargs)
    QApplication.postEvent(caller, event)


def timedCall(ms, callback, *args, **kwargs):
    """ Execute a callback on a timer in the main gui thread.

    This should only be called after the QApplication is created.

    """
    if QThread.currentThread() != QApplication.instance().thread():
        deferredCall(timedCall, ms, callback, *args, **kwargs)
    else:
        QTimer.singleShot(ms, lambda: callback(*args, **kwargs))
