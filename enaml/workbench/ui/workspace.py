#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Unicode

from enaml.core.declarative import Declarative, d_
from enaml.widgets.container import Container


class Workspace(Declarative):
    """ A declarative class for defining a workspace object.

    """
    #: Extra information to display in the window title bar.
    window_title = d_(Unicode())

    #: The primary window content for the workspace. This will be
    #: destroyed automatically when the workspace is disposed.
    content = d_(Typed(Container))

    def dispose(self):
        """ Dispose of any resources allocated by the workspace.

        This method is called when the UI plugin closes the workspace.

        """
        pass
