#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import functools
import logging

from enaml.utils import LoopbackGuard, make_dispatcher

from .qt.QtCore import QObject
from .q_deferred_caller import deferredCall


logger = logging.getLogger(__name__)


#: The dispatch function for action dispatching.
dispatch_action = make_dispatcher('on_action_', logger)


def deferred_updates(func):
    """ A method decorator which will defer widget updates.

    When used as a decorator for a QtObject, this will disable updates
    on the underlying widget, and re-enable them on the next cycle of
    the event loop after the method returns.

    Parameters
    ----------
    func : function
        A function object defined as a method on a QtObject.

    """
    @functools.wraps(func)
    def closure(self, *args, **kwargs):
        widget = self.widget()
        if widget is not None and widget.isWidgetType():
            widget.setUpdatesEnabled(False)
            try:
                res = func(self, *args, **kwargs)
            finally:
                deferredCall(widget.setUpdatesEnabled, True)
        else:
            res = func(self, *args, **kwargs)
        return res
    return closure


class QtObject(object):
    """ The most base class of all client objects for the Enaml Qt
    implementation.

    """
    @classmethod
    def construct(cls, tree, parent, session):
        """ Construct the QtObject instance for the given parameters.

        This classmethod is called by the QtSession object which owns
        the object being built. When called, it creates a new instance
        of the class by extracting the object id from the snapshot and
        calling the class' constructor. It then invokes the `create`
        method on the new instance. This classmethod exists for cases
        where it is necessary to define custom construction behavior.
        A subclass may reimplement this method as required.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot dict representing an object tree from this
            object downward.

        parent : QtObject or None
            The parent QtObject to use for this object, or None if this
            object is top-level.

        session : QtSession
            The QtSession object which owns this object. The session is
            used for sending messages to the server side widgets.

        Returns
        -------
        result : QtObject
            The QtObject instance for these parameters.

        Notes
        -----
        This method does *not* construct the children for this object.
        That responsibility lies with the QtSession object which calls
        this constructor.

        """
        object_id = tree['object_id']
        self = cls(object_id, parent, session)
        self.create(tree)
        session.register(self)
        return self

    def __init__(self, object_id, parent, session):
        """ Initialize a QtObject.

        Parameters
        ----------
        object_id : str
            The unique identifier to use with this object.

        parent : QtObject or None
            The parent object of this object, or None if this object
            has no parent.

        session : QtSession
            The QtSession object which owns this object. The session is
            used for sending messages to the server side widgets.

        """
        self._object_id = object_id
        self._session = session
        self._parent = None
        self._children = []
        self._widget = None
        self._initialized = False
        self._destroying = False
        self.set_parent(parent)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def loopback_guard(self):
        """ Lazily creates and returns a LoopbackGuard for convenient
        use by subclasses.

        """
        try:
            guard = self._loopback_guard
        except AttributeError:
            guard = self._loopback_guard = LoopbackGuard()
        return guard

    #--------------------------------------------------------------------------
    # Object Methods
    #--------------------------------------------------------------------------
    def object_id(self):
        """ Get the object id for the object.

        Returns
        -------
        result : str
            The unique identifier for this object.

        """
        return self._object_id

    def widget(self):
        """ Get the toolkit-specific object for this object.

        Returns
        -------
        result : QObject or None
            The toolkit object for this object, or None if it does not
            have a toolkit object.

        """
        return self._widget

    def parent_widget(self):
        """ Get the toolkit-specific parent widget for this object.

        Returns
        -------
        result : QObject or None
            The toolkit object for this object, or None if it does
            not exist.

        """
        parent = self._parent
        if parent is not None:
            parent = parent.widget()
        return parent

    def create_widget(self, parent, tree):
        """ A method which should be reimplemented by subclasses.

        This method is called by the create(...) method. It should
        create and return the underlying Qt widget. Implementations
        of this method should *not* call the superclass version.

        Parameters
        ----------
        parent : QObject or None
            The parent Qt toolkit object for this control, or None if
            the control does not have a parent.

        tree : dict
            The dictionary representation of the tree for this object.
            This is provided in the even that the component needs to
            create a different type of widget based on the information
            in the tree.

        """
        return QObject()

    def create(self, tree):
        """ A method called by the application when creating the UI.

        The default implementation of this method calls 'create_widget'
        and assigns the results to the 'widget' attribute, so subclasses
        must be sure to call the superclass method as the first order of
        business.

        This method is called by the application in a top-down fashion.

        Parameters
        ----------
        tree : dict
            The dictionary representation of the tree for this object.

        """
        parent = self._parent
        parent_widget = parent.widget() if parent else None
        self._widget = self.create_widget(parent_widget, tree)

    def initialized(self):
        """ Get whether or not this object is initialized.

        Returns
        -------
        result : bool
            True if this object has been initialized, False otherwise.

        """
        return self._initialized

    def initialize(self):
        """ A method called by the application to initialize the UI.

        This method is called by the application to allow the object
        tree perform any post-create initialization required. This
        method should only be called once. Multiple calls to this
        method are ignored.

        """
        if not self._initialized:
            for child in self.children():
                child.initialize()
            self.init_layout()
            self._initialized = True

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization related to layout.

        The default implementation of this method is a no-op in order
        to be super() friendly.

        This method is called by the application in a bottom-up order.

        """
        pass

    def activate(self):
        """ A method called by the session to activate the UI.

        This method is called by the session after the server side
        session has indicated it is ready to accept messages. This
        provides the object tree to make initial request for data
        from the server side objects.

        """
        for child in self.children():
            child.activate()

    def destroy(self):
        """ Destroy this object.

        After an object is destroyed, it is no longer usable and should
        be discarded. All internal references to the object will be
        removed.

        """
        # Set the destroying flag to True so objects can optimize
        # their destruction behavior.
        self._destroying = True

        # Destroy the children before destroying the underlying widget
        # this gives the children the opportunity to perform cleanup
        # with an intact parent before being destroyed. Destroying a
        # child will cause it to be removed from the parent, so the
        # list is copied to ensure proper iteration.
        for child in self._children[:]:
            child.destroy()
        self._children = []

        # Only after the children are destroyed is the intialized flag
        # set to False. This allows a child which is being destroyed
        # to fire off the child_removed event on the parent so that
        # the parent can do cleanup before the child is destroyed.
        self._initialized = False

        # Fire the child_removed event immediately, so a child can be
        # removed from any auxiliary container they parent may have
        # placed it in, before the underlying widget is destroyed.
        parent = self._parent
        if parent is not None:
            if self in parent._children:
                parent._children.remove(self)
                if parent._initialized:
                    parent.child_removed(self)
            self._parent = None

        # Finally, unparent the underlying toolkit widget. Since there
        # should no longer be any public references to it, it will be
        # garbage collected and destroyed. This appears to be a safer
        # approach than calling widget.deleteLater().
        widget = self._widget
        if widget is not None:
            widget.setParent(None)
            self._widget = None

        # Remove what should be the last remaining strong references to
        # `self` which will allow this object to be garbage collected.
        self._session.unregister(self)
        self._session = None

    #--------------------------------------------------------------------------
    # Parenting Methods
    #--------------------------------------------------------------------------
    def parent(self):
        """ Get the parent of this QtObject.

        Returns
        -------
        result : QtObject or None
            The parent object of this object, or None if it has no
            parent.

        """
        return self._parent

    def children(self):
        """ Get the children of this object.

        Returns
        -------
        result : list
            The list of children of this object. This list should not
            be modified in place by user code.

        """
        return self._children

    def set_parent(self, parent):
        """ Set the parent for this object.

        If the parent is already initialized, then the `child_removed`
        and `child_added` events will be emitted on the parent. Updates
        on the widget are disabled until after the child events on the
        parent have been processed.

        Parameters
        ----------
        parent : QtObject or None
            The parent of this object, or None if it has no parent.

        """
        # Note: If this object is not yet fully intialized, then the
        # added/removed events must be executed on the next cycle of
        # the event loop. It's possible that this method is being called
        # from the `construct` class method and the toolkit widget will
        # not yet exist. This means that child event handlers that rely
        # on the child toolkit widget existing will fail.
        curr = self._parent
        if curr is parent or parent is self:
            return

        self._parent = parent
        if curr is not None:
            if self in curr._children:
                curr._children.remove(self)
                if curr._initialized:
                    if self._initialized:
                        curr.child_removed(self)
                    else:
                        deferredCall(curr.child_removed, self)

        if parent is not None:
            parent._children.append(self)
            if parent._initialized:
                if self._initialized:
                    parent.child_added(self)
                else:
                    deferredCall(parent.child_added, self)

    def child_removed(self, child):
        """ Called when a child is removed from this object.

        The default implementation of this method unparents the toolkit
        widget if the parent of the child is None. Subclasses which need
        more control may reimplement this method.

        Parameters
        ----------
        child : QtObject
            The child object removed from this object.

        """
        if child._parent is None:
            widget = child._widget
            if widget is not None:
                widget.setParent(None)

    def child_added(self, child):
        """ A method called when a child is added to this object.

        The default implementation ensures that the toolkit widget is
        properly parented. Subclasses which need more control may
        reimplement this method.

        Parameters
        ----------
        child : QtObject
            The child object added to this object.

        """
        widget = child._widget
        if widget is not None:
            widget.setParent(self._widget)

    def index_of(self, child):
        """ Return the index of the given child.

        Parameters
        ----------
        child : QtObject
            The child of interest.

        Returns
        -------
        result : int
            The index of the given child, or -1 if it is not found.

        """
        children = self._children
        if child in children:
            return children.index(child)
        return -1

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def send_action(self, action, content):
        """ Send an action to the server side object.

        The action will only be sent if the object is fully initialized.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        if self._initialized:
            self._session.send(self._object_id, action, content)

    def receive_action(self, action, content):
        """ Receive an action from the server side object.

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
        if self._initialized:
            dispatch_action(self, action, content)

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    @deferred_updates
    def on_action_children_changed(self, content):
        """ Handle the 'children_changed' action from the Enaml object.

        This method will unparent the removed children and add the new
        children to this object. If a given new child does not exist, it
        will be built. Subclasses that need more control may reimplement
        this method. The default implementation disables updates on the
        widget while adding children and reenables them on the next cyle
        of the event loop.

        """
        # Unparent the children being removed. Destroying a widget is
        # handled through a separate message.
        lookup = self._session.lookup
        for object_id in content['removed']:
            child = lookup(object_id)
            if child is not None and child._parent is self:
                child.set_parent(None)

        # Build or reparent the children being added.
        for tree in content['added']:
            object_id = tree['object_id']
            child = lookup(object_id)
            if child is not None:
                child.set_parent(self)
            else:
                child = self._session.build(tree, self)
                child.initialize()

        # Update the ordering of the children based on the order given
        # in the message. If the given order does not include all of
        # the current children, then the ones not included will be
        # appended to the end of the new list in an undefined order.
        ordered = []
        curr_set = set(self._children)
        for object_id in content['order']:
            child = lookup(object_id)
            if child is not None and child._parent is self:
                ordered.append(child)
                curr_set.discard(child)
        ordered.extend(curr_set)
        self._children = ordered

    def on_action_destroy(self, content):
        """ Handle the 'destroy' action from the Enaml object.

        This method will call the `destroy` method on the object.

        """
        if self._initialized:
            self.destroy()
        else:
            deferredCall(self.destroy)

