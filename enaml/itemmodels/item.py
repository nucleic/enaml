#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Str

from .enums import ItemFlag, AlignmentFlag


class Item(Atom):
    """ A base class for defining items for item models.

    Subclasses should reimplement the methods of the class as needed to
    implemented appropriate behavior for a class of models.

    """
    #: Storage for the item name. By default, the name is used to access
    #: an attribute on a given data model.
    name = Str()

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
            method returns an or'd combo of selectable and enabled.

        """
        return ItemFlag.ItemIsSelectable | ItemFlag.ItemIsEnabled

    def get_edit_data(self, model):
        """ Get the edit data for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : object
            The data to show in the UI for the particular model item
            when the item is opened for editing. The default method
            simply returns the display data.

        """
        return self.get_data(model)

    def get_icon(self, model):
        """ Get the icon for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : Icon or None
            The Enaml icon object for the model item, or None if the
            item has no icon. The default method returns None.

        """
        return None

    def get_tool_tip(self, model):
        """ Get the tool tip for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : unicode or None
            The unicode tool tip value for the model item, or None if
            the item has no tool tip. The default method returns None.

        """
        return None

    def get_status_tip(self, model):
        """ Get the status tip for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : unicode or None
            The unicode status tip value for the model item, or None if
            the item has no status tip. The default method returns None.

        """
        return None

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
            None.

        """
        return None

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
            None.

        """
        return None

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
            font. The default method returns None.

        """
        return None

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
            default method returns AlignCenter.

        """
        return AlignmentFlag.AlignCenter

    def get_check_state(self, model):
        """ Get the check state for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        Returns
        -------
        result : CheckState or None
            The CheckState for the model item, or None if the item has
            no check state. The default method returns None.

        """
        return None

    def get_size_hint(self, model):
        """ Get the size hint for the model item.

        """
        return None

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
            otherwise. The default method returns False.

        """
        return False

    def set_check_state(self, model, value):
        """ Set the check state for the model item.

        Parameters
        ----------
        model : object
            The relevant model object for the operation.

        value : CheckState
            The check state enum value to set for the model item.

        Returns
        -------
        result : bool
            True if the model item was successfully updated, False
            otherwise. The default method returns False.

        """
        return False