#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List

from .pattern import Pattern


class Inline(Pattern):
    """ A pattern object that represents inline objects.

    An 'Inline' component will embed it's children inline with its
    parent.

    """
    #: The list of items created by the inline. This list should not
    #: be manipulated directly by user code.
    items = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ A reimplemented destructor.

        The inline will release the owned items on destruction.

        """
        super(Inline, self).destroy()
        del self.items

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
        for node, f_locals in self.pattern_nodes:
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
