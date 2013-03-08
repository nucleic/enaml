#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import logging

from atom.api import Atom, Constant, Event, Value, Instance, null

from enaml.utils import LoopbackGuard, make_dispatcher, id_generator

from .object import Object


#: The logger handler for the messenger module.
logger = logging.getLogger(__name__)


#: The id generator for Messenger objects.
object_id_generator = id_generator('o_')


#: The dispatch function for action dispatching.
dispatch_action = make_dispatcher('on_action_', logger)


class ChildTask(object):
    """ A task for posting a children changed event to a client.

    """
    __slots__ = ('_parent', '_removed', '_added')

    def __init__(self, parent):
        """ Initialize a ChildrenChangedTask.

        Parameters
        ----------
        parent : Object
            The object to which the children event was posted.

        """
        self._parent = parent
        self._removed = set()
        self._added = set()

    def child_added(self, child):
        """ Called to add a child to the task.

        """
        if child in self._removed:
            self._removed.remove(child)
        else:
            self._added.add(child)

    def child_removed(self, child):
        """ Called to remove a child from the task.

        """
        if child in self._added:
            self._added.remove(child)
        else:
            self._removed.add(child)

    def __call__(self):
        """ Create the content dictionary for the task.

        This method will initialize and activate the messenger objects
        which were added to the parent.

        """
        parent = self._parent
        added = self._added
        removed = self._removed
        content = {}
        snap = parent.snap_children()
        content['order'] = [child.object_id for child in snap]
        content['added'] = [child.snapshot() for child in added]
        content['removed'] = [child.object_id for child in removed]
        session = parent.session
        for child in added:
            if not child.is_active:
                child.activate(session)
        self._parent = None        # break the ref-cycle
        del parent._child_task     # a task is 1-time use
        return content


class Messenger(Atom):
    """ A mixin class for creating messaging enabled Enaml objects.

    This class must be mixed in with a class inheriting from Object.

    """
    #: A constant value which is the object's unique identifier. The
    #: identifier is guaranteed to be unique for the current process.
    object_id = Constant(factory=object_id_generator.next)

    #: A read-only property which returns the messengers's session.
    session = property(lambda self: self._session)

    #: The current lifetime state of the messenger within the session.
    #: This redefines the Object state to add the needed values for the
    #: messenger. This value should not be manipulated by user code.
    state = Object.state.extend('activating', 'active')

    #: A read-only property indicating if the messenger is activating.
    is_activating = property(lambda self: self.state == 'activating')

    #: A read-only property indicating if the messenger is active.
    is_active = property(lambda self: self.state == 'active')

    #: An event fired when an object has been activated. It is emitted
    #: once during an object's lifetime, when the object is activated
    #: by a Session.
    activated = Event()

    #: A loopback guard which can be used to prevent a notification
    #: cycle when setting attributes from within an action handler.
    loopback_guard = Instance(LoopbackGuard, factory=LoopbackGuard)

    #: Private storage values. These should *never* be manipulated by
    #: user code. For performance reasons, these are not type checked.
    _session = Value()      # Session or None
    _child_task = Value()   # ChildTask or None

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def activate(self, session):
        """ Called by a Session to activate the object tree.

        This method is called by a Session object to activate the object
        tree for messaging.

        Parameters
        ----------
        session : Session
            The session to use for messaging with this object tree.

        """
        self.state = 'activating'
        self._session = session
        session.register(self)
        isinst = isinstance
        target = Messenger
        for child in self.children:
            if isinst(child, target):
                child.activate(session)
        self.state = 'active'
        self.activated()

    def send_action(self, action, content):
        """ Send an action to the client of this object.

        The action will only be sent if the current state of the object
        is `active`. Subclasses may reimplement this method if more
        control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            self._session.send(self.object_id, action, content)

    def batch_action(self, action, content):
        """ Batch an action to be sent to the client at a later time.

        The action will only be batched if the current state of the
        object is `active`. Subclasses may reimplement this method
        if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            self._session.batch(self.object_id, action, content)

    def batch_action_task(self, action, task):
        """ Similar to `batch_action` but takes a callable task.

        The task will only be batched if the current state of the
        object is `active`. Subclasses may reimplement this method
        if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        task : callable
            A callable which will be invoked at a later time. It must
            return the content dictionary for the action.

        """
        if self.is_active:
            self._session.batch_task(self.object_id, action, task)

    def receive_action(self, action, content):
        """ Receive an action from the client of this object.

        The default implementation will dynamically dispatch the action
        to specially named handlers if the current state of the object
        is 'active'. Subclasses may reimplement this method if more
        control is needed.

        Parameters
        ----------
        action : str
            The name of the action to perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            dispatch_action(self, action, content)

    def snapshot(self):
        """ Get a dictionary representation of the object tree.

        This method can be called to get a dictionary representation of
        the current state of the widget tree which can be used by client
        side implementation to construct their own implementation tree.

        Returns
        -------
        result : dict
            A serializable dictionary representation of the widget tree
            from this widget down.

        """
        snap = {}
        snap['object_id'] = self.object_id
        snap['name'] = self.name
        snap['class'] = self.class_name()
        snap['bases'] = self.base_names()
        snap['children'] = [c.snapshot() for c in self.snap_children()]
        return snap

    def snap_children(self):
        """ Get an iterable of children to include in the snapshot.

        The default implementation returns the list of children which
        are instances of Messenger. Subclasses may reimplement this
        method if more control is needed.

        Returns
        -------
        result : list
            The list of children which are instances of Messenger.

        """
        isinst = isinstance
        target = Messenger
        return (child for child in self.children if isinst(child, target))

    def class_name(self):
        """ Get the name of the class for this instance.

        Returns
        -------
        result : str
            The name of the class of this instance.

        """
        return type(self).__name__

    def base_names(self):
        """ Get the list of base class names for this instance.

        Returns
        -------
        result : list
            The list of string names for the base classes of this
            instance. The list starts with the parent class of this
            instance and terminates with Object.

        """
        names = []
        for base in type(self).mro()[1:]:
            names.append(base.__name__)
            if base is Object:
                break
        return names

    def send_member_change(self, change):
        """ A member change handler which updates the client widget.

        This handler is a convenience which can be used as an observer
        for a member change. It will proxy the state change to the
        client widget.

        """
        name = change.name
        if change.old is not null and name not in self.loopback_guard:
            self.send_action('set_' + name, {name: change.new})

    def set_guarded(self, **attrs):
        """ Set attribute values from within a loopback guard.

        This is a convenience method provided for subclasses to set the
        values of attributes from within a loopback guard. This prevents
        the change from being proxied back to client and reduces the
        chances of getting hung in a feedback loop.

        Parameters
        ----------
        **attrs
            The attributes to set on the widget from within a loopback
            guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def destroy(self):
        """ An overridden destructor method.

        This will batch a 'destroy' message to the client widget if the
        parent of this object is not being destroyed. In this way, only
        the top-level widgets send destroy events, reducing chatter.

        """
        parent = self._parent
        if parent is None or not parent.is_destroying:
            self.batch_action('destroy', {})
        super(Messenger, self).destroy()
        session = self._session
        if session is not None:
            session.unregister(self)

    def child_removed(self, child):
        """ Handle the child removed event for the widget.

        """
        super(Messenger, self).child_removed(child)
        if self.is_active and isinstance(child, Messenger):
            task = self._child_task
            if task is None:
                task = self._child_task = ChildTask(self)
                self.batch_action_task('children_changed', task)
            task.child_removed(child)

    def child_added(self, child):
        """ Handle the child added event for the widget.

        """
        super(Messenger, self).child_added(child)
        if self.is_active and isinstance(child, Messenger):
            task = self._child_task
            if task is None:
                task = self._child_task = ChildTask(self)
                self.batch_action_task('children_changed', task)
            task.child_added(child)
