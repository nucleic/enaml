#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, Typed, Bool

from .declarative import Declarative, d_
from .object import Object


class Include(Declarative):
    """ An object which dynamically inserts children into its parent.

    The `Include` object is used to cleanly and easily insert objects
    into the children of its parent. `Object` instances assigned to the
    `objects` list of the `Include` will be parented with the parent of
    the `Include`. The parent of an `Include` should be an instance of
    `Messenger`; if this condition does not hold, the behavior will be
    undefined.

    """
    #: The list of objects belonging to this Include. Objects in this
    #: list will be automatically parented with the Include's parent.
    objects = d_(List(Typed(Object)))

    #: A boolean flag indicating whether to destroy the old objects that
    #: are removed from the parent. The default is True.
    destroy_old = d_(Bool(True))

    def pre_initialize(self):
        """ A pre-initialization handler.

        This method will add the include objects to the parent of the
        include and ensure that they are initialized.

        """
        super(Include, self).pre_initialize()
        self.parent.insert_children(self, self.objects)
        for obj in self.objects:
            obj.initialize()

    def parent_event(self, event):
        """ Handle a `ParentEvent` for the Include.

        If the object state is `active` the current include objects will
        be reparented to the new parent.

        """
        if self.is_active:
            old = event.old
            new = event.new
            with new.children_event_context():
                with old.children_event_context():
                    if new is None:
                        for obj in self.objects:
                            obj.set_parent(None)
                    else:
                        new.insert_children(self, self.objects)

    def _objects_changed(self, old, new):
        """ A change handler for the `objects` list of the Include.

        If the object state is 'active' objects which are removed will
        be unparented and objects which are added will be reparented.
        Old objects will be destroyed if the `destroy_old` flag is set
        to True.

        """
        if self.is_active:
            parent = self.parent
            if parent is not None:
                with parent.children_event_context():
                    new_set = set(new)
                    if self.destroy_old:
                        for obj in old:
                            if obj not in new_set:
                                obj.destroy()
                    else:
                        for obj in old:
                            if obj not in new_set:
                                obj.set_parent(None)
                    if new_set:
                        parent.insert_children(self, self.objects)

    def _objects_items_changed(self, event):
        """ Handle the `objects` list changing in-place.

        If the object state is 'active' objects which are removed will
        be unparented and objects which are added will be reparented.
        Old objects will be destroyed if the `destroy_old` flag is set
        to True.

        """
        if self.is_active:
            parent = self.parent
            if parent is not None:
                with parent.children_event_context():
                    add_set = set(event.added)
                    if self.destroy_old:
                        for obj in event.removed:
                            if obj not in add_set:
                                obj.destroy()
                    else:
                        for obj in event.removed:
                            if obj not in add_set:
                                obj.set_parent(None)
                    if add_set:
                        parent.insert_children(self, self.objects)

