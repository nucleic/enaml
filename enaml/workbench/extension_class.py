#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, ForwardTyped, Typed

from .extension import Extension


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


class ExtensionClass(Atom):
    """ A base class for defining extension implementation classes.

    This class is used by an extension point to define the interface
    which must be implemented by extension classes.

    """
    #: A reference to the workbench which created the extension.
    workbench = ForwardTyped(Workbench)

    #: A reference to the Extension which declared this implementation.
    extension = Typed(Extension)

    def initialize(self, workbench, extension):
        """ Initialize the extension implementation.

        This method is called by the workbench after it instantiates
        the instance of this class. Subclasses may reimplement this
        method as needed to perform additional initialization.

        """
        self.workbench = workbench
        self.extension = extension
