#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, ForwardTyped


def PluginManifest():
    """ A lazy forward import function for the PluginManifest type.

    """
    from .plugin_manifest import PluginManifest
    return PluginManifest


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


class Plugin(Atom):
    """ A base class for defining workbench plugins.

    """
    #: A reference to the workbench instance which manages the plugin.
    #: This is assigned when the plugin created by the workbench. It
    #: should not be manipulated by user code.
    workbench = ForwardTyped(Workbench)

    #: A reference to the manifest instance which declared the plugin.
    #: This is assigned when the plugin created by the workbench. It
    #: should not be manipulated by user code.
    manifest = ForwardTyped(PluginManifest)

    def get_extension(self, extension_point_id, extension_id):
        """ Get a specific extension contributed to an extension point.

        This is a convenience method which proxies the call to the
        underlying workbench.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier for the extension point
            of interest.

        extension_id : unicode
            The globally unique identifier for the extension of
            interest.

        Returns
        -------
        result : Extension or None
            The requested extension object, or None if it does not
            exist.

        """
        workbench = self.workbench
        if workbench is not None:
            return workbench.get_extension(extension_point_id, extension_id)
        return None

    def get_extensions(self, extension_point_id):
        """ Get the extensions contributed to an extension point.

        This is a convenience method which proxies the call to the
        underlying workbench.

        Parameters
        ----------
        extension_point_id : unicode
            The globally unique identifier for the extension point
            of interest.

        Returns
        -------
        result : list
            The list of Extension objects contributed to the specified
            extension point.

        """
        workbench = self.workbench
        if workbench is not None:
            return workbench.get_extensions(extension_point_id)
        return []

    def start(self):
        """ Start the life-cycle of the plugin.

        This method will be called by the workbench after it creates
        the plugin. The default implementation does nothing and can be
        safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass

    def stop(self):
        """ Stop the life-cycle of the plugin.

        This method will be called by the workbench before it removes
        the plugin. The default implementation does nothing and can be
        safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass
