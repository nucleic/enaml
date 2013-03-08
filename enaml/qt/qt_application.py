#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging
import uuid

from enaml.application import Application

from .qt.QtCore import Qt, QThread
from .qt.QtGui import QApplication
from .q_action_socket import QActionSocket
from .q_deferred_caller import deferredCall, timedCall
from .qt_session import QtSession
from .qt_factories import register_default


logger = logging.getLogger(__name__)


# This registers the default Qt factories with the QtWidgetRegistry and
# allows an application access to the default widget implementations.
register_default()


class QtApplication(Application):
    """ A Qt implementation of an Enaml application.

    A QtApplication uses the Qt toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories):
        """ Initialize a QtApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        """
        super(QtApplication, self).__init__(factories)
        self._qapp = QApplication.instance() or QApplication([])
        self._qt_sessions = {}
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
        qt_session = QtSession(session_id, groups)
        self._qt_sessions[session_id] = qt_session
        qt_session.open(session.snapshot())

        # Setup the sockets for the session pair
        server_socket = QActionSocket()
        client_socket = QActionSocket()
        conn = Qt.QueuedConnection
        server_socket.messagePosted.connect(client_socket.receive, conn)
        client_socket.messagePosted.connect(server_socket.receive, conn)

        # Activate the server and client sessions. The server session
        # is activated first so that it is ready to receive messages
        # sent by the client during activation. These messages will
        # typically be requests for resources.
        session.activate(server_socket)
        qt_session.activate(client_socket)

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
        del self._qt_sessions[session_id]

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

