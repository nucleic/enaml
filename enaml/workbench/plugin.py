#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, ForwardTyped, Typed

from .plugin_manifest import PluginManifest


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


class Plugin(Atom):
    """ A base class for defining workbench plugins.

    """
    #: A reference to the workbench instance which manages the plugin.
    #: This is assigned when the plugin is created by the workbench.
    #: It should not be manipulated by user code.
    workbench = ForwardTyped(Workbench)

    #: A reference to the manifest instance which declared the plugin.
    #: This is assigned when the plugin created by the workbench. It
    #: should not be manipulated by user code.
    manifest = Typed(PluginManifest)

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
