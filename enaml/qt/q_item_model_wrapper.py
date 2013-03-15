#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QAbstractTableModel, QSize

from .q_resource_helpers import get_cached_qcolor, get_cached_qfont, get_cached_qicon


#------------------------------------------------------------------------------
# Data Role Handlers
#------------------------------------------------------------------------------
def display_role_handler(model, row, column):
    return model.data(row, column)


def decoration_role_handler(model, row, column):
    icon = model.icon(row, column)
    if icon is not None:
        tk = icon._tkdata
        if tk is None:
            tk = get_cached_qicon(icon)
        return tk


def edit_role_handler(model, row, column):
    return model.edit_data(row, column)


def tool_tip_role_handler(model, row, column):
    return model.tool_tip(row, column)


def status_tip_role_handler(model, row, column):
    return model.status_tip(row, column)


def font_role_handler(model, row, column):
    font = model.font(row, column)
    if font is not None:
        tk = font._tkdata
        if tk is None:
            tk = get_cached_qfont(font)
        return tk


def text_alignment_role_handler(model, row, column):
    return Qt.Alignment(model.text_alignment(row, column))


def background_role_handler(model, row, column):
    color = model.background(row, column)
    if color is not None:
        tk = color._tkdata
        if tk is None:
            tk = get_cached_qcolor(color)
        return tk


def foreground_role_handler(model, row, column):
    color = model.foreground(row, column)
    if color is not None:
        tk = color._tkdata
        if tk is None:
            tk = get_cached_qcolor(color)
        return tk


def check_state_role_handler(model, row, column):
    state = model.check_state(row, column)
    if state is not None:
        return Qt.CheckState(state)


def size_hint_role_handler(model, row, column):
    size = model.size_hint(row, column)
    if size is not None:
        return QSize(*size)


ROLE_HANDLERS = {
    Qt.DisplayRole: display_role_handler,
    Qt.DecorationRole: decoration_role_handler,
    Qt.EditRole: edit_role_handler,
    Qt.ToolTipRole: tool_tip_role_handler,
    Qt.StatusTipRole: status_tip_role_handler,
    Qt.FontRole: font_role_handler,
    Qt.TextAlignmentRole: text_alignment_role_handler,
    Qt.BackgroundRole: background_role_handler,
    Qt.ForegroundRole: foreground_role_handler,
    Qt.CheckStateRole: check_state_role_handler,
    Qt.SizeHintRole: size_hint_role_handler,
}


#------------------------------------------------------------------------------
# Item model wrapper
#------------------------------------------------------------------------------
class QItemModelWrapper(QAbstractTableModel):

    def __init__(self, model):
        super(QItemModelWrapper, self).__init__()
        self._model = model
        model.data_changed.connect(self._on_data_changed)
        model.model_changed.connect(self._on_model_changed)

    def _on_data_changed(self, row, column):
        index = self.index(row, column)
        self.dataChanged.emit(index, index)

    def _on_model_changed(self):
        self.beginResetModel()
        self.endResetModel()

    #--------------------------------------------------------------------------
    # QAbstractTableModel API Implementation
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
        return Qt.ItemFlags(self._model.flags(index.row(), index.column()))

    def data(self, index, role):
        return ROLE_HANDLERS[role](self._model, index.row(), index.column())

    def setData(self, index, value, role):
        # row = index.row()
        # column = index.column()
        # if role == Qt.EditRole:
        #     return self._model.set_data(row, column, value)
        # if role == Qt.CheckStateRole:
        #     return self._model.set_check_state(row, column, value)
        return False
