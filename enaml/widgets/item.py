#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom,  Enum, Int, Typed, Signal, Unicode, Value, observe

from enaml.colors import ColorMember
from enaml.core.declarative import Declarative, d_
from enaml.fonts import FontMember
from enaml.icon import Icon


class ItemFlag(object):
    """ The available item flags for an item in an item model.

    These values can be OR'd together to create the composite flags for
    a particular item in the model.

    These enum values are equivalent to the Qt::ItemFlag enum values.

    """
    Selectable = 0x1

    Editable = 0x2

    # TODO: DragEnabled = 0x4

    # TODO: DropEnabled = 0x8

    Checkable = 0x10

    Enabled = 0x20

    # TODO: Tristate = 0x40


class CheckState(object):
    """ The available values for the check state of a model item.

    These enum values are equivalent to the Qt::CheckState enum values.

    """
    Unchecked = 0

    # TODO: PartiallyChecked = 1

    Checked = 2


class TextAlignment(object):
    """ The available alignment flags for item text in an item model.

    These values can be OR'd together to create the final alignment for
    a particular item in the model.

    These enum values are equivalent to the Qt::AlignmentFlag values.

    """
    Left = 0x1

    Right = 0x2

    HCenter = 0x4

    Justify = 0x8

    Top = 0x20

    Bottom = 0x40

    VCenter = 0x80

    Center = HCenter | VCenter

    HorizontalMask = Left | Right | HCenter | Justify

    VerticalMask = Top | Bottom | VCenter


class Style(Atom):
    """ A class for defining styles for items in an item model.

    """
    #: The background color of the item. The default value is None.
    background = ColorMember()

    #: The foreground color of the item. The default value is None.
    foreground = ColorMember()

    #: The font of the item. The default value is None.
    font = FontMember()

    #: The icon to display for the item. The default value is None.
    icon = Typed(Icon)

    #: The text alignment for the item. The default value is centered.
    text_alignment = Int(TextAlignment.Center)

    def clone(self, **overrides):
        """ Create a clone of this style with optional new values.

        Parameters
        ----------
        **overrides
            Optional new values for any of the attributes on the style.
            These values will be used for the clone, in lieu of the
            current values on the style.

        """
        dct = {}
        dct['flags'] = self.flags
        dct['background'] = self.background
        dct['foreground'] = self.foreground
        dct['font'] = self.font
        dct['icon'] = self.icon
        dct['text_alignment'] = self.text_alignment
        dct.update(overrides)
        return Style(**overrides)

    def align_left(self):
        """ Set the horizontal text alignment to left align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.VerticalMask) | TextAlignment.Left
        self.text_alignment = align
        return self

    def align_right(self):
        """ Set the horizontal text alignment to right align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.VerticalMask) | TextAlignment.Right
        self.text_alignment = align
        return self

    def align_h_center(self):
        """ Set the horizontal text alignment to center align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.VerticalMask) | TextAlignment.HCenter
        self.text_alignment = align
        return self

    def align_justify(self):
        """ Set the horizontal text alignment to justify align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.VerticalMask) | TextAlignment.Justify
        self.text_alignment = align
        return self

    def align_top(self):
        """ Set the vertical text alignment to top align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.HorizontalMask) | TextAlignment.Top
        self.text_alignment = align
        return self

    def align_bottom(self):
        """ Set the vertical text alignment to bottom align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.HorizontalMask) | TextAlignment.Bottom
        self.text_alignment = align
        return self

    def align_v_center(self):
        """ Set the vertical text alignment to center align.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        align = self.text_alignment
        align = (align & TextAlignment.HorizontalMask) | TextAlignment.VCenter
        self.text_alignment = align
        return self

    def align_center(self):
        """ Set the vertical and horizontal text alignment to center.

        Returns
        -------
        result : self
            The self reference to allow method chaining.

        """
        self.text_alignment = TextAlignment.Center
        return self


class Item(Declarative):
    """ An object representing an item in an item model.

    An Item encapsulates a data value and the styling information for
    rendering that value to the screen.

    """
    #: The data value for the item. The default value is None.
    data = d_(Value())

    #: The check state for the item. The default value is None.
    check_state = d_(Enum(None, CheckState.Unchecked, CheckState.Checked))

    #: The flags for the item. The default is selectable and enabled.
    item_flags = d_(Int(ItemFlag.Selectable | ItemFlag.Enabled))

    #: The style to use for the item. The default value is None.
    style = d_(Typed(Style))

    #: The unicode tool tip for the item.
    tool_tip = d_(Unicode())

    #: The unicode status tip for the item.
    status_tip = d_(Unicode())

    #: An index which can be used by the framework to locate the item
    #: in a model. This value should not be manipulated by user code.
    index = Value()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def get_data(self):
        """ Get the data value for the item.

        Returns
        -------
        result : object
            The data value for the item. The default implementation
            returns the 'data' attribute.

        """
        return self.data

    def set_data(self, value):
        """ Set the data value for the item.

        Parameters
        ----------
        value : object
            The value input by the user.

        Returns
        -------
        result : bool
            Whether or not the value was successfully updated. The
            default implementation sets the 'data' attribute and
            returns True.

        """
        self.data = value
        return True

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    # tool_tip and status_tip are pulled on as-needed; no need to observe.
    @observe(('data', 'check_state', 'item_flags', 'style'))
    def _item_changed(self, change):
        """ A private observer for item state change.

        If the item has a parent with an 'item_changed' method, it will
        be invoked when the item changes, passing itself as the first
        argument to the handler.

        """
        if change['type'] == 'update':
            handler = getattr(self.parent, 'item_changed', None)
            if handler is not None:
                handler(self)


class ItemModel(Atom):
    """ A base class for defining item models.

    This class should be subclassed and implemented as needed to define
    data models based on Item instances.

    """
    #: A signal emitted when the model is reset in its entirety. This
    #: signal has no payload.
    model_reset = Signal()

    #: A signal emitted when data in the model has changed. The payload
    #: is the starting and ending index of the changed cell span. Each
    #: index is represented as a (row, column) tuple of ints.
    data_changed = Signal()

    def row_count(self):
        """ Get the row count for the item model.

        Returns
        -------
        result : int
            The number of rows in the model. The default returns 0.

        """
        return 0

    def column_count(self):
        """ Get the column count for the item model.

        Returns
        -------
        result : int
            The number of columns in the model. The default returns 0.

        """
        return 0

    def row_header_item(self, row):
        """ Get the item for the given row header index.

        Parameters
        ----------
        row : int
            The row index for the requested header.

        Returns
        -------
        result : Item or None
            An Item object for the requested header, or None if one
            cannot be provided. The default returns None.

        """
        return None

    def column_header_item(self, column):
        """ Get the item for the given column header index.

        Parameters
        ----------
        column : int
            The column index for the requested header.

        Returns
        -------
        result : Item or None
            An Item object for the requested header, or None if one
            cannot be provided. The default returns None.

        """
        return None

    def item(self, row, column):
        """ Get the item for the given cell coordinates.

        Parameters
        ----------
        row : int
            The row index for the requested cell.

        column : int
            The column index for the requested cell.

        Returns
        -------
        result : Item or None
            An Item object for the requested cell, or None if one
            cannot be provided. THe default returns None.

        """
        return None
