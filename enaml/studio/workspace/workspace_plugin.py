#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.workbench.plugin import Plugin

from .workspace_model import WorkspaceModel


class WorkspacePlugin(Plugin):
    """

    """
    def start(self):
        """

        """
        self._create_model()


    def stop(self):
        """

        """
        self._release_model()

    @property
    def model(self):
        """ Get a reference to the workspace model.

        This is a framework property used by various classes related to
        this plugin. It should not be consumed by user code.

        Returns
        -------
        result : WorkspaceModel
            The workspace model which is drives the UI.

        """
        return self._model

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The workspace model instance which drives the UI.
    _model = Typed(WorkspaceModel)

    def _create_model(self):
        self._model = WorkspaceModel(workbench=self.workbench)

