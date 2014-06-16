#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Callable, Unicode

from enaml.core.declarative import Declarative, d_


class Command(Declarative):
    """ A declarative class for defining a workbench command.

    """
    #: The globally unique identifier for the command.
    id = d_(Unicode())

    #: An optional description of the command.
    description = d_(Unicode())

    #: A required callable which handles the command. It must accept a
    #: single argument, which is an instance of ExecutionEvent.
    handler = d_(Callable())
