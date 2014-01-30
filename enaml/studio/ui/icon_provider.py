#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.icon import Icon
from enaml.workbench.extension_object import ExtensionObject


class IconProvider(ExtensionObject):
    """ An interface for creating icon providers.

    Plugins which contribute to the 'enaml.studio.ui.icon' extension
    point should subclass this to provide a studio icon.

    """
    #: The icon to use as the studio icon. The studio icon will
    #: automatically update if this value changes at runtime.
    icon = Typed(Icon)
