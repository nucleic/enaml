#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
import logging

from enaml.utils import make_dispatcher

from .qt_resource_manager import QtResourceManager
from .qt_widget_registry import QtWidgetRegistry


logger = logging.getLogger(__name__)


#: The dispatch function for action dispatching.
dispatch_action = make_dispatcher('on_action_', logger)


class URLRequest(object):
    """ A simple object for making url requests.

    """
    def __init__(self, session):
        """ Initialize a URLRequest.

        Parameters
        ----------
        session : Session
            The session object for which the url is being requested.

        """
        self._session = session

    def __call__(self, req_id, url, metadata):
        """ Make a request for the given url resource.

        Parameters
        ----------
        req_id : str
            A unique identifier for this request.

        url : str
            The resource url which should be requested.

        metadata : dict
            Additional metadata to pass along with the request.

        Returns
        -------
        result : bool

        """
        content = {}
        content['id'] = req_id
        content['url'] = url
        content['metadata'] = metadata
        session = self._session
        session.send(session._session_id, 'url_request', content)


class QtSession(object):
    """ An object which manages a session of Qt client objects.

    """
    def __init__(self, session_id, widget_groups):
        """ Initialize a QtSession.

        Parameters
        ----------
        session_id : str
            The string identifier for this session.

        widget_groups : list of str
            The list of string widget groups for this session.

        """
        self._session_id = session_id
        self._widget_groups = widget_groups
        self._resource_manager = QtResourceManager()
        self._registered_objects = {}
        self._windows = []
        self._socket = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self, snapshot):
        """ Open the session using the given snapshot.

        Parameters
        ----------
        snapshot : list of dicts
            The list of tree snapshots to build for this session.

        """
        windows = self._windows
        for tree in snapshot:
            window = self.build(tree, None)
            if window is not None:
                windows.append(window)
                window.initialize()

    def activate(self, socket):
        """ Active the session and its windows.

        Parameters
        ----------
        socket : ActionSocketInterface
            The socket interface to use for messaging with the server
            side Enaml objects.

        """
        # Setup the socket before activation so that widgets may
        # request resources from the server for startup purposes.
        self._socket = socket
        socket.on_message(self.on_message)
        for window in self._windows:
            window.activate()

    def build(self, tree, parent):
        """ Build and return a new widget using the given tree dict.

        Parameters
        ----------
        tree : dict
            The dictionary snapshot representation of the tree of
            items to build.

        parent : QtObject or None
            The parent for the tree, or None if the tree is top-level.

        Returns
        -------
        result : QtObject or None
            The object representation of the root of the tree, or None
            if it could not be built. If the object cannot be built,
            the building errors will be sent to the error logger.

        """
        groups = self._widget_groups
        factory = QtWidgetRegistry.lookup(tree['class'], groups)
        if factory is None:
            for class_name in tree['bases']:
                factory = QtWidgetRegistry.lookup(class_name, groups)
                if factory is not None:
                    break
        if factory is None:
            msg =  'Unhandled object type: %s:%s'
            item_class = tree['class']
            item_bases = tree['bases']
            logger.error(msg % (item_class, item_bases))
            return
        obj = factory().construct(tree, parent, self)
        for child in tree['children']:
            self.build(child, obj)
        return obj

    def register(self, obj):
        """ Register an object with the session.

        QtObjects are registered automatically during construction.

        Parameters
        ----------
        obj : QtObject
            The QtObject to register with the session.

        """
        self._registered_objects[obj.object_id()] = obj

    def unregister(self, obj):
        """ Unregister an object from the session.

        QtObjects are unregistered automatically during destruction.

        Parameters
        ----------
        obj : QtObject
            The QtObject to unregister from the session.

        """
        self._registered_objects.pop(obj.object_id(), None)

    def lookup(self, object_id):
        """ Lookup a registered object with the given object id.

        Parameters
        ----------
        object_id : str
            The object id for the object to lookup.

        Returns
        -------
        result : QtObject or None
            The registered QtObject with the given identifier, or None
            if no registered object is found.

        """
        return self._registered_objects.get(object_id)

    def load_resource(self, url, metadata=None):
        """ Asynchronously Load the resource pointed to by the given url.

        Parameters
        ----------
        url : str
            The url pointed to the resource that should be loaded.

        metadata : dict, optional
            Additional metadata required by the session to load the
            requested resource.

        Returns
        -------
        result : DeferredResource
            A deferred object which will invoke a callback when the
            resource for the url is loaded.

        """
        if metadata is None:
            metadata = {}
        request = URLRequest(self)
        return self._resource_manager.load(url, metadata, request)

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def send(self, object_id, action, content):
        """ Send a message to a server object.

        This method is called by the `QtObject` instances owned by this
        session to send messages to their server implementations.

        Parameters
        ----------
        object_id : str
            The object id of the server object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        socket = self._socket
        if socket is not None:
            socket.send(object_id, action, content)

    def on_message(self, object_id, action, content):
        """ Receive a message sent to an object owned by this session.

        This is a handler method registered as the callback for the
        action socket. The message will be routed to the appropriate
        `QtObject` instance.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        if object_id == self._session_id:
            dispatch_action(self, action, content)
        else:
            try:
                obj = self._registered_objects[object_id]
            except KeyError:
                msg = "Invalid object id sent to QtSession: %s:%s"
                logger.warn(msg % (object_id, action))
                return
            else:
                obj.receive_action(action, content)

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    def on_action_add_window(self, content):
        """ Handle the 'add_window' action from the Enaml session.

        """
        window = self.build(content['window'], None)
        if window is not None:
            self._windows.append(window)
            window.initialize()
            window.activate()

    def on_action_url_reply(self, content):
        """ Handle the 'url_reply' action from the Enaml session.

        """
        url = content['url']
        req_id = content['id']
        status = content['status']
        manager = self._resource_manager
        if status == 'ok':
            resource = content['resource']
            manager.on_load(req_id, url, resource)
        else:
            manager.on_fail(req_id, url)

    def on_action_message_batch(self, content):
        """ Handle the 'message_batch' action sent by the Enaml session.

        Actions sent to the message batch are processed in the following
        order 'children_changed' -> 'destroy' -> 'relayout' -> other...

        """
        actions = defaultdict(list)
        for item in content['batch']:
            action = item[1]
            actions[action].append(item)
        ordered = []
        batch_order = ('children_changed', 'destroy', 'relayout')
        for key in batch_order:
            ordered.extend(actions.pop(key, ()))
        for value in actions.itervalues():
            ordered.extend(value)
        objects = self._registered_objects
        for object_id, action, msg_content in ordered:
            try:
                obj = objects[object_id]
            except KeyError:
                msg = "Invalid object id sent to QtSession %s:%s"
                logger.warn(msg % (object_id, action))
            else:
                dispatch_action(obj, action, msg_content)

    def on_action_close(self, content):
        """ Handle the 'close' action sent by the Enaml session.

        """
        for window in self._windows:
            window.destroy()
        self._windows = []
        self._registered_objects = {}
        self._resource_manager = None
        self._socket.on_message(None)
        self._socket = None

