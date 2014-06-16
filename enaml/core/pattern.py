#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List

from .declarative import Declarative


class Pattern(Declarative):
    """ A declarative object that represents a pattern object.

    The Pattern class serves as a base class for other classes such as
    Looper and Conditional, where the compiler nodes for the hierarchy
    are used to modify the standard behavior of creating children.

    Creating a Pattern without a parent is a programming error.

    """
    #: Single to the compiler that this class handles child creation.
    __intercepts_child_nodes__ = True

    #: Storage for the collected pattern nodes. This is used directly
    #: by subclasses and should not be manipulated by user code.
    pattern_nodes = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A reimplemented initialization method.

        """
        super(Pattern, self).initialize()
        self.refresh_items()
        # The pattern is responsible for initializing new items
        # during the initialization pass. At all other times, the
        # parent declarative object will initialize new children.
        for item in self.pattern_items():
            item.initialize()

    def destroy(self):
        """ A reimplemented destructor.

        The pattern will destroy all of the pattern items unless the
        parent object is in the process of being destroyed.

        """
        parent = self.parent
        destroy_items = parent is None or not parent.is_destroyed
        super(Pattern, self).destroy()
        if destroy_items:
            for item in self.pattern_items():
                if not item.is_destroyed:
                    item.destroy()
        del self.pattern_nodes

    def child_node_intercept(self, nodes, key, f_locals):
        """ Add a child subtree to this pattern.

        This method changes the default behavior of the runtime. It
        stores the child nodes and the locals mapping until the object
        is initialized, at which point the nodes will be called to
        create the pattern items.

        Parameters
        ----------
        nodes : list
            A list of compiler nodes containing the information required
            to instantiate the children.

        key : object
            The scope key for the current local scope.

        f_locals : mapping or None
            A mapping object for the current local scope.

        """
        self.pattern_nodes.append((nodes, key, f_locals))

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def pattern_items(self):
        """ Get a list of the items created by the pattern.

        This method must be implemented by subclasses to return a flat
        list of Declarative instances created by the subclass.

        Returns
        -------
        result : list
            A new list of Declarative objects owned by the pattern.

        """
        raise NotImplementedError

    def refresh_items(self):
        """ Refresh the items of the pattern.

        This method must be implemented by subclasses to refresh the
        items of the pattern.

        """
        raise NotImplementedError
