#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import cPickle

from atom.api import Unicode

from enaml.layout.api import HSplitLayout
from enaml.widgets.api import Container, DockArea
from enaml.widgets.dock_area import save_dock_area, restore_dock_area
from enaml.workbench.ui.api import Workspace

import enaml
with enaml.imports():
    from persistent_view import Pane, PersistentManifest


print 'Imported Persistent Workspace!'


#: Storage for the persisted dock area data. This would be saved
#: to some persistent storage media in a real application.
PERSISTED_DOCK_AREA_DATA = None


def create_new_area():
    """ Create a new persistent dock area.

    """
    area = DockArea(name='the_dock_area')
    Pane(area, name='first', title='Pane 0')
    Pane(area, name='second', title='Pane 1')
    area.layout = HSplitLayout('first', 'second')
    return area


class PersistentWorkspace(Workspace):
    """ A custom Workspace class for the crash course example.

    """
    #: Storage for the plugin manifest's id.
    _manifest_id = Unicode()

    def start(self):
        """ Start the workspace instance.

        This method will create the container content and register the
        provided plugin with the workbench.

        """
        content = Container(padding=0)
        area = self.load_area()
        area.set_parent(content)
        self.content = content
        manifest = PersistentManifest()
        self._manifest_id = manifest.id
        self.workbench.register(manifest)

    def stop(self):
        """ Stop the workspace instance.

        This method will unregister the workspace's plugin that was
        registered on start.

        """
        self.save_area()
        self.workbench.unregister(self._manifest_id)

    def save_area(self):
        """ Save the dock area for the workspace.

        """
        global PERSISTED_DOCK_AREA_DATA
        area = self.content.find('the_dock_area')
        data = cPickle.dumps(save_dock_area(area))
        PERSISTED_DOCK_AREA_DATA = data

    def load_area(self):
        """ Load the dock area for the workspace.

        """
        if PERSISTED_DOCK_AREA_DATA is not None:
            data = cPickle.loads(PERSISTED_DOCK_AREA_DATA)
            return restore_dock_area(data)
        return create_new_area()
