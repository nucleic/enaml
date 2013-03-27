#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, List

from .declarative import Declarative, d_


def populate_conditional(conditional, node, f_locals):
    """ The populate function for the Conditional class.

    """
    if node.scope_member:
        node.scope_member.set_slot(conditional, f_locals)
    if node.identifier:
        f_locals[node.identifier] = conditional
    conditional._cdata.append((node, f_locals))


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
    _cdata = List()

    @classmethod
    def populator_func(cls):
        """ Get the populator function for the Conditional class.

        This returns a populator function which intercepts the creation
        of the child items and defers it until the initialization pass.

        """
        return populate_conditional

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

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _observe_condition(self, change):
        """ A private observer for the `condition` attribute.

        If the condition changes while the conditional is active, the
        items will be refreshed.

        """
        if self.is_initialized:
            self._refresh_items()

    def _refresh_items(self):
        """ A private method which refreshes the conditional items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        condition = self.condition
        cdata = self._cdata

        if condition and len(cdata) > 0:
            for node, f_locals in cdata:
                new_locals = f_locals.copy()
                for child_node in node.child_defs:
                    child = child_node.typeclass()
                    child_node.populate(child, child_node, new_locals)
                    items.append(child)

        for old in self.items:
            if not old.is_destroyed:
                old.destroy()
        if len(items) > 0:
            self.parent.insert_children(self, items)
        self.items = items
