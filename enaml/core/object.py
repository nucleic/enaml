#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque
import re

from atom.api import Atom, Unicode, Value, List, Event


def flag_generator():
    """ A generator which yields success bit flags.

    This should be used when creating flag values for a subclass of
    Object in order to not trample on superclass flags.

    """
    flag = 1
    while True:
        yield flag
        flag <<= 1
flag_generator = flag_generator()


#: A flag indicated that an object has been destroyed.
DESTROYED_FLAG = next(flag_generator)


def flag_property(flag):
    """ A factory function which creates a flag accessor property.

    """
    def getter(self):
        return (self._flags & flag) != 0
    def setter(self, value):
        if value:
            self._flags |= flag
        else:
            self._flags &= ~flag
    return property(getter, setter)


class Object(Atom):
    """ The most base class of the Enaml object hierarchy.

    An Enaml Object provides supports parent-children relationships and
    provides methods for navigating, searching, and destroying the tree.

    """
    #: An optional name to give to this object to assist in finding it
    #: in the tree (see . the 'find' method). There is no guarantee of
    #: uniqueness for an object `name`. It is left to the developer to
    #: choose an appropriate name.
    name = Unicode()

    #: The read-only property which returns the object parent. This will
    #: be an Object or None. Use 'set_parent()' or pass the parent to
    #: the constructor to set the parent of an object.
    parent = property(lambda self: self._parent)

    #: A read-only property which returns the object children. This is
    #: a list of Object instances. User code should not modify the list
    #: directly. Instead, use 'set_parent()' or 'insert_children()'.
    children = property(lambda self: self._children)

    #: A property which gets and sets the destroyed flag. This should
    #: not be manipulated directly by user code.
    is_destroyed = flag_property(DESTROYED_FLAG)

    #: An event fired when an object has been destroyed. It is triggered
    #: once during the object lifetime, just before the object is
    #: removed from the tree structure.
    destroyed = Event()

    #: Private storage values. These should *never* be manipulated by
    #: user code. For performance reasons, these are not type checked.
    _parent = Value()   # Object or None
    _children = List()  # list of Object
    _flags = Value(0)   # object flags

    def __init__(self, parent=None, **kwargs):
        """ Initialize an Object.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments to apply as attributes to the
            object.

        """
        super(Object, self).__init__(**kwargs)
        if parent is not None:
            self.set_parent(parent)

    def destroy(self):
        """ Destroy this object and all of its children recursively.

        This will emit the `destroyed` event before any change to the
        object tree is made. After this returns, the object should be
        considered invalid and should no longer be used.

        """
        self.is_destroyed = True
        self.destroyed()
        self.unobserve()
        for child in self._children:
            child.destroy()
        del self._children
        parent = self._parent
        if parent is not None:
            if parent.is_destroyed:
                self._parent = None
            else:
                self.set_parent(None)

    #--------------------------------------------------------------------------
    # Parenting API
    #--------------------------------------------------------------------------
    def set_parent(self, parent):
        """ Set the parent for this object.

        If the parent is not None, the child will be appended to the end
        of the parent's children. If the parent is already the parent of
        this object, then this method is a no-op. If this object already
        has a parent, then it will be properly reparented.

        Parameters
        ----------
        parent : Object or None
            The Object instance to use for the parent, or None if this
            object should be unparented.

        Notes
        -----
        It is the responsibility of the caller to initialize and activate
        the object as needed, if it is reparented dynamically at runtime.

        """
        old_parent = self._parent
        if parent is old_parent:
            return
        if parent is self:
            raise ValueError('cannot use `self` as Object parent')
        if parent is not None and not isinstance(parent, Object):
            raise TypeError('parent must be an Object or None')
        self._parent = parent
        self.parent_changed(old_parent, parent)
        if old_parent is not None:
            old_parent._children.remove(self)
            old_parent.child_removed(self)
        if parent is not None:
            parent._children.append(self)
            parent.child_added(self)

    def insert_children(self, before, insert):
        """ Insert children into this object at the given location.

        The children will be automatically parented and inserted into
        the object's children. If any children are already children of
        this object, then they will be moved appropriately.

        Parameters
        ----------
        before : Object, int or None
            A child object or int to use as the marker for inserting
            the new children. The new children will be inserted before
            this marker. If the Object is None or not a child, or if
            the int is not a valid index, then the new children will be
            added to the end of the children.

        insert : iterable
            An iterable of Object children to insert into this object.

        Notes
        -----
        It is the responsibility of the caller to initialize and activate
        the object as needed, if it is reparented dynamically at runtime.

        """
        insert_list = list(insert)
        insert_set = set(insert_list)
        if self in insert_set:
            raise ValueError('cannot use `self` as Object child')
        if len(insert_list) != len(insert_set):
            raise ValueError('cannot insert duplicate children')
        if not all(isinstance(child, Object) for child in insert_list):
            raise TypeError('children must be an Object instances')

        if isinstance(before, int):
            try:
                before = self._children[before]
            except IndexError:
                before = None

        new = []
        added = False
        for child in self._children:
            if child in insert_set:
                insert_set.remove(child)
                continue
            if child is before:
                new.extend(insert_list)
                added = True
            new.append(child)
        if not added:
            new.extend(insert_list)

        for child in insert_list:
            old_parent = child._parent
            if old_parent is not self:
                child._parent = self
                child.parent_changed(old_parent, self)
                if old_parent is not None:
                    old_parent.child_removed(child)

        self._children = new
        child_added = self.child_added
        child_moved = self.child_moved
        for child in insert_list:
            if child in insert_set:
                child_added(child)
            else:
                child_moved(child)

    def parent_changed(self, old, new):
        """ A method invoked when the parent of the object changes.

        This method is called when the parent on the object has changed,
        but before the children of the new parent have been updated.
        Sublasses may reimplement this method as required.

        Parameters
        ----------
        old : Object or None
            The old parent of the object.

        new : Object or None
            the new parent of the object.

        """
        pass

    def child_added(self, child):
        """ A method invoked when a child is added to the object.

        Sublasses may reimplement this method as required.

        Parameters
        ----------
        child : Object
            The child added to this object.

        """
        pass

    def child_moved(self, child):
        """ A method invoked when a child is moved in the object.

        Sublasses may reimplement this method as required.

        Parameters
        ----------
        child : Object
            The child moved in this object.

        """
        pass

    def child_removed(self, child):
        """ A method invoked when a child is removed from the object.

        Sublasses may reimplement this method as required.

        Parameters
        ----------
        child : Object
            The child removed from the object.

        """
        pass

    #--------------------------------------------------------------------------
    # Object Tree API
    #--------------------------------------------------------------------------
    def root_object(self):
        """ Get the root object for this hierarchy.

        Returns
        -------
        result : Object
            The top-most object in the hierarchy to which this object
            belongs.

        """
        obj = self
        while obj._parent is not None:
            obj = obj._parent
        return obj

    def traverse(self, depth_first=False):
        """ Yield all of the objects in the tree, from this object down.

        Parameters
        ----------
        depth_first : bool, optional
            If True, yield the nodes in depth first order. If False,
            yield the nodes in breadth first order. Defaults to False.

        """
        if depth_first:
            stack = [self]
            stack_pop = stack.pop
            stack_extend = stack.extend
        else:
            stack = deque([self])
            stack_pop = stack.popleft
            stack_extend = stack.extend
        while stack:
            obj = stack_pop()
            yield obj
            stack_extend(obj._children)

    def traverse_ancestors(self, root=None):
        """ Yield all of the objects in the tree, from this object up.

        Parameters
        ----------
        root : Object, optional
            The object at which to stop traversal. Defaults to None.

        """
        parent = self._parent
        while parent is not root and parent is not None:
            yield parent
            parent = parent._parent

    def find(self, name, regex=False):
        """ Find the first object in the subtree with the given name.

        This method will traverse the tree of objects, breadth first,
        from this object downward, looking for an object with the given
        name. The first object with the given name is returned, or None
        if no object is found with the given name.

        Parameters
        ----------
        name : string
            The name of the object for which to search.

        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of children instead of tested
            for equality. Defaults to False.

        Returns
        -------
        result : Object or None
            The first object found with the given name, or None if no
            object is found with the given name.

        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        for obj in self.traverse():
            if match(obj.name):
                return obj

    def find_all(self, name, regex=False):
        """ Find all objects in the subtree with the given name.

        This method will traverse the tree of objects, breadth first,
        from this object downward, looking for a objects with the given
        name. All of the objects with the given name are returned as a
        list.

        Parameters
        ----------
        name : string
            The name of the objects for which to search.

        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of objects instead of testing
            for equality. Defaults to False.

        Returns
        -------
        result : list of Object
            The list of objects found with the given name, or an empty
            list if no objects are found with the given name.

        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        res = []
        push = res.append
        for obj in self.traverse():
            if match(obj.name):
                push(obj)
        return res
