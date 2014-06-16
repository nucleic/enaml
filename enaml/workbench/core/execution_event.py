#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Dict, Typed, Value

from enaml.workbench.workbench import Workbench

from .command import Command


class ExecutionEvent(Atom):
    """ The object passed to a command handler when it is invoked.

    """
    #: The command which is being invoked.
    command = Typed(Command)

    #: The workbench instance which owns the command.
    workbench = Typed(Workbench)

    #: The user-supplied parameters for the command.
    parameters = Dict()

    #: The user-object object which triggered the command.
    trigger = Value()
