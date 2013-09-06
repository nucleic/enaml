#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Event, Typed, Unicode
from atom.datastructures.api import sortedmap

from .declarative_meta import DeclarativeMeta
from .expression_engine import ExpressionEngine
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
        The default is True.

    writable : bool, optional
        Whether the member is writable from Enaml syntax. The member
        must be writable to use the '=', '<<', and ':=' operators.
        The default is True.

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
    __metaclass__ = DeclarativeMeta

    #: Export the 'name' attribute as a declarative member.
    name = d_(Unicode())

    #: An event fired when an object is initialized. It is triggered
    #: once during the object lifetime, at the end of the initialize
    #: method.
    initialized = d_(Event(), writable=False)

    #: A property which gets and sets the initialized flag. This should
    #: not be manipulated directly by user code.
    is_initialized = flag_property(INITIALIZED_FLAG)

    #: Storage space for the declarative runtime. This value should not
    #: be manipulated by user code.
    _d_storage = Typed(sortedmap, ())

    #: Storage space for the declarative engine. This value should not
    #: be manipulated by user code.
    _d_engine = Typed(ExpressionEngine)

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
        self.is_initialized = False
        del self._d_storage
        del self._d_engine
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
