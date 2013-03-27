#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from PyQt4.QtCore import Qt, QTimer, QAbstractTableModel
from PyQt4.QtGui import QTableView

from enaml.modelview.editor_view import ProxyEditorView

from .q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qicon
)
from .qt_control import QtControl


class ChangeSet(object):

    def __init__(self):
        self._min_row = 0
        self._max_row = 0
        self._min_col = 0
        self._max_col = 0

    def reset(self):
        self.__init__()

    def update(self, row, col):
        self._min_row = min(row, self._min_row)
        self._min_col = min(col, self._min_col)
        self._max_row = max(row, self._max_row)
        self._max_col = max(row, self._max_col)

    def emit(self, model):
        first = model.index(self._min_row, self._min_col)
        last = model.index(self._max_row, self._max_col)
        model.dataChanged.emit(first, last)


class QEditorModel(QAbstractTableModel):

    def __init__(self):
        super(QEditorModel, self).__init__()
        self._names = []
        self._items = []
        self._editors = []
        self._row_count = 0
        self._column_count = 0
        self._change_set = ChangeSet()
        self._change_timer = QTimer()
        self._change_timer.setSingleShot(True)
        self._change_timer.timeout.connect(self._on_change_timer)

    #--------------------------------------------------------------------------
    # Editor Interface
    #--------------------------------------------------------------------------
    def editor_changed(self, item):
        index = item._tk_index
        if index is None or self._items[index] is not item:
            try:
                index = self._items.index(item)
            except ValueError:
                return
            item._tk_index = index
        row, column = divmod(index, self._column_count)
        self._change_set.update(row, column)
        self._change_timer.start()

    def _on_change_timer(self):
        change_set = self._change_set
        change_set.emit(self)
        change_set.reset()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addEditor(self, editor):
        self._editors.append(editor)
        editor._tk_model = self

    def doLayout(self):
        self.beginResetModel()
        # Make a first pass over the editors to collect the layout names.
        groupnames = []
        groupmap = defaultdict(lambda: (list(), set()))
        for editor in self._editors:
            for group in editor.groups():
                if group.name not in groupmap:
                    groupnames.append(group.name)
                gnames, snames = groupmap[group.name]
                for item in group.items():
                    if item.name not in snames:
                        snames.add(item.name)
                        gnames.append(item.name)

        # Collect the names into a flat list.
        names = self._names = []
        for groupname in groupnames:
            names.extend(groupmap[groupname][0])

        # Make a second pass over the editors to collect the data.
        items = self._items = []
        for editor in self._editors:
            editormap = {}
            for group in editor.groups():
                editoritems = editormap.setdefault(group.name, {})
                for item in group.items():
                    editoritems[item.name] = item
            for groupname in groupnames:
                if groupname in editormap:
                    egroup = editormap[groupname]
                    for iname in groupmap[groupname][0]:
                        item = egroup.get(iname)
                        item._tk_index = len(items)
                        items.append(item)
                else:
                    items.extend([None] * len(groupmap[groupname][0]))

        self._row_count = len(self._editors)
        self._column_count = len(self._names)
        self.endResetModel()

    #--------------------------------------------------------------------------
    # QAbstractTableModel Interface
    #--------------------------------------------------------------------------
    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self._row_count

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return self._column_count

    def flags(self, index):
        item = self._items[index.row() * self._column_count + index.column()]
        if item is not None:
            style = item.style
            if style is not None:
                return Qt.ItemFlags(style.flags)
        return Qt.ItemFlags(0)

    def data(self, index, role):
        item = self._items[index.row() * self._column_count + index.column()]
        if item is not None:
            if role == Qt.DisplayRole:
                return item.data
            if role == Qt.CheckStateRole:
                return item.check_state
            if role == Qt.BackgroundRole:
                style = item.style
                if style is not None:
                    color = style.background
                    if color is not None:
                        tk = color._tkdata
                        if tk is None:
                            tk = get_cached_qcolor(color)
                        return tk
                return None
            if role == Qt.ForegroundRole:
                style = item.style
                if style is not None:
                    color = style.foreground
                    if color is not None:
                        tk = color._tkdata
                        if tk is None:
                            tk = get_cached_qcolor(color)
                        return tk
                return None
            if role == Qt.FontRole:
                style = item.style
                if style is not None:
                    font = style.font
                    if font is not None:
                        tk = font._tkdata
                        if tk is None:
                            tk = get_cached_qfont(font)
                        return tk
                return None
            if role == Qt.DecorationRole:
                style = item.style
                if style is not None:
                    icon = style.icon
                    if icon is not None:
                        tk = icon._tkdata
                        if tk is None:
                            tk = get_cached_qicon(icon)
                        return tk
                return None
            if role == Qt.TextAlignmentRole:
                style = item.style
                if style is not None:
                    return style.text_alignment
            if role == Qt.ToolTipRole:
                return item.tool_tip()
            if role == Qt.StatusTipRole:
                return item.status_tip()
            if role == Qt.EditRole:
                return item.data


class QtEditorView(QtControl, ProxyEditorView):

    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
        self.widget.setModel(QEditorModel())
        self.widget.setAttribute(Qt.WA_StaticContents, True)

    def init_widget(self):
        super(QtEditorView, self).init_widget()
        d = self.declaration
        qmodel = self.widget.model()
        models = d.models
        factory = d.editor_factory
        for model in models:
            qmodel.addEditor(factory(model))

    def init_layout(self):
        super(QtEditorView, self).init_widget()
        self.widget.model().doLayout()

