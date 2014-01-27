#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.container import Container
from enaml.workbench.api import ExtensionObject


class ContentProvider(ExtensionObject):
    """ An ExtensionObject for contributing content to the studio window.

    Plugins which contribute to the 'enaml.studio.ui.content' extension
    point should subclass this to provide window content.

    """
    #: The Container to use as the window content. The window content
    #: will automatically update if this value changes at runtime.
    content = Typed(Container)
