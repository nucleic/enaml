#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QAbstractTableModel, QSize

from enaml.itemmodels.enums import Orientation

from .q_resource_helpers import get_cached_qcolor, get_cached_qfont, get_cached_qicon


#------------------------------------------------------------------------------
# Item Data Role Handlers
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


ITEM_DATA_ROLE_HANDLERS = {
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


def set_edit_role_handler(model, row, column, value):
    return model.set_data(row, column, value)


def set_check_state_role_handler(model, row, column, value):
    return model.set_check_state(row, column, value)


ITEM_DATA_SET_ROLE_HANDLERS = {
    Qt.EditRole: set_edit_role_handler,
    Qt.CheckStateRole: set_check_state_role_handler,
}


#------------------------------------------------------------------------------
# Header Data Role Handlers
#------------------------------------------------------------------------------
def header_display_role_handler(model, orientation, section):
    return model.header_data(orientation, section)


def header_decoration_role_handler(model, orientation, section):
    icon = model.header_icon(orientation, section)
    if icon is not None:
        tk = icon._tkdata
        if tk is None:
            tk = get_cached_qicon(icon)
        return tk


def header_tool_tip_role_handler(model, orientation, section):
    return model.header_tool_tip(orientation, section)


def header_status_tip_role_handler(model, orientation, section):
    return model.header_status_tip(orientation, section)




def header_text_alignment_role_handler(model, orientation, section):
    return Qt.Alignment(model.header_text_alignment(orientation, section))


def header_background_role_handler(model, orientation, section):
    color = model.header_background(orientation, section)
    if color is not None:
        tk = color._tkdata
        if tk is None:
            tk = get_cached_qcolor(color)
        return tk


def header_foreground_role_handler(model, orientation, section):
    color = model.header_foreground(orientation, section)
    if color is not None:
        tk = color._tkdata
        if tk is None:
            tk = get_cached_qcolor(color)
        return tk


def header_font_role_handler(model, orientation, section):
    font = model.header_font(orientation, section)
    if font is not None:
        tk = font._tkdata
        if tk is None:
            tk = get_cached_qfont(font)
        return tk


def header_size_hint_role_handler(model, orientation, section):
    size = model.header_size_hint(orientation, section)
    if size is not None:
        return QSize(*size)


HEADER_DATA_ROLE_HANDLERS = {
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
        handler = ITEM_DATA_ROLE_HANDLERS.get(role)
        if handler is not None:
            return handler(self._model, index.row(), index.column())

    def setData(self, index, value, role):
        handler = ITEM_DATA_SET_ROLE_HANDLERS.get(role)
        if handler is not None:
            return handler(self._model, index.row(), index.column(), value)
        return False
