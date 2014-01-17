#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Unicode


class ExtensionPointEvent(Atom):
    """ A class representing changes to an extension point.

    """
    #: The globally unique identifier of the extension point.
    identifier = Unicode()

    #: The list of extensions removed from the extension point.
    removed = List()

    #: The list of extensions added to the extension point.
    added = List()
