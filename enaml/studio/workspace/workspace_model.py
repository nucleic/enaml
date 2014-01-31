#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from enaml.studio.ui.content_provider import ContentProvider
from enaml.workbench.workbench import Workbench


class WorkspaceModel(Atom):
    """ A handler object which drives changes to the workspace.

    The data for the model is provided and kept up-to-date by the
    workspace plugin.

    This is a framework class which should not be used directly by
    user code.

    """
    #: A reference to the workbench. This is provided by the plugin.
    workbench = Typed(Workbench)

    #: The content provider for the window. This will be set by the
    #: workspace plugin when it creates the workspace model.
    content_provider = Typed(ContentProvider)

    #: A mapping of unicode config names to extension object.
    configs = Typed(dict, ())

    #: The cur
    def select_config(self, name):
        pass
