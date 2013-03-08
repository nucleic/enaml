#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class ActionSocketInterface(object):
    """ An abstract base class defining an action socket interface.

    Concrete implementations of this interface can be used by Session
    instances to send and recieve messages to and from their client
    objects.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_message(self, callback):
        """ Register a callback for receiving messages sent by a
        client object.

        Parameters
        ----------
        callback : callable
            A callable with an argument signature that is equivalent to
            the `send` method. If the callback is a bound method, then
            the lifetime of the callback will be bound to lifetime of
            the method owner object.

        """
        raise NotImplementedError

    @abstractmethod
    def send(self, object_id, action, content):
        """ Send an action to the client of an object.

        Parameters
        ----------
        object_id : str
            The object id for the Object sending the message.

        action : str
            The action that should be take by the client object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        raise NotImplementedError

