#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, List

from .declarative import d_, scope_lookup
from .templated import Templated


class Conditional(Templated):
    """ A templated object that represents conditional objects.

    When the `condition` attribute is True, the conditional will create
    its template items and insert them into its parent; when False, the
    old items will be destroyed.

    Creating a `Conditional` without a parent is a programming error.

    """
    #: The condition variable. If this is True, a copy of the children
    #: will be inserted into the parent. Otherwise, the old copies will
    #: be destroyed.
    condition = d_(Bool(True))

    #: The list of items created by the conditional. This should not be
    #: manipulated directly by user code.
    items = List()

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A reimplemented initialization method.

        """
        super(Conditional, self).initialize()
        self._refresh_conditional_items()

    def destroy(self):
        """ A reimplemented destructor

        The conditional will destroy all of its items, provided that
        the items and parent are not already destroyed.

        """
        super(Conditional, self).destroy()
        parent = self.parent
        if parent is not None and not parent.is_destroyed:
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

    def _refresh_conditional_items(self):
        """ A private method which refreshes the conditional items.

        This method destroys the old items and creates and initializes
        the new items.

        """
        items = []
        condition = self.condition
        templates = self._templates

        if condition and len(templates) > 0:
            # Each template is a 3-tuple of identifiers, globals, and
            # list of description dicts. There will only typically be
            # one template, but more can exist if the conditional was
            # subclassed via enamldef to provided default children.
            for identifiers, f_globals, descriptions in templates:
                # Each conditional gets a new scope derived from the
                # existing scope. This also allows the new children
                # to add their own independent identifiers. The items
                # are constructed with no parent since they are
                # parented via `insert_children` later on.
                scope = identifiers.copy()
                for descr in descriptions:
                    cls = scope_lookup(descr['type'], f_globals, descr)
                    instance = cls()
                    instance.populate(descr, scope, f_globals)
                    items.append(instance)

        old_items = self.items
        if len(old_items) > 0 or len(items) > 0:
            if len(old_items) > 0:
                for old in old_items:
                    if not old.is_destroyed:
                        old.destroy()
            if len(items) > 0:
                self.parent.insert_children(self, items)
                for item in items:
                    item.initialize()
        self.items = items
