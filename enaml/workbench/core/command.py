#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Callable, Str

from enaml.core.declarative import Declarative, d_


class Command(Declarative):
    """ A declarative class for defining a workbench command.

    """
    #: The globally unique identifier for the command.
    id = d_(Str())

    #: An optional description of the command.
    description = d_(Str())

    #: A required callable which handles the command. It must accept a
    #: single argument, which is an instance of ExecutionEvent.
    handler = d_(Callable())
