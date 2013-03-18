#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import set_default

from .baseitem import DefaultItemFlags
from .enums import ItemFlag
from .item import Item


class EditableItem(Item):
    """ An Item subclass which is editable by default.

    """
    flags = set_default(DefaultItemFlags | ItemFlag.ItemIsEditable)


class IntItem(EditableItem):
    """ An editable item for editing integer values.

    """
    converter = set_default(int)


class LongItem(EditableItem):
    """ An editable item for editing long integer values.

    """
    converter = set_default(long)


class FloatItem(EditableItem):
    """ An editable item for editing float value.

    """
    converter = set_default(float)


class StrItem(EditableItem):
    """ An editable item for editing string values.

    """
    converter = set_default(str)


class UnicodeItem(EditableItem):
    """ An editable item for editing unicode values.

    """
    converter = set_default(unicode)
