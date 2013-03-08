#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import types

from enaml.socket_interface import ActionSocketInterface
from enaml.weakmethod import WeakMethod

from .qt.QtCore import QObject, Signal


class QActionSocket(QObject):
    """ A concrete implementation of ActionSocketInterface.

    This is a QObject subclass which converts a `send` on the socket
    into a `messagePosted` signal which can be connected to another
    part of the application. Incoming socket messages can be delivered
    to the `receive` method of the socket.

    """
    #: A signal emitted when a message has been sent on the socket.
    messagePosted = Signal(object, object, object)

    def __init__(self):
        """ Initialize a QActionSocket.

        """
        super(QActionSocket, self).__init__()
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
        self.messagePosted.emit(object_id, action, content)

    def receive(self, object_id, action, content):
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
            callback(object_id, action, content)


ActionSocketInterface.register(QActionSocket)

