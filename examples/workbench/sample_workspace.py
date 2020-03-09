#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import print_function

from atom.api import Subclass, Str

from enaml.widgets.api import Container
from enaml.workbench.api import PluginManifest
from enaml.workbench.ui.api import Workspace


print('Imported Sample Workspace!')


class SampleWorkspace(Workspace):
    """ A custom Workspace class for the crash course example.

    This workspace class will instantiate the content and register an
    additional plugin with the workbench when it is started. The extra
    plugin can be used to add addtional functionality to the workbench
    window while this workspace is active. The plugin is unregistered
    when the workspace is stopped.

    """
    #: The enamldef'd Container to create when the workbench is started.
    content_def = Subclass(Container)

    #: The enamldef'd PluginManifest to register on start.
    manifest_def = Subclass(PluginManifest)

    #: Storage for the plugin manifest's id.
    _manifest_id = Str()

    def start(self):
        """ Start the workspace instance.

        This method will create the container content and register the
        provided plugin with the workbench.

        """
        self.content = self.content_def()
        manifest = self.manifest_def()
        self._manifest_id = manifest.id
        self.workbench.register(manifest)

    def stop(self):
        """ Stop the workspace instance.

        This method will unregister the workspace's plugin that was
        registered on start.

        """
        self.workbench.unregister(self._manifest_id)
