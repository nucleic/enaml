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


def populate_looper(looper, node, f_locals):
    """ The populate function for the Looper class.

    """
    if node.scope_member:
        node.scope_member.set_slot(looper, f_locals)
    if node.identifier:
        f_locals[node.identifier] = looper
    looper._cdata.append((node, f_locals))


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
    _idata = Typed(sortedmap, ())

    #: Private data storage for the looper.
    _cdata = List()

    @classmethod
    def populator_func(cls):
        """ Get the populator function for the Looper class.

        This returns a populator function which intercepts the creation
        of the child items and defers it until the initialization pass.

        """
        return populate_looper

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
        parent = self.parent
        if destroy_items:
            for iteration in self.items:
                for item in iteration:
                    if not item.is_destroyed:
                        item.destroy()
        del self.iterable
        del self.items
        del self._idata
        del self._cdata

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _observe_iterable(self, change):
        """ A private observer for the `iterable` attribute.

        If the iterable changes while the looper is active, the loop
        items will be refreshed.

        """
        if self.is_initialized:
            self._refresh_items()

    def _refresh_items(self):
        """ A private method which refreshes the loop items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        old_items = self.items[:]
        old_idata = self._idata
        iterable = self.iterable
        cdata = self._cdata
        new_idata = sortedmap()
        new_items = []

        if iterable and len(cdata) > 0:
            for loop_index, loop_item in enumerate(iterable):
                iteration = old_idata.get(loop_item)
                if iteration is not None:
                    new_idata[loop_item] = iteration
                    new_items.append(iteration)
                    old_items.remove(iteration)
                    continue
                iteration = []
                new_idata[loop_item] = iteration
                new_items.append(iteration)
                for node, f_locals in cdata:
                    new_locals = f_locals.copy()
                    new_locals['loop_index'] = loop_index
                    new_locals['loop_item'] = loop_item
                    for child_node in node.child_defs:
                        child = child_node.typeclass()
                        child_node.populate(child, child_node, new_locals)
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
        self._idata = new_idata


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
