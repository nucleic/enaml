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
def item_display_data(item):
    """ Retrieve the display data for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the display data.

    Returns
    -------
    result : object
        The display data value for the item.

    """
    return item.get_data()


def item_edit_data(item):
    """ Retrieve the edit data for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the edit data.

    Returns
    -------
    result : object
        The edit data value for the item.

    """
    return item.get_data()


def item_check_state(item):
    """ Retrieve the check state for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the check state.

    Returns
    -------
    result : CheckState
        The integer check state for the item.

    """
    return item.check_state


def item_tool_tip(item):
    """ Retrieve the tool tip for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the tool tip.

    Returns
    -------
    result : unicode
        The tool tip for the item.

    """
    return item.tool_tip


def item_status_tip(item):
    """ Retrieve the status tip for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the status tip.

    Returns
    -------
    result : unicode
        The status tip for the item.

    """
    return item.status_tip


def item_background(item):
    """ Retrieve the background color for the item.

    The color is cached on the item the first time it is retrieved.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the background color.

    Returns
    -------
    result : QColor or None
        The background color for the item, or None.

    """
    style = item.style
    if style is not None:
        color = style.background
        if color is not None:
            tk = color._tkdata
            if tk is None:
                tk = get_cached_qcolor(color)
            return tk


def item_foreground(item):
    """ Retrieve the foreground color for the item.

    The color is cached on the item the first time it is retrieved.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the foreground color.

    Returns
    -------
    result : QColor or None
        The foreground color for the item, or None.

    """
    style = item.style
    if style is not None:
        color = style.foreground
        if color is not None:
            tk = color._tkdata
            if tk is None:
                tk = get_cached_qcolor(color)
            return tk


def item_font(item):
    """ Retrieve the font for the item.

    The font is cached on the item the first time it is retrieved.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the font.

    Returns
    -------
    result : QFont or None
        The font for the item, or None.

    """
    style = item.style
    if style is not None:
        font = style.font
        if font is not None:
            tk = font._tkdata
            if tk is None:
                tk = get_cached_qfont(font)
            return tk


def item_decoration(item):
    """ Retrieve the decoration for the item.

    The icon is cached on the item the first time it is retrieved.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the decoration.

    Returns
    -------
    result : QIcon or None
        The decoration for the item, or None.

    """
    style = item.style
    if style is not None:
        icon = style.icon
        if icon is not None:
            tk = icon._tkdata
            if tk is None:
                tk = get_cached_qicon(icon)
            return tk


def item_text_alignment(item):
    """ Retrieve the text alignment for an Item.

    Parameters
    ----------
    item : Item
        The Enaml Item for which to retrieve the text alignment.

    Returns
    -------
    result : TextAlignment
        The integer text alignment for the item.

    """
    style = item.style
    if style is not None:
        return style.text_alignment


#: A mapping of data roles to item role handler functions.
ROLE_HANDLERS = {
    Qt.DisplayRole: item_display_data,
    Qt.EditRole: item_edit_data,
    Qt.CheckStateRole: item_check_state,
    Qt.ToolTipRole: item_tool_tip,
    Qt.StatusTipRole: item_status_tip,
    Qt.BackgroundRole: item_background,
    Qt.ForegroundRole: item_foreground,
    Qt.FontRole: item_font,
    Qt.DecorationRole: item_decoration,
    Qt.TextAlignmentRole: item_text_alignment,
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
