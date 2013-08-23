#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import AtomMeta
from atom.datastructures.api import sortedmap


class EnamlDefMeta(AtomMeta):
    """ The metaclass which creates types for the 'enamldef' keyword.

    """
    #: Class level storage for the construct node. This is populated by
    #: the compiler when the enamldef class is created. It should not be
    #: modified by user code.
    __node__ = None

    def iternodes(cls):
        """ Get a generator which yields the construct nodes.

        The nodes are yielded in the order in which they should be
        consumed for the purpose of populating the child subtree. It
        includes the superclass nodes followed by the current node.

        Returns
        -------
        result : generator
            A generator which yields the enamldef construct nodes.

        """
        node = cls.__node__  # this should never be None
        for super_node in node.super_nodes:
            yield super_node
        yield node

    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ Create a new instance of the enamldef class.

        This method will create the new instance, then populate that
        instance with children defined in the enamldef. Once those
        children are added, the __init__ method of the instance will
        be invoked with the provided arguments.

        Parameters
        ----------
        parent : Object or None
            The parent object of the new instance.

        **kwargs
            Additional keyword arguments to pass to the constructor.

        """
        self = cls.__new__(cls)

        # Each node represents a subtree which exists in a separate
        # conceptual scope and therefore has its own locals mapping.
        # A node with None for a scope key does not require locals
        # and the storage overhead for that node can be avoided. The
        # instance is repsonsible for building out its subtree. The
        # indirection allows objects like Looper and Conditional to
        # intercept the build process and delay the creation of the
        # subtree to a later point.
        for node in cls.iternodes():
            f_locals = None
            if node.has_block_identifiers:
                f_locals = sortedmap()
            self.add_subtree(node, f_locals)

        self.__init__(parent, **kwargs)
        return self
