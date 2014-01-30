#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode

from enaml.workbench.extension_object import ExtensionObject


class TitleProvider(ExtensionObject):
    """ An interface for creating window title providers.

    Plugins which contribute to the 'enaml.studio.ui.title' extension
    point should subclass this to provide a window title.

    """
    #: The unicode string to use as the window title. The window title
    #: will automatically update if this value changes at runtime.
    title = Unicode()
