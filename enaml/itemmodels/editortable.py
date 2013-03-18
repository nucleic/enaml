#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import List, Int

from .abstractitemmodel import AbstractItemModel
from .editor import Editor


class EditorTable(AbstractItemModel):
    """ An AbstractItemModel implementation for editors.

    The EditorTable lays out a list of Editor instances in a 2D table.
    Editors should be added using the 'add_editor' method. Once all
    editors have been added to the model, the 'layout' method should be
    called so that the model can generate the internal layout.

    """
    #: The list of Editor instances given to the table model.
    _editors = List()

    #: The flattened list of editor names generated from the editors.
    _names = List()

    #: The flattened list of Item instances generated from the editors.
    #: These are stored in row-major order.
    _items = List()

    #: The row count of the model. This is updated during layout.
    _row_count = Int()

    #: The column count of the model. This is updated during layout.
    _column_count = Int()

    def add_editor(self, editor):
        """ Add a model editor to the table model.

        Parameters
        ----------
        editor : ModelEditor
            The model editor instance to add to the model.

        """
        assert isinstance(editor, Editor)
        self._editors.append(editor)

    def layout(self):
        """ Generate the internal layout for the table model.

        This method should be called after all editors have been added
        to the model.

        """
        # Make a first pass over the editors to collect the layout names.
        groupnames = []
        groupmap = defaultdict(lambda: (list(), set()))
        for editor in self._editors:
            for group in editor.groups:
                if group.name not in groupmap:
                    groupnames.append(group.name)
                gnames, snames = groupmap[group.name]
                for item in group.items:
                    if item.name not in snames:
                        snames.add(item.name)
                        gnames.append(item.name)

        # Collect the names into a flat list.
        names = self._names
        del names[:]
        for groupname in groupnames:
            names.extend(groupmap[groupname][0])

        # Make a second pass over the editors to collect the data.
        items = self._items
        del items[:]
        for editor in self._editors:
            editormap = {}
            for group in editor.groups:
                editoritems = editormap.setdefault(group.name, {})
                for item in group.items:
                    editoritems[item.name] = item
            for groupname in groupnames:
                if groupname in editormap:
                    egroup = editormap[groupname]
                    for iname in groupmap[groupname][0]:
                        items.append(egroup.get(iname))
                else:
                    items.extend([None] * len(groupmap[groupname][0]))

        self._row_count = len(self._editors)
        self._column_count = len(self._names)

    #--------------------------------------------------------------------------
    # AbstractItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        return self._row_count

    def column_count(self):
        return self._column_count

    def data(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_data(self._editors[row].model)

    def flags(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_flags(self._editors[row].model)
        return 0

    def icon(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_icon(self._editors[row].model)

    def tool_tip(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_tool_tip(self._editors[row].model)

    def status_tip(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_status_tip(self._editors[row].model)

    def background(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_background(self._editors[row].model)

    def foreground(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_foreground(self._editors[row].model)

    def font(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_font(self._editors[row].model)

    def text_alignment(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_text_alignment(self._editors[row].model)
        return 0

    def check_state(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_check_state(self._editors[row].model)

    def size_hint(self, row, column):
        item = self._items[row * self._column_count + column]
        if item is not None:
            return item.get_size_hint(self._editors[row].model)

    def set_data(self, row, column, value):
        item = self._items[row * self._column_count + column]
        if item is not None:
            if item.set_data(self._editors[row].model, value):
                self.data_changed.emit(row, column)
                return True
        return False

    def set_check_state(self, row, column, value):
        item = self._items[row * self._column_count + column]
        if item is not None:
            if item.set_check_state(self._editors[row].model, value):
                self.data_changed.emit(row, column)
                return True
        return False
