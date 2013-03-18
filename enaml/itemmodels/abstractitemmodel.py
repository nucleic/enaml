#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Signal

from .enums import AlignmentFlag, ItemFlag


class AbstractItemModel(Atom):
    """ An abstract base class for creating item based models.

    """
    #: A signal which should be emitted when an item changes. The
    #: payload is the row and column index of the item that changed.
    data_changed = Signal()

    #: A signal which should be emitted when the entire model changes
    #: structure. Sometimes, this can be simpler and more efficient
    #: than the other notification signals. This signal has no payload.
    model_changed = Signal()

    #: A signal which should be emitted when rows are inserted. The
    #: payload should be the index of the insert and the number of
    #: rows inserted.
    rows_inserted = Signal()

    #: A signal which should be emitted when rows are removed. The
    #: payload should be the index of the removal and the number of
    #: rows removed.
    rows_removed = Signal()

    #: A signal which should be emitted when columns are inserted. The
    #: payload should be the index of the insert and the number of
    #: columns inserted.
    columns_inserted = Signal()

    #: A signal which should be emitted when columns are removed. The
    #: payload should be the index of the removal and the number of
    #: columns removed.
    columns_removed = Signal()

    #: A signal which should be emitted when a header changes. The
    #: payload is the orientation of the header the indices of the
    #: first and last changed sections, respectively.
    header_data_changed = Signal()

    def row_count(self):
        """ Get the number of rows in the model.

        Returns
        -------
        result : int
            The number of rows in the model.

        """
        raise NotImplementedError

    def column_count(self):
        """ Get the number of columns in the model.

        Returns
        -------
        result : int
            The number of columns in the model.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Item Data Methods
    #--------------------------------------------------------------------------
    def data(self, row, column):
        """ Get the item data for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : object or None
            The data value for the given indices, or None if no data is
            available.

        """
        raise NotImplementedError

    def flags(self, row, column):
        """ Get the item flags for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : int
            An or'd combination of ItemFlag enum values for the given
            indices. The default is enabled and centered.

        """
        return ItemFlag.ItemIsEnabled | ItemFlag.ItemIsSelectable

    def edit_data(self, row, column):
        """ Get the item edit data for the given indices.

        This is the data that will be displayed when an editor is
        opened for the given cell.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : object or None
            The edit data value for the given indices, or None if no
            edit data is available. The default delegates to 'data()'.

        """
        return self.data(row, column)

    def icon(self, row, column):
        """ Get the icon for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : Icon or None
            The icon for the item or None. The default is None.

        """
        return None

    def tool_tip(self, row, column):
        """ Get the tool tip for the given item indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : unicode or None
            The tool tip for the item, or None if no tool tip is
            available. The default is None.

        """
        return None

    def status_tip(self, row, column):
        """ Get the status tip for the given item indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : unicode or None
            The status tip for the item, or None if no status tip is
            available. The default is None.

        """
        return None

    def background(self, row, column):
        """ Get the background color for the given item indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : Color or None
            The background color of the item as an Enaml Color object,
            or None if the item has no background color. The default is
            None.

        """
        return None

    def foreground(self, row, column):
        """ Get the foreground color for the given item indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : Color or None
            The foreground color of the item as an Enaml Color object,
            or None if the item has no foreground color. The default is
            None.

        """
        return None

    def font(self, row, column):
        """ Get the font for the given item indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : Font or None
            The font of the item as an Enaml Font object, or None if
            the item has no font. The default is None.

        """
        return None

    def text_alignment(self, row, column):
        """ Get the text alignment for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : int
            An or'd combination of AlignmentFlag enum values for the
            given indices. The default is centered.

        """
        return AlignmentFlag.AlignCenter

    def check_state(self, row, column):
        """ Get the check state for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : int or None
            One of the CheckState enum values, or None if the item has
            no check state. The default is None.

        """
        return None

    def size_hint(self, row, column):
        """ Get the size hint for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : tuple or None
            The (width, height) size hint for the item, or None if the
            item has no size hint. The default is None.

        """
        # TODO make this a Size object?
        return None

    def set_data(self, row, column, value):
        """ Set the item data for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        value : object
            The value entered by the user.

        Returns
        -------
        result : bool
            True if the item was set successfully, False otherwise.
            The default is False.

        """
        return False

    def set_check_state(self, row, column, value):
        """ Set the check state for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        value : CheckState
            One of the CheckState enum values.

        Returns
        -------
        result : bool
            True if the item state set successfully, False otherwise.
            The default is False.

        """
        return False

    #--------------------------------------------------------------------------
    # Header Data Methods
    #--------------------------------------------------------------------------
    def header_data(self, orientation, section):
        """ Get the header data for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : object or None
            The data value for the given header section, or None if no
            data is available. The default is the section index.

        """
        return section

    def header_icon(self, orientation, section):
        """ Get the header icon for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : Icon or None
            The icon for the header section or None. The default is
            None.

        """
        return None

    def header_tool_tip(self, orientation, section):
        """ Get the header tool tip for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : unicode or None
            The unicode tool tip for the header section or None. The
            default is None.

        """
        return None

    def header_status_tip(self, orientation, section):
        """ Get the header status tip for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : unicode or None
            The unicode status tip for the header section or None. The
            default is None.

        """
        return None

    def header_background(self, orientation, section):
        """ Get the header background for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : Color or None
            The background color for the header section or None. The
            default is None.

        """
        return None

    def header_foreground(self, orientation, section):
        """ Get the header foreground for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : Color or None
            The foreground color for the header section or None. The
            default is None.

        """
        return None

    def header_font(self, orientation, section):
        """ Get the header font for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : Font or None
            The font for the header section or None. The default is
            None.

        """
        return None

    def header_text_alignment(self, orientation, section):
        """ Get the header text alignment for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : int
            An or'd combination of AlignmentFlag enum values for the
            given indices. The default is centered.

        """
        return AlignmentFlag.AlignCenter

    def header_size_hint(self, orientation, section):
        """ Get the header text alignment for the given section.

        Parameters
        ----------
        orientation : Orientation
            The orienation value for the given header.

        section : int
            The relevant section index of the header.

        Returns
        -------
        result : tuple or None
            The (width, height) size hint for the header section, or
            None if the item has no size hint. The default is None.

        """
        # TODO make this a Size object?
        return None
