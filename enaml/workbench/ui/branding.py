#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Unicode

from enaml.core.declarative import Declarative, d_
from enaml.icon import Icon


class Branding(Declarative):
    """ A declarative class for defining window branding.

    """
    #: The primary title of the workbench window.
    title = d_(Unicode())

    #: The icon for the workbench window.
    icon = d_(Typed(Icon))
