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
            The relevant model object for the operation.

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


class AttrEditor(ItemEditor):
    """ An ItemEditor which accesses an attribute on the model.

    The 'name' assigned to the editor is used as the attribute name to
    lookup on the model when data is corrected.

    """
    def get_data(self, model):
        """ Get the data for the model item.

        This method retrieves the data by doing a getattr on the model
        using the 'name' provided to the editor.

        """
        return getattr(model, self.name)

    def set_data(self, model, value):
        """ Set the data for the model item.

        This method sets the data by doing a setattr on the model
        using the 'name' provided to the editor.

        """
        setattr(model, self.name, value)
        return True


class EditGroup(Atom):
    """ A class which groups together a collection of item editors.

    An EditGroup is used to collect related item editors into a logical
    collection. The various item models use these groups to generate
    their internal item layouts.

    """
    #: The name of the edit group. The semantic meaning of the name is
    #: left to the particular item model consuming the group.
    name = Str()

    #: The list of item editors for the edit group. Whenever possible,
    #: ItemEditor instances should be shared in an application. The
    #: various item models will keep strong references to these editors,
    #: so to keep the memory footprint low when dealing with a large
    #: number of models, only create the minimum necessary editors and
    #: share them. This list will not be copied on assignment, so lists
    #: of item editors can also be shared.
    item_editors = List(ItemEditor, copy=False)


class ModelEditor(Atom):
    """ A class which defines an editor for a model object.

    A ModelEditor comprises a 'model' object and a collection of editors
    for that model. Instances of 'ModelEditor' are give to the various
    item model implementations to generate a model usable by the UI.

    """
    #: The model object to be edited by this editor. Subclasses may
    #: redefine this member to enforce more strict type checking.
    model = Typed(object)

    #: The list of edit groups for the model editor. When possible,
    #: EditGroup instances should be shared between ModelEditors.
    #: This helps keep the memory footprint of an application low.
    #: This list will not be copied on assignment, so lists of edit
    #: goups can also be shared.
    edit_groups = List(EditGroup, copy=False)
