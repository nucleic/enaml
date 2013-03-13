#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QAbstractTableModel, QSize

from .q_color_helpers import q_parse_color
from .q_font_helpers import QtFontCache
from .q_resource_helpers import get_cached_qicon


class QItemModelWrapper(QAbstractTableModel):

    role_handlers = {
        Qt.DisplayRole: '_item_display_role',
        Qt.DecorationRole: '_item_decoration_role',
        Qt.EditRole: '_item_edit_role',
        Qt.ToolTipRole: '_item_tool_tip_role',
        Qt.StatusTipRole: '_item_status_tip_role',
        Qt.FontRole: '_item_font_role',
        Qt.TextAlignmentRole: '_item_text_alignment_role',
        Qt.BackgroundRole: '_item_background_role',
        Qt.ForegroundRole: '_item_foreground_role',
        Qt.CheckStateRole: '_item_check_state_role',
        Qt.SizeHintRole: '_item_size_hint_role',
    }

    def __init__(self, model):
        super(QItemModelWrapper, self).__init__()
        self._model = model
        self._colors = {}
        self._fonts = QtFontCache()
        model.data_changed.connect(self._on_data_changed)
        model.model_changed.connect(self._on_model_changed)

    def _on_data_changed(self, row, column):
        index = self.index(row, column)
        self.dataChanged.emit(index, index)

    def _on_model_changed(self):
        self.beginResetModel()
        self.endResetModel()

    #--------------------------------------------------------------------------
    # Abstract API Implementation
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
        f = self._model.flags(index.row(), index.column())
        if f is not None:
            return Qt.ItemFlags(f)
        return Qt.ItemFlags(0)

    def data(self, index, role):
        handler = self.role_handlers[role]
        return getattr(self, handler)(index.row(), index.column())

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            return self._model.set_data(row, column, value)
        if role == Qt.CheckStateRole:
            return self._model.set_check_state(row, column, value)
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _item_display_role(self, row, column):
        return self._model.data(row, column)

    def _item_decoration_role(self, row, column):
        icon = self._model.icon(row, column)
        if icon is not None:
            return get_cached_qicon(icon)

    def _item_edit_role(self, row, column):
        return self._model.edit_data(row, column)

    def _item_tool_tip_role(self, row, column):
        return self._model.tool_tip(row, column)

    def _item_status_tip_role(self, row, column):
        return self._model.status_tip(row, column)

    def _item_font_role(self, row, column):
        font = self._model.font(row, column)
        if font:
            return self._fonts[font]

    def _item_text_alignment_role(self, row, column):
        a = self._model.text_alignment(row, column)
        if a is not None:
            return Qt.Alignment(a)

    def _item_background_role(self, row, column):
        color = self._model.background(row, column)
        if color:
            colors = self._colors
            if color in colors:
                qcolor = colors[color]
            else:
                qcolor = colors[color] = q_parse_color(color)
            return qcolor

    def _item_foreground_role(self, row, column):
        color = self._model.foreground(row, column)
        if color:
            colors = self._colors
            if color in colors:
                qcolor = colors[color]
            else:
                qcolor = colors[color] = q_parse_color(color)
            return qcolor

    def _item_check_state_role(self, row, column):
        state = self._model.check_state(row, column)
        if state is not None:
            return Qt.CheckState(state)

    def _item_size_hint_role(self, row, column):
        size = self._model.size_hint(row, column)
        if size is not None:
            return QSize(*size)
