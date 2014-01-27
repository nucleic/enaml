#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.icon import Icon
from enaml.workbench.api import ExtensionObject


class IconProvider(ExtensionObject):
    """ An ExtensionObject for contributing a studio window title.

    Plugins which contribute to the 'enaml.studio.ui.title' extension
    point should subclass this to provide a window title.

    """
    #: The icon to use as the window icon. The window icon will
    #: automatically update if this value changes at runtime.
    icon = Typed(Icon)
