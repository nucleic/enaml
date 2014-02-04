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
    """ A declarative class for defining a plugin command.

    """
    #: The identifier for the command. This should typically be globally
    #: unique, but is not enforced so that handlers can be overridden.
    id = d_(Unicode())

    #: The handler for the command. The first argument will always be
    #: the workbench instance. Additional arguments and keywords may be
    #: passed by the code which invokes the command. Well behaved apps
    #: will make this a function which lazily imports its dependencies
    #: in order to keep startup times short.
    handler = d_(Callable())
