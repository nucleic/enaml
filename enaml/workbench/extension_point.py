#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Subclass, Unicode

from .extension import Extension


class ExtensionPoint(Atom):
    """ A class used to describe an extension point of a plugin.

    An extension point is used to declare how plugins can contribute
    functionality to another plugin. It contains metadata and an
    optional extension validator.

    """
    #: The globally unique identifier of the plugin. This can be any
    #: string, but it will typically be in dot-separated form.
    id = Unicode()

    #: An optional human readable name of the extension point.
    name = Unicode()

    #: An optional human readable description of the extension point.
    description = Unicode()

    #: The allowed type (and subtypes) of contributed extensions.
    extension_type = Subclass(Extension)
