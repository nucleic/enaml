#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Int, Typed

from enaml.colors import ColorMember
from enaml.fonts import FontMember
from enaml.icon import Icon


class TextAlignment(object):
    """ The available alignment flags for item text in align data model.

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
    """ A class for defining styles for items in a data model.

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
