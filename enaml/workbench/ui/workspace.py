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
from enaml.workbench.workbench import Workbench


class Workspace(Declarative):
    """ A declarative class for defining a workspace object.

    """
    #: Extra information to display in the window title bar.
    window_title = d_(Unicode())

    #: The primary window content for the workspace. This will be
    #: destroyed automatically when the workspace is disposed.
    content = d_(Typed(Container))

    #: The workbench object which owns the workspace. This will be
    #: assigned when the ui plugin creates the workspace. It will
    #: be available by the time the 'start' method is called.
    workbench = Typed(Workbench)

    def start(self):
        """ Start the workspace.

        This method is called when the UI plugin starts the workspace.
        This can be used to load content or any other resource which
        should exist for the life of the workspace.

        """
        pass

    def stop(self):
        """ Stop the workspace.

        This method is called when the UI plugin closes the workspace.
        This should be used to release any resources acquired during
        the lifetime of the workspace. The content Container will be
        destroyed automatically after this method returns.

        """
        pass
