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
    #: The "/" separated path to this item in the menu bar.
    path = d_(Unicode())

    #: The parent menu group to which this action item belongs.
    group = d_(Unicode())

    #: The action item will appear before this item in its group.
    before = d_(Unicode())

    #: The action item will appear after this item in its group.
    after = d_(Unicode())

    #: The id of the Command invoked by the action.
    command = d_(Unicode())

    #: The user parameters to pass to the command handler.
    parameters = d_(Dict())

    #: The display label for the action.
    label = d_(Unicode())

    #: The shortcut keybinding for the action. e.g. Ctrl+C
    shortcut = d_(Unicode())

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
