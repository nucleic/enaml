#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Value

from enaml.core.declarative import Declarative

from .item import Item


class Group(Declarative):

    def items(self):
        for child in self.children:
            if isinstance(child, Item):
                yield child

    def item_changed(self, item):
        handler = getattr(self.parent, 'item_changed', None)
        if handler is not None:
            handler(item)


class Editor(Declarative):

    _tk_model = Value()

    def groups(self):
        for child in self.children:
            if isinstance(child, Group):
                yield child

    def item_changed(self, item):
        tk_model = self._tk_model
        if tk_model is not None:
            tk_model.editor_changed(item)
