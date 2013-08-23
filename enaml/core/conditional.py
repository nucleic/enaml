#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, List

from .declarative import Declarative, d_


class Conditional(Declarative):
    """ A declarative object that represents conditional objects.

    When the `condition` attribute is True, the conditional will create
    its child items and insert them into its parent; when False, the old
    items will be destroyed.

    Creating a `Conditional` without a parent is a programming error.

    """
    #: The condition variable. If this is True, a copy of the children
    #: will be inserted into the parent. Otherwise, the old copies will
    #: be destroyed.
    condition = d_(Bool(True))

    #: The list of items created by the conditional. This list should
    #: not be manipulated directly by user code.
    items = List()

    #: Private data storage for the conditional.
    _node_data = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A reimplemented initialization method.

        """
        super(Conditional, self).initialize()
        self._refresh_items()
        # The conditional is responsible for initializing new items
        # during the initialization pass. At all other times, the
        # parent declarative object will initialize new children.
        for item in self.items:
            item.initialize()

    def destroy(self):
        """ A reimplemented destructor

        The conditional will destroy all of its items, provided that
        the items and parent are not already destroyed.

        """
        parent = self.parent
        destroy_items = parent is not None and not parent.is_destroyed
        super(Conditional, self).destroy()
        if destroy_items:
            for item in self.items:
                if not item.is_destroyed:
                    item.destroy()
        del self.items
        del self._node_data

    def add_subtree(self, node, f_locals):
        """ Add a node subtree to this conditional.

        This method changes the default behavior provided by the parent
        class. It stores the node object and the locals mapping until
        the object is initialized, at which point it creates the subtree
        if the conditional expression evaluates to True.

        Parameters
        ----------
        node : ConstructNode
            A construct node containing the information required to
            instantiate the children.

        f_locals : mapping or None
            A mapping object for the current local scope or None if
            the block does not require a local scope.

        """
        if f_locals is not None:
            if node.identifier:
                f_locals[node.identifier] = self
            self._d_storage[node.scope_key] = f_locals
        self._node_data.append((node, f_locals))

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _observe_condition(self, change):
        """ A private observer for the `condition` attribute.

        If the condition changes while the conditional is active, the
        items will be refreshed.

        """
        if change['type'] == 'update' and self.is_initialized:
            self._refresh_items()

    def _refresh_items(self):
        """ A private method which refreshes the conditional items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        condition = self.condition
        node_data = self._node_data

        if condition and len(node_data) > 0:
            for node, f_locals in node_data:
                if f_locals is not None:
                    f_locals = f_locals.copy()
                for child_node in node.children:
                    child = child_node.klass()
                    child.add_subtree(child_node, f_locals)
                    items.append(child)

        for old in self.items:
            if not old.is_destroyed:
                old.destroy()

        if len(items) > 0:
            self.parent.insert_children(self, items)

        self.items = items
