#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Callable, ForwardTyped, Unicode

from enaml.core.declarative import Declarative, d_

from .extension import Extension
from .extension_point import ExtensionPoint


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


def plugin_factory():
    """ A factory function which returns a plain Plugin instance.

    """
    from .plugin import Plugin
    return Plugin()


class PluginManifest(Declarative):
    """ A declarative class which represents a plugin manifest.

    """
    #: The globally unique identifier for the plugin. The suggested
    #: format is dot-separated, e.g. 'foo.bar.baz'.
    id = d_(Unicode())

    #: The factory which will create the Plugin instance. It should
    #: take no arguments and return an instance of Plugin. Well behaved
    #: applications will make this a function which lazily imports the
    #: plugin class so that startup times remain small.
    factory = d_(Callable(plugin_factory))

    #: The workbench instance with which this manifest is registered.
    #: This is assigned by the framework and should not be manipulated
    #: by user code.
    workbench = ForwardTyped(Workbench)

    #: An optional description of the plugin.
    description = d_(Unicode())

    @property
    def extensions(self):
        """ Get the list of extensions defined by the manifest.

        """
        return [c for c in self.children if isinstance(c, Extension)]

    @property
    def extension_points(self):
        """ Get the list of extensions points defined by the manifest.

        """
        return [c for c in self.children if isinstance(c, ExtensionPoint)]
