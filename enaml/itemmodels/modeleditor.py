#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Str, List, Typed

from .enums import ItemFlag, AlignmentFlag


class ItemEditor(Atom):
    """ A base class for defining item editors for models.

    Subclasses should reimplement the methods below as needed to edit
    the relevant item in a particular class of data model.

    """
    #: Storage for the item name. The semantic meaning of the name is
    #: left to the writer of the subclass.
    name = Str()

    def get_data(self, model):
        """ Get the data for the model item.

        Parameters
        ----------
        model : object
            The model object which holds the data.

        Returns
        -------
        result : object
            The data to show in the UI for the particular model item.
            The default method returns None.

        """
        return None

    def get_flags(self, model):
        """ Get the flags for the model item.

        Parameters
        ----------
        model : object
            The model object which holds the flags.

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
            The model object which holds the edit data.

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
            The model object which holds the icon.

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
            The model object which holds the tool tip.

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
            The model object which holds the status tip.

        Returns
        -------
        result : unicode or None
            The unicode status tip value for the model item, or None if
            the item has no status tip. The default method returns None.

        """
        return None

    def get_background(self, model):
        """ Get the status tip for the model item.

        Parameters
        ----------
        model : object
            The model object which holds the status tip.

        Returns
        -------
        result : unicode or None
            The unicode status tip value for the model item, or None if
            the item has no status tip. The default method returns None.

        """
        return None

    def get_foreground(self, model):
        return None

    def get_font(self, model):
        return None

    def get_text_alignment(self, model):
        return AlignmentFlag.AlignCenter

    def get_check_state(self, model):
        return None

    def get_size_hint(self, model):
        return None

    def set_data(self, model, value):
        return False

    def set_check_state(self, model, value):
        return False


class AttrEditor(ItemEditor):

    def get_data(self, model):
        return getattr(model, self.name)

    def set_data(self, model, value):
        setattr(model, self.name, value)


class EditGroup(Atom):

    name = Str()

    item_editors = List(Typed(ItemEditor))


class ModelEditor(Atom):

    model = Typed(object)

    def edit_groups(self):
        return []
