#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Str, List

from .baseitem import BaseItem


class Group(Atom):
    """ A class which groups together a collection of items.

    An Group is used to collect related items into a logical collection.
    The various implementations of rich item models use these groups to
    generate their internal item layouts.

    """
    #: The name of the group. The semantic meaning of the name is left
    #: to the particular item model instance which consumes the group.
    name = Str()

    #: The list of items for the group. When possible, Item instances
    #: should be shared in an application. The various item models will
    #: keep strong references to the items, so to reduce memory usage
    #: when dealing with a large number of model instances, only create
    #: the minimum necessary items and share them. The list of items
    #: will not be copied on assignment, so the list can also be shared.
    items = List(BaseItem, copy=False)

    def __init__(self, name, **kwargs):
        """ Initialize an Group.

        Parameters
        ----------
        name : str
            The name of the group.

        **kwargs
            Additional keyword arguments to pass to the superclass
            constructor.

        """
        super(Group, self).__init__(name=name, **kwargs)
