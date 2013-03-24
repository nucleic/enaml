#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import Iterable

from atom.api import Instance, List

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
    it creates. When the iterable for the looper is changed, the old
    items will be destroyed.

    Creating a `Looper` without a parent is a programming error.

    """
    #: The iterable to use when creating the items for the looper.
    iterable = d_(Instance(Iterable))

    #: The list of items created by the conditional. Each item in the
    #: list represents one iteration of the loop and is a list of the
    #: items generated during that iteration. This list should not be
    #: manipulated directly by user code.
    items = List()

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
        super(Looper, self).destroy()
        parent = self.parent
        if parent is not None and not parent.is_destroyed:
            for iteration in self.items:
                for item in iteration:
                    if not item.is_destroyed:
                        item.destroy()
        del self.iterable
        del self.items
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
        items = []
        iterable = self.iterable
        cdata = self._cdata

        if iterable and len(cdata) > 0:
            for loop_index, loop_item in enumerate(iterable):
                iteration = []
                for node, f_locals in cdata:
                    new_locals = f_locals.copy()
                    new_locals['loop_index'] = loop_index
                    new_locals['loop_item'] = loop_item
                    for child_node in node.child_defs:
                        child = child_node.typeclass()
                        child_node.populate(child, child_node, new_locals)
                        iteration.append(child)
                items.append(iteration)

        for iteration in self.items:
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()
        if len(items) > 0:
            self.parent.insert_children(self, sum(items, []))
        self.items = items
