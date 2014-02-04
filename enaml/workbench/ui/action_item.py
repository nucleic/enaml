#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Dict, Typed, Unicode

from enaml.core.declarative import Declarative, d_
from enaml.icon import Icon


class ActionItem(Declarative):
    """ A declarative class for defining a workbench action item.

    """
    #: The globally unique identifier for the action item.
    id = d_(Unicode())

    #: The identifier of the parent menu in which the action resides. A
    #: group can be specified by appending a colon followed by the name
    #: of the desired group. e.g. file:close_group
    location = d_(Unicode())

    #: The item id before which this action will appear.
    before = d_(Unicode())

    #: The item id after which this action will appear.
    after = d_(Unicode())

    #: The id of the Command invoked by the action.
    command_id = d_(Unicode())

    #: The user parameters to pass to the command handler.
    parameters = d_(Dict())

    #: The display label for the action.
    label = d_(Unicode())

    #: Whether or not the action is visible.
    visible = d_(Bool(True))

    #: Whether or not the action is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the action is checkable.
    checkable = d_(Bool(False))

    #: Whether or not the checkable action is checked.
    checked = d_(Bool(False))

    #: The default display icon for the action.
    icon = d_(Typed(Icon))

    #: The tooltip for the action.
    tool_tip = d_(Unicode())

    #: The statustip for the action.
    status_tip = d_(Unicode())
