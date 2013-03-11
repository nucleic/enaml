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
    NO_ITEM_FLAGS = 0x0

    ITEM_IS_SELECTABLE = 0x1

    ITEM_IS_EDITABLE = 0x2

    # TODO: ITEM_IS_DRAG_ENABLED = 0x4

    # TODO: ITEM_IS_DROP_ENABLED = 0x8

    ITEM_IS_USER_CHECKABLE = 0x10

    ITEM_IS_ENABLED = 0x20

    # TODO: ITEM_IS_TRISTATE = 0x40


class CheckState(object):
    """ The available values for item's check state.

    These enum values are equivalent to the Qt::CheckState enum values.

    """
    UNCHECKED = 0

    # TODO: PARTIALLY_CHECKED = 1

    CHECKED = 2


class AlignmentFlag(object):
    """ The available values for text alignment.

    These values can be OR'd together to create the final alignment for
    a particular item in the model.

    These enum values are equivalent to the Qt::AlignmentFlag values.

    """
    ALIGN_LEFT = 0x1

    ALIGN_RIGHT = 0x2

    ALIGN_H_CENTER = 0x4

    ALIGN_JUSTIFY = 0x8

    ALIGN_TOP = 0x20

    ALIGN_BOTTOM = 0x40

    ALIGN_V_CENTER = 0x80

    ALIGN_CENTER = ALIGN_H_CENTER | ALIGN_V_CENTER

    ALIGN_HORIZONTAL_MASK = (
        ALIGN_LEFT | ALIGN_RIGHT | ALIGN_H_CENTER | ALIGN_JUSTIFY
    )

    ALIGN_VERTICAL_MASK = (ALIGN_TOP | ALIGN_BOTTOM | ALIGN_V_CENTER)
