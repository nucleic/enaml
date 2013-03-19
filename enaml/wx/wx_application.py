#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.application import Application, ProxyResolver

from .wx_deferred_caller import DeferredCall, TimedCall
from .wx_factories import WX_FACTORIES


class WxApplication(Application):
    """ A Wx implementation of an Enaml application.

    A WxApplication uses the Wx toolkit to implement an Enaml UI that
    runs in the local process.

    """
    #: The private QApplication instance.
    _wxapp = Typed(wx.App)

    def __init__(self):
        """ Initialize a WxApplication.

        """
        super(WxApplication, self).__init__()
        self._wxapp = wx.GetApp() or wx.PySimpleApp()
        self.resolver = ProxyResolver(factories=WX_FACTORIES)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the application's main event loop.

        """
        app = self._wxapp
        if not app.IsMainLoopRunning():
            app.MainLoop()

    def stop(self):
        """ Stop the application's main event loop.

        """
        app = self._wxapp
        if app.IsMainLoopRunning():
            app.Exit()

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
        DeferredCall(callback, *args, **kwargs)

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
        TimedCall(ms, callback, *args, **kwargs)

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        return wx.Thread_IsMain()
