#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import Iterable

from atom.api import Instance, List, Typed
from atom.datastructures.api import sortedmap

from .conditional import Conditional
from .declarative import Declarative, d_


class Looper(Declarative):
    """ A declarative object that repeats its children over an iterable.

    The children of a `Looper` are used as a template when creating new
    objects for each item in the given `iterable`. Each iteration of the
    loop will be given an indenpendent scope which is the union of the
    outer scope and any identifiers created during the iteration. This
    scope will also contain `loop_index` and `loop_item` variables which
    are the index and value of the iterable, respectively.

    All items created by the looper will be added as children of the
    parent of the `Looper`. The `Looper` keeps ownership of all items
    it creates. When the iterable for the looper is changed, the looper
    will only create and destroy children for the items in the iterable
    which have changed.

    Creating a `Looper` without a parent is a programming error.

    """
    #: The iterable to use when creating the items for the looper.
    iterable = d_(Instance(Iterable))

    #: The list of items created by the conditional. Each item in the
    #: list represents one iteration of the loop and is a list of the
    #: items generated during that iteration. This list should not be
    #: manipulated directly by user code.
    items = List()

    #: Private data storage which maps the user iterable data to the
    #: list of items created for that iteration. This allows the looper
    #: to only create and destroy the items which have changed.
    _iter_data = Typed(sortedmap, ())

    #: Private data storage for the node data for the looper.
    _node_data = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A reimplemented initialization method.

        This method will create and initialize the loop items using the
        looper templates to generate the items.

        """
        super(Looper, self).initialize()
        self._refresh_items()
        # The looper is responsible for initializing new items during
        # the initialization pass. At all other times, the parent
        # declarative object will initialize new children.
        for iteration in self.items:
            for item in iteration:
                item.initialize()

    def destroy(self):
        """ A reimplemented destructor

        The looper will destroy all of its items, provided that the
        items are not already destroyed and the parent is not in the
        process of being destroyed.

        """
        parent = self.parent
        destroy_items = parent is not None and not parent.is_destroyed
        super(Looper, self).destroy()
        if destroy_items:
            for iteration in self.items:
                for item in iteration:
                    if not item.is_destroyed:
                        item.destroy()
        del self.iterable
        del self.items
        del self._iter_data
        del self._node_data

    def add_subtree(self, node, f_locals):
        """ Add a node subtree to this looper.

        This method changes the default behavior provided by the parent
        class. It stores the node object and the locals mapping until
        the object is initialized, at which point it creates the subtree
        by repeating the node items according to the provided iterable.

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
    def _observe_iterable(self, change):
        """ A private observer for the `iterable` attribute.

        If the iterable changes while the looper is active, the loop
        items will be refreshed.

        """
        if change['type'] == 'update' and self.is_initialized:
            self._refresh_items()

    def _refresh_items(self):
        """ A private method which refreshes the loop items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        old_items = self.items[:]
        old_iter_data = self._iter_data
        iterable = self.iterable
        node_data = self._node_data
        new_iter_data = sortedmap()
        new_items = []

        if iterable and len(node_data) > 0:
            for loop_index, loop_item in enumerate(iterable):
                iteration = old_iter_data.get(loop_item)
                if iteration is not None:
                    new_iter_data[loop_item] = iteration
                    new_items.append(iteration)
                    old_items.remove(iteration)
                    continue
                iteration = []
                new_iter_data[loop_item] = iteration
                new_items.append(iteration)
                for node, f_locals in node_data:
                    if f_locals is not None:
                        f_locals = f_locals.copy()
                    else:
                        f_locals = sortedmap()
                    f_locals['loop_index'] = loop_index
                    f_locals['loop_item'] = loop_item
                    for child_node in node.children:
                        child = child_node.klass()
                        child.add_subtree(child_node, f_locals)
                        iteration.append(child)

        for iteration in old_items:
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()

        if len(new_items) > 0:
            expanded = []
            _recursive_expand(sum(new_items, []), expanded)
            self.parent.insert_children(self, expanded)

        self.items = new_items
        self._iter_data = new_iter_data


def _recursive_expand(items, expanded):
    """ Recursively expand the list of items created by the looper.

    This allows the final list to be inserted into the parent and
    maintain the proper ordering of children.

    Parameters
    ----------
    items : list
        The list of items to expand. This should be composed of
        Looper, Conditional, and other Object instances.

    expanded : list
        The output list. This list will be modified in-place.

    """
    for item in items:
        if isinstance(item, Conditional):
            _recursive_expand(item.items[:], expanded)
        elif isinstance(item, Looper):
            _recursive_expand(sum(item.items, []), expanded)
        expanded.append(item)
