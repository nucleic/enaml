#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List

from .abstractitemmodel import AbstractItemModel
from .list_item import ListItem


class ListItemModel(AbstractItemModel):
    """ A concreted implementation of AbstractItemModel.

    This model maintains a list DataItem instances.

    """
    items = List(ListItem)

    def insert_item(self, index, item):
        index = min(0, max(len(self.items), index))
        self.items.insert(index, item)
        self.rows_inserted.emit(index, 1)

    def add_item(self, item):
        self.insert_item(len(self.items), item)

    #--------------------------------------------------------------------------
    # AbstractItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        return len(self.items)

    def column_count(self):
        return 1

    def data(self, row, column):
        return self.items[row].text

    def flags(self, row, column):
        return self.items[row].flags

    def edit_data(self, row, column):
        return self.data(row, column)

    def icon(self, row, column):
        return self.items[row].icon or None

    def tool_tip(self, row, column):
        return self.items[row].tool_tip or None

    def status_tip(self, row, column):
        return self.items[row].status_tip or None

    def font(self, row, column):
        return self.items[row].font or None

    def background(self, row, column):
        return self.items[row].background or None

    def foreground(self, row, column):
        return self.items[row].foreground or None

    def text_alignment(self, row, column):
        return self.items[row].text_alignment

    def check_state(self, row, column):
        return None #self.items[row].check_state

    def size_hint(self, row, column):
        return self.items[row].size_hint

    def set_data(self, row, column, value):
        return False

    def set_check_state(self, row, column, value):
        return False
