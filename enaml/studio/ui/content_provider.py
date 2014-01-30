#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.container import Container
from enaml.workbench.extension_object import ExtensionObject


class ContentProvider(ExtensionObject):
    """ An interface for creating window content providers.

    Plugins which contribute to the 'enaml.studio.ui.content' extension
    point should subclass this to provide window content.

    """
    #: The Container to use as the window content. The window content
    #: will automatically update if this value changes at runtime. The
    #: studio takes ownership of the Container and will destroy it at
    #: the appropriate time.
    content = Typed(Container)
