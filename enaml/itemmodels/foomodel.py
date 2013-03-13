class ModelEditorItemModel(AbstractItemModel):

    _names = List()

    _model_editors = List()

    _item_editors = List()

    _row_count = Int()

    _col_count = Int()

    def add_editor(self, editor):
        assert isinstance(editor, ModelEditor)
        self._model_editors.append(editor)

    def layout(self):
        groups = []
        edit_ps = []
        groupmap = defaultdict(list)
        groupset = defaultdict(set)
        for editor in self._model_editors:
            #editor_p = set()
            #edit_ps.append(editor_p)
            for groupname, names in editor.provides().iteritems():
                if groupname not in groupset:
                    groups.append(groupname)
                s = groupset[groupname]
                filtered = [name for name in names if name not in s]
                s.update(names)
                #editor_p.update(names)
                groupmap[groupname].extend(filtered)
        names = self._names
        for groupname in groups:
            names.extend(groupmap[groupname])
        item_editors = self._item_editors
        #for editor, edit_p in zip(self._model_editors, edit_ps):
        for editor in self._model_editors:
            for name in names:
                item_editors.append(editor.item_editor(name))
        self._row_count = len(self._model_editors)
        self._col_count = len(self._names)

    #--------------------------------------------------------------------------
    # AbstractItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        return self._row_count

    def column_count(self):
        return self._col_count

    def data(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_data(m.model)

    def flags(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_flags(m.model)

    def icon(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_icon(m.model)

    def tool_tip(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_tool_tip(m.model)

    def status_tip(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_status_tip(m.model)

    def background(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_background(m.model)

    def foreground(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_foreground(m.model)

    def font(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_font(m.model)

    def text_alignment(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_text_alignment(m.model)

    def check_state(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_check_state(m.model)

    def size_hint(self, row, column):
        idx = row * self._col_count + column
        p = self._item_editors[idx]
        m = self._model_editors[row]
        if p is not None:
            return p.get_size_hint(m.model)
