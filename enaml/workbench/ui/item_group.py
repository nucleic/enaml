#------------------------------------------------------------------------------
# Copyright (c) 2013-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str

from enaml.core.declarative import Declarative, d_


class ItemGroup(Declarative):
    """ A declarative class for defining an item group in a menu.

    """
    #: The identifier of group within the menu.
    id = d_(Str())

    #: Whether or not the group is visible.
    visible = d_(Bool(True))

    #: Whether or not the group is enabled.
    enabled = d_(Bool(True))

    #: Whether or not checkable ations in the group are exclusive.
    exclusive = d_(Bool(False))
