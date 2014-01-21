#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Callable, List, Unicode

from .extension import Extension
from .extension_point import ExtensionPoint


class PluginManifest(Atom):
    """ A class used to describe a plugin.

    A plugin manifest is used to declare the metadata, extension points,
    and extensions of a plugin, as well as a factory to use for creating
    instances of the plugin.

    """
    #: The globally unique identifier of the plugin. This can be any
    #: string, but it will typically be in dot-separated form.
    id = Unicode()

    #: An optional human readable name of the plugin.
    name = Unicode()

    #: An optional human readable description of the plugin.
    description = Unicode()

    #: An optional callable object which takes no arguments and returns
    #: a Plugin instance. The factory will be invoked the first time the
    #: plugin instance is requested and should lazily import its runtime
    #: dependencies to keep application startup time low. If a factory
    #: is not provided, a default plugin will be created.
    factory = Callable()

    #: The list of extension points exposed by the plugin.
    extension_points = List(ExtensionPoint)

    #: The list of extensions contributed by the plugin.
    extensions = List(Extension)
