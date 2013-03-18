#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, Event, null

from .object import Object, flag_generator, flag_property


def d_(member, readable=True, writable=True, final=True):
    """ Mark an Atom member as bindable from Enaml syntax.

    Parameters
    ----------
    member : Member
        The atom member to mark as bindable from Enaml syntax.

    readable : bool, optional
        Whether the member is readable from Enaml syntax. The member
        must be readable to use the '>>', ':=', and '::' operators.

    writable : bool, optional
        Whether the member is writable from Enaml syntax. The member
        must be writable to use the '=', '<<', and ':=' operators.

    final : bool, optional
        Whether or not the member can be redefined from Enaml syntax
        using the 'attr' keyword. The default is True and indicates
        that the member cannot be overridden.

    """
    metadata = member.metadata
    if metadata is None:
        metadata = member.metadata = {}
    metadata['d_member'] = True
    metadata['d_readable'] = readable
    metadata['d_writable'] = writable
    metadata['d_final'] = final
    return member


#: The flag indicating that the Declarative object has been initialized.
INITIALIZED_FLAG = flag_generator.next()


class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    #: Export the 'name' attribute as a declarative member.
    name = d_(Str())

    #: A property which gets and sets the initialized flag. This should
    #: not be manipulated directly by user code.
    is_initialized = flag_property(INITIALIZED_FLAG)

    #: An event fired when an object is initialized. It is triggered
    #: once during the object lifetime, at the end of the initialize
    #: method.
    initialized = d_(Event(), writable=False)

    def initialize(self):
        """ Initialize this object all of its children recursively.

        This is called to give the objects in the tree the opportunity
        to initialize additional state which depends upon the object
        tree being fully built. It is the responsibility of external
        code to call this method at the appropriate time. This will
        emit the `initialized` signal after all of the children have
        been initialized.

        """
        # Iterate over a copy since the children add and remove
        # other children during initialization.
        for child in self.children[:]:
            if isinstance(child, Declarative):
                child.initialize()
        self.is_initialized = True
        self.initialized()

    def destroy(self):
        """ An overridden destructor method for declarative cleanup.

        """
        members = self.members()
        for d, f_globals in self.__descriptions__:
            scopename = d['scopename']
            if scopename in members:
                delattr(self, scopename)
        for op in type(self).__eval_operators__.itervalues():
            op.release(self)
        for oplist in type(self).__notify_operators__.itervalues():
            for op in oplist:
                op.release(self)
        super(Declarative, self).destroy()

    def child_added(self, child):
        """ An overridden child added event handler.

        This handler will automatically initialize a declarative child
        if this object itself has already been initialized.

        """
        super(Declarative, self).child_added(child)
        if isinstance(child, Declarative):
            if self.is_initialized and not child.is_initialized:
                child.initialize()

    #--------------------------------------------------------------------------
    # Private Framework API
    #--------------------------------------------------------------------------
    #: Class level storage for declarative description dictionaries.
    #: This is populated by the compiler when the class is created.
    #: It should not be modified by user code.
    __descriptions__ = ()

    #: Class level storage for eval operators. This dict is populated
    #: by the Enaml compiler when the operators are invoked at class
    # creation time. It should not be modified by user code.
    __eval_operators__ = {}

    #: Class level storage for notify operators. This dict is populated
    #: by the Enaml compiler when the operators are invoked at class
    # creation time. It should not be modified by user code.
    __notify_operators__ = {}

    @classmethod
    def _eval_operators(cls):
        """ Get the eval operators for this class.

        This classmethod will ensure the dict returned is owned by
        the class. The returned value should not be modified by user
        code.

        """
        if '__eval_operators__' in cls.__dict__:
            return cls.__eval_operators__
        exprs = cls.__eval_operators__ = cls.__eval_operators__.copy()
        return exprs

    @classmethod
    def _notify_operators(cls):
        """ Get the notify operators for this class.

        This classmethod will ensure the dict returned is owned by
        the class. The returned value should not be modified by user
        code.

        """
        if '__notify_operators__' in cls.__dict__:
            return cls.__notify_operators__
        ops = {}
        for key, oplist in cls.__notify_operators__.iteritems():
            ops[key] = oplist[:]
        cls.__notify_operators__ = ops
        return ops

    def _run_eval_operator(self, name):
        """ Run the eval operator attached to the given name.

        This method is used as a default value handler by the Enaml
        operators when an eval operator is bound to the object.

        Parameters
        ----------
        name : str
            The name to which the operator of interest is bound.

        Returns
        -------
        result : object or null
            The result of the evaluated operator, or null if there
            is no eval operator bound for the given name.

        """
        op = type(self).__eval_operators__.get(name)
        if op is not None:
            return op.eval(self)
        return null

    def _run_notify_operator(self, change):
        """ Invoke a bound notify operator for the given change.

        This method is used as a static observer by the Enaml
        operators when a notify operator is bound to the object.

        Parameters
        ----------
        change : dict
            The change dictionary for the notification.

        """
        oplist = type(self).__notify_operators__.get(change['name'])
        if oplist is not None:
            for op in oplist:
                op.notify(change)

    def _populate(self, description, f_locals, f_globals):
        """ Populate this declarative instance from a description.

        This is called by the EnamlDef metaclass when an enamldef block
        is instantiated. For classes which are enamldef subclasses, this
        method is invoked *before* the __init__ method of that class. A
        subclass may reimplement this method to gain custom control over
        how the children for its instances are created.

        Parameters
        ----------
        description : dict
            The description dictionary for the instance.

        f_locals : dict
            The dictionary of local scope identifiers for the current
            enamldef block being populated.

        f_globals : dict
            The dictionary of globals for the scope in which the object
            was declared.

        """
        scopename = description['scopename']
        if scopename and description['bindings']:
            setattr(self, scopename, f_locals)
        ident = description['identifier']
        if ident:
            f_locals[ident] = self
        for child in description['children']:
            # Create the child without a parent so that all of the
            # children of the new object are added before this
            # object gets the child_added event.
            instance = child['class']()
            instance._populate(child, f_locals, f_globals)
            instance.set_parent(self)
