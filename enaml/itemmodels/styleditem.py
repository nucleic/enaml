#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.colors import ColorMember
from enaml.fonts import FontMember

from .item import Item


class StyledItem(Item):
    """ An Item subclass which provides storage for styling.

    A StyledItem allows the developer to specify the background color,
    foreground color, and font as attributes of an Item. This provides
    a convenient alternative to subclassing Item when the given style
    applies to model items equally.

    """
    #: The background color of the item. The default value is None.
    background = ColorMember()

    #: The foreground color of the item. The default value is None.
    foreground = ColorMember()

    #: The font of the item. The default value is None.
    font = FontMember()

    def get_background(self, model):
        """ Get the background color for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : Color
            The background color for the model item, or None if the
            item has no background color. The default method returns
            the value of the 'background' attribute.

        """
        return self.background

    def get_foreground(self, model):
        """ Get the foreground color for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : Color
            The foreground color for the model item, or None if the
            item has no foreground color. The default method returns
            the value of the foreground attribute.

        """
        return self.foreground

    def get_font(self, model):
        """ Get the font for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : Font
            The font for the model item, or None if the item has no
            font. The default method returns the value of the font
            attribute.

        """
        return self.font
