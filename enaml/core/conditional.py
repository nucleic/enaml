#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, List

from .declarative import d_
from .pattern import Pattern


class Conditional(Pattern):
    """ A pattern object that represents conditional objects.

    When the `condition` attribute is True, the conditional will create
    its child items and insert them into its parent; when False, the old
    items will be destroyed.

    """
    #: The condition variable. If this is True, a copy of the children
    #: will be inserted into the parent. Otherwise, the old copies will
    #: be destroyed.
    condition = d_(Bool(True))

    #: The list of items created by the conditional. This list should
    #: not be manipulated directly by user code.
    items = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ A reimplemented destructor

        The conditional will releases the owned items on destruction.

        """
        super(Conditional, self).destroy()
        del self.items

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    def _observe_condition(self, change):
        """ A private observer for the `condition` attribute.

        If the condition changes while the conditional is active, the
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
        return self.items[:]

    def refresh_items(self):
        """ Refresh the items of the pattern.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        condition = self.condition
        pattern_nodes = self.pattern_nodes

        if condition and len(pattern_nodes) > 0:
            for node, f_locals in pattern_nodes:
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
