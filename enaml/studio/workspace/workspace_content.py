#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.studio.ui.content_provider import ContentProvider


WORKSPACE_PLUGIN = u'enaml.studio.workspace'


class WorkspaceContent(ContentProvider):
    """ The provider object which contributes workspace content.

    """
    def initialize(self):
        """ Initialize the content provider.

        This method registers the provider with the workspace since
        the workspace model updates the provider directly.

        """
        workspace = self.workbench.get_plugin(WORKSPACE_PLUGIN)
        workspace.model.content_provider = self
