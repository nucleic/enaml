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

from .compiler_nodes import new_scope
from .declarative import d_
from .pattern import Pattern


class Looper(Pattern):
    """ A pattern object that repeats its children over an iterable.

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

    """
    #: The iterable to use when creating the items for the looper.
    #: The items in the iterable must be unique. This allows the
    #: Looper to optimize the creation and destruction of widgets.
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

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ A reimplemented destructor.

        The looper will release the owned items on destruction.

        """
        super(Looper, self).destroy()
        del self.iterable
        del self.items
        del self._iter_data

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    def _observe_iterable(self, change):
        """ A private observer for the `iterable` attribute.

        If the iterable changes while the looper is active, the loop
        items will be refreshed.

        """
        if change['type'] == 'update' and self.is_initialized:
            self.refresh_items()

    #--------------------------------------------------------------------------
    # Pattern API
    #--------------------------------------------------------------------------
    def pattern_items(self):
        """ Get a list of items created by the pattern.

        """
        return sum(self.items, [])

    def refresh_items(self):
        """ Refresh the items of the pattern.

        This method destroys the old items and creates and initializes
        the new items.

        """
        old_items = self.items[:]
        old_iter_data = self._iter_data
        iterable = self.iterable
        pattern_nodes = self.pattern_nodes
        new_iter_data = sortedmap()
        new_items = []

        if iterable is not None and len(pattern_nodes) > 0:
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
                for nodes, key, f_locals in pattern_nodes:
                    with new_scope(key, f_locals) as f_locals:
                        f_locals['loop_index'] = loop_index
                        f_locals['loop_item'] = loop_item
                        for node in nodes:
                            child = node(None)
                            if isinstance(child, list):
                                iteration.extend(child)
                            else:
                                iteration.append(child)

        for iteration in old_items:
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()

        if len(new_items) > 0:
            expanded = []
            recursive_expand(sum(new_items, []), expanded)
            self.parent.insert_children(self, expanded)

        self.items = new_items
        self._iter_data = new_iter_data


def recursive_expand(items, expanded):
    """ Recursively expand the list of items created by the looper.

    This allows the final list to be inserted into the parent and
    maintain the proper ordering of children.

    Parameters
    ----------
    items : list
        The list of items to expand. This should be composed of
        Pattern and other Object instances.

    expanded : list
        The output list. This list will be modified in-place.

    """
    for item in items:
        if isinstance(item, Pattern):
            recursive_expand(item.pattern_items(), expanded)
        expanded.append(item)
