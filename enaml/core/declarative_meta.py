#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import AtomMeta


class DeclarativeMeta(AtomMeta):
    """ The metaclass for declarative classes.

    """
    #: Class level storage for the construct nodes. This is populated by
    #: the compiler when the enamldef class is created. It should not be
    #: modified by user code.
    __constructs__ = ()

    #: Class level storage for eval operators. This dict is populated
    #: by the Enaml compiler when the operators are invoked at class
    # creation time. It should not be modified by user code.
    __eval_operators__ = {}

    #: Class level storage for notify operators. This dict is populated
    #: by the Enaml compiler when the operators are invoked at class
    # creation time. It should not be modified by user code.
    __notify_operators__ = {}

    def populator_func(cls):
        """ Get the populator function for the class.

        Subclasses may declare a class method to override this and
        supply their own custom populate routine for instances.

        """
        return default_populator

    def eval_operators(cls):
        """ Get the eval operators for the class.

        This classmethod will ensure the dict returned is owned by
        the class. The returned value should not be modified by user
        code.

        """
        if '__eval_operators__' in cls.__dict__:
            return cls.__eval_operators__
        exprs = cls.__eval_operators__ = cls.__eval_operators__.copy()
        return exprs

    def notify_operators(cls):
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


def default_populator(item, node, f_locals):
    """ The default populate function for Declarative classes.

    """
    # The children of the item are created without a parent so that the
    # entire subtree is built before the item gets a child_added event.
    if node.scope_member:
        node.scope_member.set_slot(item, f_locals)
    if node.identifier:
        f_locals[node.identifier] = item
    for child_node in node.child_defs:
        child = child_node.typeclass()
        child_node.populate(child, child_node, f_locals)
        child.set_parent(item)
