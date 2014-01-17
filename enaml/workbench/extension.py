#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode


class Extension(Atom):
    """ A base class for defining extensions.

    User code should subclass Extension to define the interface and
    behavior required for contributions to a given extension point.
    It is recommended that extensions behave as factories, so that
    userland imports can be deferred until an extension is actually
    used by the associated extension point.

    """
    #: The globally unique identifier of the extension point to which
    #: the extension object contributes.
    contributes_to = Unicode()
