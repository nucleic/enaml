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
from .modeleditor import ModelEditor


class EditorTableModel(AbstractItemModel):
    """ An AbstractItemModel implementation for model editors.

    The EditorTableModel lays out a list of ModelEditor instances in
    a 2D table. Editors should be added using the 'add_editor' method.
    Once all editors have been added to the model, the 'layout' method
    should be called so that the model can generate the internal layout.

    """
    #: The list of ModelEditor instances given to the table model.
    _model_editors = List()

    #: The flattened list of editor names generated from the models.
    _names = List()

    #: The flattened list of ItemEditor instances generated from the
    #: model editors. These are stored in row-major order.
    _item_editors = List()

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
        assert isinstance(editor, ModelEditor)
        self._model_editors.append(editor)

    def layout(self):
        """ Generate the internal layout for the table model.

        This method should be called after all editors have been added
        to the model.

        """
        # Make a first pass over the editors to collect the layout names.
        groups = []
        groupmap = defaultdict(lambda: (list(), set()))
        for editor in self._model_editors:
            for edit_group in editor.edit_groups:
                if edit_group.name not in groupmap:
                    groups.append(edit_group.name)
                gnames, snames = groupmap[edit_group.name]
                for item in edit_group.item_editors:
                    if item.name not in gnames:
                        snames.add(item.name)
                        gnames.append(item.name)

        # Collect the names into a flat list.
        names = self._names
        for groupname in groups:
            names.extend(groupmap[groupname][0])

        # Make a second pass over the editors to collect the data.
        item_editors = self._item_editors
        for editor in self._model_editors:
            editormap = {}
            for edit_group in editor.edit_groups:
                editoritems = editormap.setdefault(edit_group.name, {})
                for item in edit_group.item_editors:
                    editoritems[item.name] = item
            for groupname in groups:
                if groupname in editormap:
                    egroup = editormap[groupname]
                    for iname in groupmap[groupname][0]:
                        item_editors.append(egroup.get(iname))
                else:
                    item_editors.extend([None] * len(groupmap[groupname][0]))

        self._row_count = len(self._model_editors)
        self._column_count = len(self._names)

    #--------------------------------------------------------------------------
    # AbstractItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        return self._row_count

    def column_count(self):
        return self._column_count

    def data(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_data(m.model)

    def flags(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_flags(m.model)
        return 0

    def icon(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_icon(m.model)

    def tool_tip(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_tool_tip(m.model)

    def status_tip(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_status_tip(m.model)

    def background(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_background(m.model)

    def foreground(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_foreground(m.model)

    def font(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_font(m.model)

    def text_alignment(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_text_alignment(m.model)
        return 0

    def check_state(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_check_state(m.model)

    def size_hint(self, row, column):
        idx = row * self._column_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_size_hint(m.model)
