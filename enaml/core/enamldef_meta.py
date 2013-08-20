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

    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ A custom instance creation routine for EnamlDef classes.

        """
        self = cls.__new__(cls)
        nodes = []
        for klass in cls.mro():
            node = getattr(klass, '__node__', None)
            if node is None:
                break
            nodes.append(node)
        for node in reversed(nodes):
            f_locals = sortedmap()
            self._storage[node.scope_key] = f_locals
            if node.identifier:
                f_locals[node.identifier] = self
            for child_node in node.children:
                self.build_subtree(child_node, f_locals)
        self.__init__(parent, **kwargs)
        return self
