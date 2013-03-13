#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class ItemFlag(object):
    """ The available flags for an item in an item model.

    These values can be OR'd together to create the composite flags for
    a particular item in the model.

    These enum values are equivalent to the Qt::ItemFlag enum values.

    """
    NoItemFlags = 0x0

    ItemIsSelectable = 0x1

    ItemIsEditable = 0x2

    # TODO: ItemIsDragEnabled = 0x4

    # TODO: ItemIsDropEnabled = 0x8

    ItemIsUserCheckable = 0x10

    ItemIsEnabled = 0x20

    # TODO: ItemIsTristate = 0x40


class CheckState(object):
    """ The available values for item's check state.

    These enum values are equivalent to the Qt::CheckState enum values.

    """
    Unchecked = 0

    # TODO: PartiallyChecked = 1

    Checked = 2


class AlignmentFlag(object):
    """ The available values for text alignment.

    These values can be OR'd together to create the final alignment for
    a particular item in the model.

    These enum values are equivalent to the Qt::AlignmentFlag values.

    """
    AlignLeft = 0x1

    AlignRight = 0x2

    AlignHCenter = 0x4

    AlignJustify = 0x8

    AlignTop = 0x20

    AlignBottom = 0x40

    AlignVCenter = 0x80

    AlignCenter = AlignHCenter | AlignVCenter

    AlignHorizontalMask = AlignLeft | AlignRight | AlignHCenter | AlignJustify

    AlignVerticalMask = AlignTop | AlignBottom | AlignVCenter
