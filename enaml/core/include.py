#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import ContainerList, Bool

from .declarative import Declarative, d_
from .object import Object


class Include(Declarative):
    """ An object which dynamically inserts children into its parent.

    The 'Include' object is used to cleanly and easily insert objects
    into the children of its parent. 'Object' instances assigned to the
    'objects' list of the 'Include' will be parented with the parent of
    the 'Include'. Creating an 'Include' with no parent is a programming
    error.

    """
    #: The list of objects belonging to this Include. Objects in this
    #: list will be automatically parented with the Include's parent.
    objects = d_(ContainerList(Object))

    #: A boolean flag indicating whether to destroy the old objects that
    #: are removed from the parent. The default is True.
    destroy_old = d_(Bool(True))

    def initialize(self):
        """ A reimplemented initializer.

        This method will add the include objects to the parent of the
        include and ensure that they are initialized.

        """
        super(Include, self).initialize()
        self.parent.insert_children(self, self.objects)
        for obj in self.objects:
            obj.initialize()

    def destroy(self):
        """ A reimplemented destructor.

        The Include will destroy all of its objects if the 'destroy_old'
        flag is set and the parent is not also being destroyed.

        """
        destroy_items = self.destroy_old
        if destroy_items:
            parent = self.parent
            destroy_items = parent is None or not parent.is_destroyed
        super(Include, self).destroy()
        if destroy_items:
            for item in self.objects:
                if not item.is_destroyed:
                    item.destroy()
        del self.objects

    def _observe_objects(self, change):
        """ A change handler for the 'objects' list of the Include.

        If the object is initialized objects which are removed will be
        unparented and objects which are added will be reparented. Old
        objects will be destroyed if the 'destroy_old' flag is True.

        """
        # TODO clean this up
        if self.is_initialized:
            if change['type'] == 'update':
                oldvalue = change['oldvalue']
                newvalue = change['value']
                newset = set(newvalue)
                if self.destroy_old:
                    for obj in oldvalue:
                        if obj not in newset:
                            obj.destroy()
                else:
                    for obj in oldvalue:
                        if obj not in newset:
                            obj.set_parent(None)
                if newvalue:
                    self.parent.insert_children(self, newvalue)
            elif change['type'] == 'container':
                added = []
                removed = []
                op = change['operation']
                if op == '__delitem__':
                    item = change['item']
                    if isinstance(item, list):
                        removed.extend(item)
                    else:
                        removed.append(item)
                elif op == '__iadd__':
                    added.extend(change['items'])
                elif op == '__setitem__':
                    olditem = change['olditem']
                    newitem = change['newitem']
                    if isinstance(olditem, list):
                        removed.extend(olditem)
                    else:
                        removed.append(olditem)
                    if isinstance(newitem, list):
                        added.extend(newitem)
                    else:
                        added.append(newitem)
                elif op == 'append':
                    added.append(change['item'])
                elif op == 'extend':
                    added.extend(change['items'])
                elif op == 'insert':
                    added.append(change['item'])
                elif op == 'pop':
                    removed.append(change['item'])
                elif op == 'remove':
                    removed.append(change['item'])
                addset = set(added)
                if self.destroy_old:
                    for obj in removed:
                        if obj not in addset:
                            obj.destroy()
                else:
                    for obj in removed:
                        if obj not in addset:
                            obj.set_parent(None)
                self.parent.insert_children(self, change['value'])
