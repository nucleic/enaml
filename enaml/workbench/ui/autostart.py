#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str

from enaml.core.declarative import Declarative, d_


class Autostart(Declarative):
    """ A declarative object for use with auto start extensions.

    """
    #: The id of the plugin which should be preemptively started.
    plugin_id = d_(Str())
