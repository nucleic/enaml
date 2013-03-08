#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import types

import wx
import wx.lib.newevent

from enaml.socket_interface import ActionSocketInterface
from enaml.weakmethod import WeakMethod


#: A custom event type for posting messages on the socket.
wxActionSocketEvent, EVT_ACTION_SOCKET = wx.lib.newevent.NewEvent()


class wxActionSocket(wx.EvtHandler):
    """ A concrete implementation of ActionSocketInterface.

    This is a wxEvtHandler subclass which converts a `send` on the
    socket into an `EVT_ACTION_SOCKET` event which can be bound to
    another part of the application. Incoming socket events can be
    delivered to the `receive` method of the socket.

    """
    def __init__(self):
        """ Initialize a wxActionSocket.

        """
        super(wxActionSocket, self).__init__()
        self._callback = None

    def on_message(self, callback):
        """ Register a callback for receiving messages sent by a client
        object.

        Parameters
        ----------
        callback : callable
            A callable with an argument signature that is equivalent to
            the `send` method. If the callback is a bound method, then
            the lifetime of the callback will be bound to lifetime of
            the method owner object.

        """
        if isinstance(callback, types.MethodType):
            callback = WeakMethod(callback)
        self._callback = callback

    def send(self, object_id, action, content):
        """ Send the action to any attached listeners.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        event = wxActionSocketEvent(
            object_id=object_id, action=action, content=content,
        )
        wx.PostEvent(self, event)

    def receive(self, event):
        """ Receive a message sent to the socket.

        The message will be routed to the registered callback, if one
        exists.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        callback = self._callback
        if callback is not None:
            callback(event.object_id, event.action, event.content)


ActionSocketInterface.register(wxActionSocket)

