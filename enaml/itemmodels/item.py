#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Callable, Int, Str, null

from enaml.colors import ColorMember
from enaml.fonts import FontMember

from .baseitem import BaseItem, DefaultItemFlags, DefaultTextAlignment


class Item(BaseItem):
    """ A BaseItem subclass which provides convenient storage.

    The standard Item class provides storage for commonly used item data
    which does not typically depend on a particular model instance. This
    allows developers to easily supply the data without needing to write
    a BaseItem subclass.

    An Item will retrieve the data from a model instance by looking up
    the 'name' attribute on the item. The data on the model is updated
    in a similar fashion.

    """
    #: The string name of the item. By default, the name is used to
    #: access the named attribute on the model as the item data.
    name = Str()

    #: The flags for the item. The default is selectable and enabled.
    flags = Int(DefaultItemFlags)

    #: The background color of the item. The default value is None.
    background = ColorMember()

    #: The foreground color of the item. The default value is None.
    foreground = ColorMember()

    #: The font of the item. The default value is None.
    font = FontMember()

    #: The text alignment for the item. The default value is centered.
    text_alignment = Int(DefaultTextAlignment)

    #: Storage for a callable to convert the user input value into a
    #: value appropriate for assigning to the data attribute. The
    converter = Callable()

    def __init__(self, name, **kwargs):
        """ Initialize an Item.

        Parameters
        ----------
        name : str
            The name of the item.

        **kwargs
            Additional keyword arguments to pass to the superclass
            constructor.

        """
        super(Item, self).__init__(name=name, **kwargs)

    def get_data(self, model):
        """ Get the data for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : object
            The data to show in the UI for the particular model item.
            The default method accesses the 'name' attribute on the
            model.

        """
        return getattr(model, self.name)

    def get_flags(self, model):
        """ Get the flags for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : ItemFlag
            An or'd combination of ItemFlag enum values. The default
            method returns the value of the 'flags' attribute.

        """
        return self.flags

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
            the value of the 'foreground' attribute.

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
            font. The default method returns the value of the 'font'
            attribute.

        """
        return self.font

    def get_text_alignment(self, model):
        """ Get the text alignment flags for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : AlignmentFlag
            An or'd combination of AlignmentFlag enum values. The
            default method returns the value of the 'text_alignment'
            attribute.

        """
        return self.text_alignment

    def set_data(self, model, value):
        """ Set the data for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        value : object
            The value to set for the model item.

        Returns
        -------
        result : bool
            True if the model item was successfully updated, False
            otherwise. The default method attempt to conver the value
            using any supplied converter and then assigns it to the
            attribute.

        """
        converter = self.converter
        if converter is not null:
            value = converter(value)
        setattr(model, self.name, value)
        return True
