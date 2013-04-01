#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QTimer, QAbstractTableModel
from PyQt4.QtGui import QTableView

from enaml.widgets.item import ItemModel
from enaml.widgets.model_editor import ProxyEditorView

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
        self._model = ItemModel()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setItemModel(self, model):
        self.beginResetModel()
        self._model = model
        self.endResetModel()

    #--------------------------------------------------------------------------
    # QAbstractTableModel Interface
    #--------------------------------------------------------------------------
    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.row_count()

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.column_count()

    def flags(self, index):
        item = self._model.item(index.row(), index.column())
        if item is not None:
            return Qt.ItemFlags(item.item_flags)
        return Qt.ItemFlags(0)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                item = self._model.column_header_item(section)
                if item is not None:
                    return item.value
            return section

    def data(self, index, role):
        item = self._model.item(index.row(), index.column())
        if item is not None:
            if role == Qt.DisplayRole:
                return item.value
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
                return item.tool_tip
            if role == Qt.StatusTipRole:
                return item.status_tip
            if role == Qt.EditRole:
                return item.value


class QtEditorView(QtControl, ProxyEditorView):

    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
        self.widget.setModel(QEditorModel())
        self.widget.setAttribute(Qt.WA_StaticContents, True)

    def init_widget(self):
        super(QtEditorView, self).init_widget()
        self.widget.model().setItemModel(self.declaration.item_model)

    #--------------------------------------------------------------------------
    # ProxyEditorView API
    #--------------------------------------------------------------------------
    def set_item_model(self, model):
        pass
