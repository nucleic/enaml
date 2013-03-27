#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Int, Typed, Value, observe

from enaml.core.declarative import Declarative, d_

from .style import Style


class ItemFlag(object):
    """ The available item flags for an item in an data model.

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
    """ The available values for the check state of a data model item.

    These enum values are equivalent to the Qt::CheckState enum values.

    """
    Unchecked = 0

    # TODO: PartiallyChecked = 1

    Checked = 2


def item_flag_property(flag):
    """ Create a property to get and set the item flags on an item.

    Parameters
    ----------
    flag : ItemFlag
        The integer item flag of interest.

    Returns
    -------
    result : property
        A get/set property to manipulate the given flag.

    """
    def getter(self):
        return (self.flags & flag) != 0

    def setter(self, value):
        if value:
            self.flags |= flag
        else:
            self.flags &= ~flag

    return property(getter, setter)


class Item(Declarative):
    """ An object representing an item in a data model.

    An Item encapsulates a data value and the styling information for
    rendering that value to the screen.

    """
    #: The data value for the item. The default value is None.
    data = d_(Value())

    #: The check state for the item. The default value is None.
    check_state = d_(Enum(None, CheckState.Unchecked, CheckState.Checked))

    #: The style to use for the item. The default value is None.
    style = d_(Typed(Style))

    #: The flags for the item. The default is selectable and enabled.
    flags = d_(Int(ItemFlag.Selectable | ItemFlag.Enabled))

    #: A get/set property for manipulating the 'Selectable' item flag.
    selectable = item_flag_property(ItemFlag.Selectable)

    #: A get/set property for manipulating the 'Editable' item flag.
    editable = item_flag_property(ItemFlag.Editable)

    #: A get/set property for manipulating the 'Checkable' item flag.
    checkable = item_flag_property(ItemFlag.Checkable)

    #: A get/set property for manipulating the 'Enabled' item flag.
    enabled = item_flag_property(ItemFlag.Enabled)

    def display_data(self):
        """ Get the data to display for the item.

        This method may be reimplemented in a subclass to apply custom
        data formatting and conversion.

        Returns
        -------
        result : object
            The data value to display for the item. The default
            method returns the 'data' attribute directly.

        """
        return self.data

    def edit_data(self):
        """ Get the data to display when editing the item.

        This method may be reimplemented in a subclass to apply custom
        data formatting and conversion.

        Returns
        -------
        result : object
            The data value to use for editing the item. The default
            method returns the 'data' attribute directly.

        """
        return self.data

    def set_data(self, value):
        """ Set the data for the item.

        This method may be reimplemented in a subclass to apply custom
        data formatting and conversion.

        Parameters
        ----------
        value : object
            The data value input by the user.

        Returns
        -------
        result : bool
            True if the item was updated successfully, False otherwise.
            The default method sets the value of the 'data' attribute
            and returns True.

        """
        self.data = value
        return True

    def tool_tip(self):
        """ Get the tool tip for the item.

        Returns
        -------
        result : unicode or None
            The unicode tool tip to use for the item, or None if the
            item has no tool tip. The default method returns None.

        """
        return None

    def status_tip(self):
        """ Get the status tip for the item.

        Returns
        -------
        result : unicode or None
            The unicode status tip to use for the item, or None if the
            item has no status tip. The default method returns None.

        """
        return None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: Private storage for use by a toolkit backend.
    _tk_data = Value()

    @observe(('data', 'check_state', 'style', 'flags'))
    def _item_changed(self, change):
        """ A private observer for item state change.

        If the item has a parent with an 'item_changed' method, it will
        be invoked when the item changes, passing itself as the first
        argument to the handler.

        """
        handler = getattr(self.parent, 'item_changed', None)
        if handler is not None:
            handler(self)
