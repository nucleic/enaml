#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from atom.api import Atom, Instance, List, ReadOnly, Enum, Signal, Str, Value

from enaml.widgets.window import Window

from .application import deferred_call
from .resource_manager import ResourceManager
from .socket_interface import ActionSocketInterface
from .utils import make_dispatcher


#: The logger for the session module.
logger = logging.getLogger(__name__)


#: The dispatch function for action dispatching on the session.
dispatch_action = make_dispatcher('on_action_', logger)


class DeferredBatch(Atom):
    """ A class which aggregates batch items.

    Each time an item is added to this object, its tick count is
    incremented and a tick down event is posted to the event queue.
    When the object receives the tick down event, it decrements its
    tick count, and if it's zero, fires the `triggered` signal.

    This allows a consumer of the batch to continually add items and
    have the `triggered` signal fired only when the event queue is
    fully drained of relevant messages.

    """
    #: A signal emitted when the tick count of the batch reaches zero
    #: and the owner of the batch should consume the messages.
    triggered = Signal()

    #: The private list of items contained in the batch.
    _items = Value(factory=list)

    #: The private tick count of the batch.
    _tick = Value(0)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _tick_down(self):
        """ A private handler method which ticks down the batch.

        The tick down events are called in a deferred fashion to allow
        for the aggregation of batch events. When the tick reaches
        zero, the `triggered` signal will be emitted.

        """
        self._tick -= 1
        if self._tick == 0:
            self.triggered.emit()
        else:
            deferred_call(self._tick_down)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def release(self):
        """ Release the items that were added to the batch.

        Returns
        -------
        result : list
            The list of items added to the batch.

        """
        items = self._items
        self._items = []
        return items

    def append(self, item):
        """ Append an item to the batch.

        This will cause the batch to tick up and then start the tick
        down process if necessary.

        Parameters
        ----------
        item : object
            The item to add to the batch.

        """
        self._items.append(item)
        if self._tick == 0:
            deferred_call(self._tick_down)
        self._tick += 1


class Session(Atom):
    """ An object representing the session between a client and its
    Enaml objects.

    The session object is what ensures that each client has their own
    individual instances of objects, so that the only state that is
    shared between simultaneously existing clients is that which is
    explicitly provided by the developer.

    """
    #: Session objects are weakrefable so that it's bound methods can
    #: be used as observers where needed.
    __slots__ = '__weakref__'

    #: The string identifier for this session. This is provided by
    #: the application when the session is opened. The value should
    #: not be manipulated by user code.
    session_id = ReadOnly()

    #: The top level windows which are managed by this session. This
    #: should be populated by user code during the `on_open` method.
    windows = List(Window)

    #: The widget implementation groups which should be used by the
    #: widgets in this session. Widget groups are an advanced feature
    #: which allow the developer to selectively expose toolkit specific
    #: implementations of Enaml widgets. All standard Enaml widgets are
    #: available in the 'default' group. This value will rarely need to
    #: be changed by the user.
    widget_groups = List(Str(), ['default'])

    #: A resource manager used for loading resources for the session.
    resource_manager = Instance(ResourceManager, args=())

    #: The socket used by this session for communication. This is
    #: provided by the Application when the session is activated.
    #: The value should not normally be manipulated by user code.
    socket = Instance(ActionSocketInterface)

    #: The current state of the session. This value is changed by the
    #: by the application as it drives the session through its lifetime.
    #: This should not be manipulated directly by user code.
    state = Enum(
        'default', 'opening', 'opened', 'activating', 'active', 'closing',
        'closed',
    )

    #: A read-only property which is True if the session is inactive.
    is_default = property(lambda self: self.state == 'inactive')

    #: A read-only property which is True if the session is opening.
    is_opening = property(fget=lambda self: self.state == 'opening')

    #: A read-only property which is True if the session is opened.
    is_opened = property(fget=lambda self: self.state == 'opened')

    #: A read-only property which is True if the session is activating.
    is_activating = property(fget=lambda self: self.state == 'activating')

    #: A read-only property which is True if the session is active.
    is_active = property(fget=lambda self: self.state == 'active')

    #: A read-only property which is True if the session is closing.
    is_closing = property(fget=lambda self: self.state == 'closing')

    #: A read-only property which is True if the session is closed.
    is_closed = property(fget=lambda self: self.state == 'closed')

    #: A private dictionary of objects registered with this session.
    #: This value should not be manipulated by user code.
    _registered_objects = Value(factory=dict)

    #: The private deferred message batch used for collapsing layout
    #: related messages into a single batch to send to the client
    #: session for more efficient handling. This value should not be
    #: manipulated by user code.
    _batch = Value()

    def _default__batch(self):
        batch = DeferredBatch()
        batch.triggered.connect(self._on_batch_triggered)
        return batch

    #--------------------------------------------------------------------------
    # Class API
    #--------------------------------------------------------------------------
    @classmethod
    def factory(cls, name='', description='', *args, **kwargs):
        """ Get a SessionFactory instance for this Session class.

        Parameters
        ----------
        name : str, optional
            The name to use for the session instances. The default uses
            the class name.

        description : str, optional
            A human friendly description of the session. The default uses
            the class docstring.

        *args, **kwargs
            Any positional and keyword arguments to pass to the session
            when it is instantiated.

        """
        from enaml.session_factory import SessionFactory
        if not name:
            name = cls.__name__
        if not description:
            description = cls.__doc__
        return SessionFactory(name, description, cls, *args, **kwargs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_batch_triggered(self):
        """ A signal handler for the `triggered` signal on the deferred
        message batch.

        """
        batch = [task() for task in self._batch.release()]
        content = {'batch': batch}
        self.send(self.session_id, 'message_batch', content)

    def _on_window_destroyed(self, change):
        """ A private observer for the `destroyed` event on the windows.

        This handler will remove a destroyed window from the list of
        the session's windows.

        """
        window = change.object
        self.windows.remove(window)
        window.unobserve('destroyed', self._on_window_destroyed)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def on_open(self):
        """ Called by the application when the session is opened.

        This method must be implemented in a subclass and is called to
        create the Enaml objects for the session. This method will only
        be called once during the session lifetime. User code should
        create their windows and assign them to the list of `windows`
        before the method returns.

        """
        raise NotImplementedError

    def on_close(self):
        """ Called by the application when the session is closed.

        This method may be optionally implemented by subclasses so that
        they can perform custom cleaup. After this method returns, the
        session should be considered invalid. This method is only called
        once during the session lifetime.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self, session_id):
        """ Called by the application to open the session.

        This method will call the `on_open` abstract method which must
        be implemented by subclasses. The method should never be called
        by user code.

        Parameters
        ----------
        session_id : str
            The unique identifier to use for this session.

        """
        self.session_id = session_id
        self.state = 'opening'
        self.on_open()
        assert all(isinstance(w, Window) for w in self.windows)
        for window in self.windows:
            window.initialize()
            window.observe('destroyed', self._on_window_destroyed)
        self.state = 'opened'

    def activate(self, socket):
        """ Called by the application to activate the session and its
        windows.

        This method will be called by the Application once during the
        session lifetime. Once this method returns, the session and
        its objects will be ready to send and receive messages. This
        should never be called by user code.

        Parameters
        ----------
        socket : ActionSocketInterface
            A concrete implementation of ActionSocketInterface to use
            for messaging by this session.

        """
        self.state = 'activating'
        for window in self.windows:
            window.activate(self)
        self.socket = socket
        socket.on_message(self.on_message)
        self.state = 'active'

    def close(self):
        """ Called by the application when the session is closed.

        This method will call the `on_close` method which can optionally
        be implemented by subclasses. The method should never be called
        by user code.

        """
        self.send(self.session_id, 'close', {})
        self.state = 'closing'
        self.on_close()
        # The list is copied to avoid issues with the list changing size
        # while iterating. Windows are removed from the `windows` list
        # when they fire their `destroyed` event during destruction.
        for window in self.windows[:]:
            window.destroy()
        self.windows = []
        self._registered_objects = {}
        self.socket.on_message(None)
        self.socket = None
        self.state = 'closed'

    def add_window(self, window):
        """ Add a window to the session's window list.

        This will add the window to the session and create the client
        side window if necessary. If the window
        already exists in the session, this is a no-op.

        Parameters
        ----------
        window : Window
            A new window instance to add to the session. It will not
            normally have a parent, though this is not enforced.

        """
        assert isinstance(window, Window)
        if window not in self.windows:
            self.windows.append(window)
            if self.is_active:
                window.initialize()
                # If the window has no parent, the client session must
                # be told to create it. Otherwise, the window's parent
                # will create it during the children changed event.
                if window.parent is None:
                    content = {'window': window.snapshot()}
                    self.send(self.session_id, 'add_window', content)
                window.activate(self)
                window.observe('destroyed', self._on_window_destroyed)

    def snapshot(self):
        """ Get a snapshot of the windows of this session.

        Returns
        -------
        result : list
            A list of snapshots representing the current windows for
            this session.

        """
        return [window.snapshot() for window in self.windows]

    def register(self, obj):
        """ Register an object with the session.

        This method is called by an Object when it is activated by a
        Session. It should never be called by user code.

        Parameters
        ----------
        obj : Object
            The object to register with the session.

        """
        self._registered_objects[obj.object_id] = obj

    def unregister(self, obj):
        """ Unregister an object from the session.

        This method is called by an Object when it is being destroyed.
        It should never be called by user code.

        Parameters
        ----------
        obj : Object
            The object to unregister from the session.

        """
        self._registered_objects.pop(obj.object_id, None)

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def send(self, object_id, action, content):
        """ Send a message to a client object.

        This method is called by the `Object` instances owned by this
        session to send messages to their client implementations.

        Parameters
        ----------
        object_id : str
            The object id of the client object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        if self.is_active:
            self.socket.send(object_id, action, content)

    def batch(self, object_id, action, content):
        """ Batch a message to be sent by the session.

        This method can be called to add a message to an internal batch
        to be sent to the client at a later time. This is useful for
        queueing messages which are related and are emitted in rapid
        succession, such as `destroy` and `children_changed`. This can
        allow the client-side to batch update the ui, avoiding flicker
        and rendering artifacts. This method should be used with care.

        Parameters
        ----------
        object_id : str
            The object id of the client object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        task = lambda: (object_id, action, content)
        self._batch.append(task)

    def batch_task(self, object_id, action, task):
        """ Similar to `batch` but takes a callable task.

        Parameters
        ----------
        object_id : str
            The object id of the client object.

        action : str
            The action that should be performed by the object.

        task : callable
            A callable which will be invoked at a later time to get
            the content of the message. The callable must return the
            content dictionary for the action.

        """
        ctask = lambda: (object_id, action, task())
        self._batch.append(ctask)

    def on_message(self, object_id, action, content):
        """ Receive a message sent to an object owned by this session.

        This is a handler method registered as the callback for the
        action socket. The message will be routed to the appropriate
        `Object` instance.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        if self.is_active:
            if object_id == self.session_id:
                dispatch_action(self, action, content)
            else:
                try:
                    obj = self._registered_objects[object_id]
                except KeyError:
                    msg = "Invalid object id sent to Session: %s:%s"
                    logger.warn(msg % (object_id, action))
                    return
                else:
                    obj.receive_action(action, content)

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    def on_action_url_request(self, content):
        """ Handle the 'url_request' action from the client session.

        """
        url = content['url']
        metadata = content['metadata']
        reply = URLReply(self, content['id'], url)
        self.resource_manager.load(url, metadata, reply)


class URLReply(Atom):
    """ A reply object for sending a loaded resource to a client session.

    """
    #: The session object for which the url is being requested.
    session = Instance(Session)

    #: The unique id which was sent with  the request.
    request_id = Str()

    #: The url that was sent with the original requested.
    url = Str()

    def __call__(self, resource):
        """ Send the reply to the client session.

        Parameters
        ----------
        resource : Resource
            The loaded resource object, or None if the resource failed
            to load.

        """
        reply = {'id': self.request_id, 'url': self.url}
        if resource is None:
            reply['status'] = 'fail'
        else:
            reply['status'] = 'ok'
            reply['resource'] = resource.snapshot()
        self.session.send(self.session.session_id, 'url_reply', reply)

