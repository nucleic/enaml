#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from .plugin_manifest import PluginManifest


class Plugin(Atom):
    """ A base class for defining workbench plugins.

    """
    #: A reference to the plugin manifest instance which declared the
    #: plugin. This is assigned by the framework and should never be
    #: manipulated by user code.
    manifest = Typed(PluginManifest)

    @property
    def workbench(self):
        """ Get the workbench which is handling the plugin.

        """
        return self.manifest.workbench

    def start(self):
        """ Start the life-cycle of the plugin.

        This method will be called by the workbench after it creates
        the plugin. The default implementation does nothing and can be
        ignored by subclasses which do not need life-cycle behavior.

        This method should never be called by user code.

        """
        pass

    def stop(self):
        """ Stop the life-cycle of the plugin.

        This method will be called by the workbench when the plugin is
        removed. The default implementation does nothing and can be
        ignored by subclasses which do not need life-cycle behavior.

        This method should never be called by user code.

        """
        pass
