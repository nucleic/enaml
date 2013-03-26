#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx


class wxDeferredCaller(object):
    """ A simple object which facilitates running callbacks on the main
    application thread.

    """
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def DeferredCall(self, callback, *args, **kwargs):
        """ Execute the callback on the main gui thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute on the main thread.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        wx.CallAfter(callback, *args, **kwargs)

    def TimedCall(self, ms, callback, *args, **kwargs):
        """ Execute a callback on timer in the main gui thread.

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
        f = lambda: wx.CallLater(ms, callback, *args, **kwargs)
        wx.CallAfter(f)


#: A globally available caller instance. This will be created on demand
#: by the globally available caller functions.
_caller = None


def DeferredCall(callback, *args, **kwargs):
    """ Execute the callback on the main gui thread.

    This is a convenience wrapper around QDeferredCaller.deferredCall.
    This should only be called after the QApplication is created.

    """
    global _caller
    c = _caller
    if c is None:
        c = _caller = wxDeferredCaller()
    c.DeferredCall(callback, *args, **kwargs)


def TimedCall(ms, callback, *args, **kwargs):
    """ Execute a callback on a timer in the main gui thread.

    This is a convenience wrapper around QDeferredCaller.timedCall.
    This should only be called after the QApplication is created.

    """
    global _caller
    c = _caller
    if c is None:
        c = _caller = wxDeferredCaller()
    c.TimedCall(ms, callback, *args, **kwargs)
