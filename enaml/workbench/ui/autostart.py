#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode

from enaml.core.declarative import Declarative, d_


class Autostart(Declarative):
    """ A declarative object for use with auto start extensions.

    """
    #: The id of the plugin which should be preemptively started.
    plugin_id = d_(Unicode())
