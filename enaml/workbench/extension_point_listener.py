#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from .extension_point import ExtensionPoint
from .plugin import Plugin


class ExtensionPointListener(Atom):
    """ An extension point listener which dispatches atom observers.

    Instances of this class are created by a plugin manager when a
    plugin is added to the workbench. It should not be used directly
    by user code.

    """
    #: A reference tot he extension point object. This will be set
    #: by the plugin manager when the plugin is registered.
    extension_point = Typed(ExtensionPoint)

    #: A reference to the underlying plugin object. This will be set
    #: and cleared by the plugin manager when the plugin is registered.
    plugin = Typed(Plugin)

    def __nonzero__(self):
        """ The listener will test false if the plugin is removed.

        """
        return bool(self.plugin)

    def __call__(self, event):
        """ Invoke the listener and the associated plugin observers.

        """
        plugin = self.plugin
        if plugin is not None:
            extp = self.extension_point
            change = {'type': 'extension-point', 'object': plugin,
                      'name': extp.name, 'value': event}
            extp.notify(plugin, change)
            plugin.notify(extp.name, change)
