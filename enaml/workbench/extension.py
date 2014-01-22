#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Unicode


class Extension(Atom):
    """ A base class for defining an extensions to an extension point.

    An extension is used to declare a contribution from one plugin to
    an extension point of another. An extension point may restrict the
    allowed extension types to a particular subclass of Extension.

    """
    #: An optional identifier for the extension. This can be provided
    #: to enable querying the registry for a specific extension. It
    #: should be a unique value, but this is not strictly enforced.
    id = Unicode()

    #: An optional human readable name of the extension.
    name = Unicode()

    #: An optional human readable description of the extension.
    description = Unicode()

    #: The unique identifier of the extension point to which this
    #: extension contributes.
    point = Unicode()
