#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QAbstractTableModel

from enaml.widgets.item import ItemModel

from .q_resource_helpers import (
    get_cached_qcolor, get_cached_qfont, get_cached_qicon
)


#------------------------------------------------------------------------------
# Role Handlers
#------------------------------------------------------------------------------
def _display_data(item):
    return item.get_data()


def _edit_data(item):
    return item.get_data()


def _check_state(item):
    return item.check_state


def _tool_tip(item):
    return item.tool_tip


def _status_tip(item):
    return item.status_tip


def _background(item):
    style = item.style
    if style is not None:
        color = style.background
        if color is not None:
            tk = color._tkdata
            if tk is None:
                tk = get_cached_qcolor(color)
            return tk


def _foreground(item):
    style = item.style
    if style is not None:
        color = style.foreground
        if color is not None:
            tk = color._tkdata
            if tk is None:
                tk = get_cached_qcolor(color)
            return tk


def _font(item):
    style = item.style
    if style is not None:
        font = style.font
        if font is not None:
            tk = font._tkdata
            if tk is None:
                tk = get_cached_qfont(font)
            return tk


def _decoration(item):
    style = item.style
    if style is not None:
        icon = style.icon
        if icon is not None:
            tk = icon._tkdata
            if tk is None:
                tk = get_cached_qicon(icon)
            return tk


def _text_alignment(item):
    style = item.style
    if style is not None:
        return style.text_alignment


ROLE_HANDLERS = {
    Qt.DisplayRole: _display_data,
    Qt.EditRole: _edit_data,
    Qt.CheckStateRole: _check_state,
    Qt.ToolTipRole: _tool_tip,
    Qt.StatusTipRole: _status_tip,
    Qt.BackgroundRole: _background,
    Qt.ForegroundRole: _foreground,
    Qt.FontRole: _font,
    Qt.DecorationRole: _decoration,
    Qt.TextAlignmentRole: _text_alignment,
}


#------------------------------------------------------------------------------
# Item Model Wrapper
#------------------------------------------------------------------------------
class QItemModelWrapper(QAbstractTableModel):
    """ A concrete QAbstractTableModel which wraps an ItemModel.

    """
    def __init__(self, model=None):
        """ Initialize a QItemModelWrapper.

        Parameters
        ----------
        model : ItemModel, optional
            The ItemModel instance to be wrapped by this model.

        """
        super(QItemModelWrapper, self).__init__()
        self._model = ItemModel()
        if model is not None:
            self.setItemModel(model)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setItemModel(self, model):
        """ Set the ItemModel to wrap with this model.

        Parameters
        ----------
        model : ItemModel or None
            The ItemModel instance to wrap, or None.

        """
        assert isinstance(model, ItemModel)
        self.beginResetModel()
        old = self._model
        old.model_reset.disconnect(self._on_model_reset)
        old.data_changed.disconnect(self._on_data_changed)
        self._model = model or ItemModel()
        model.model_reset.connect(self._on_model_reset)
        model.data_changed.connect(self._on_data_changed)
        self.endResetModel()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_model_reset(self):
        """ A signal handler for the 'model_reset' signal on the model.

        """
        self.beginResetModel()
        self.endResetModel()

    def _on_data_changed(self, start, end):
        """ A signal handler for the 'data_changed' signal on the model.

        """
        start_index = self.index(*start)
        end_index = self.index(*end)
        self.dataChanged.emit(start_index, end_index)

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
        if orientation == Qt.Horizontal:
            item = self._model.column_header_item(section)
        else:
            item = self._model.row_header_item(section)
        if item is not None:
            handler = ROLE_HANDLERS.get(role)
            if handler is not None:
                return handler(item)

    def data(self, index, role):
        item = self._model.item(index.row(), index.column())
        if item is not None:
            handler = ROLE_HANDLERS.get(role)
            if handler is not None:
                return handler(item)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            item = self._model.item(index.row(), index.column())
            if item is not None:
                if item.set_data(value):
                    self.dataChanged.emit(index, index)
                    return True
        return False
