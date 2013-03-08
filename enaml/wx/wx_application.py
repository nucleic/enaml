#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging
import uuid

import wx

from enaml.application import Application

from .wx_action_socket import wxActionSocket, EVT_ACTION_SOCKET
from .wx_deferred_caller import DeferredCall, TimedCall
from .wx_session import WxSession
from .wx_factories import register_default


logger = logging.getLogger(__name__)


# This registers the default Wx factories with the WxWidgetRegistry and
# allows an application access to the default widget implementations.
register_default()


class WxApplication(Application):
    """ A concrete implementation of an Enaml application.

    A WxApplication uses the Wx toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories):
        """ Initialize a WxApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        """
        super(WxApplication, self).__init__(factories)
        self._wxapp = wx.GetApp() or wx.PySimpleApp()
        self._wx_sessions = {}
        self._sessions = {}

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def start_session(self, name):
        """ Start a new session of the given name.

        This method will create a new session object for the requested
        session type and return the new session_id. If the session name
        is invalid, an exception will be raised.

        Parameters
        ----------
        name : str
            The name of the session to start.

        Returns
        -------
        result : str
            The unique identifier for the created session.

        """
        if name not in self._named_factories:
            raise ValueError('Invalid session name')

        # Create and open a new server-side session.
        factory = self._named_factories[name]
        session = factory()
        session_id = uuid.uuid4().hex
        session.open(session_id)
        self._sessions[session_id] = session

        # Create and open a new client-side session.
        groups = session.widget_groups[:]
        wx_session = WxSession(session_id, groups)
        self._wx_sessions[session_id] = wx_session
        wx_session.open(session.snapshot())

        # Setup the sockets for the session pair
        server_socket = wxActionSocket()
        client_socket = wxActionSocket()
        server_socket.Bind(EVT_ACTION_SOCKET, client_socket.receive)
        client_socket.Bind(EVT_ACTION_SOCKET, server_socket.receive)

        # Activate the server and client sessions. The server session
        # is activated first so that it is ready to receive messages
        # sent by the client during activation. These messages will
        # typically be requests for resources.
        session.activate(server_socket)
        wx_session.activate(client_socket)

        return session_id

    def end_session(self, session_id):
        """ End the session with the given session id.

        This method will close down the existing session. If the session
        id is not valid, an exception will be raised.

        Parameters
        ----------
        session_id : str
            The unique identifier for the session to close.

        """
        if session_id not in self._sessions:
            raise ValueError('Invalid session id')
        self._sessions.pop(session_id).close()
        del self._wx_sessions[session_id]

    def session(self, session_id):
        """ Get the session for the given session id.

        Parameters
        ----------
        session_id : str
            The unique identifier for the session to retrieve.

        Returns
        -------
        result : Session or None
            The session object with the given id, or None if the id
            does not correspond to an active session.

        """
        return self._sessions.get(session_id)

    def sessions(self):
        """ Get the currently active sessions for the application.

        Returns
        -------
        result : list
            The list of currently active sessions for the application.

        """
        return self._sessions.values()

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

