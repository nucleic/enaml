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


class ExtensionObject(Atom):
    """ A base class for defining extension implementation classes.

    This class is used by an extension point to define the interface
    which must be implemented by extension implementation classes.

    """
    #: A reference to the workbench which created the extension. This
    #: is assigned by the workbench when it creates the object.
    workbench = ForwardTyped(Workbench)

    #: A reference to the Extension which declared this implementation.
    #: This is assigned by the workbench when it creates the object.
    extension = Typed(Extension)

    def initialize(self):
        """ An initialization point for subclasses.

        This method will be called after the object is instantiated
        and populated with the Workbench and Extension objects. It
        can be used by subclasses to initialize additional state
        before the object is handed off to the consuming plugin.

        The default implementation of this method is a no-op and can
        be ignored by subclasses which do not need the feature.

        """
        pass
