#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import atomref, Str, Typed

from enaml.workbench.api import RegistryEventListener


class RefreshListener(RegistryEventListener):
    """ A registry event listener for use by plugin classes.

    This listener will invoke a named method on the owner plugin
    when extensions are added or removed from the extension point
    for which the listener is registered.

    """
    #: An atomref to the owner plugin.
    plugin_ref = Typed(atomref)

    #: The name of the refresh method to invoke on the owner.
    method_name = Str()

    def extensions_added(self, extensions):
        """ Handle the extensions added registry notification.

        This will refresh the owner ui plugin.

        """
        self._refresh()

    def extensions_removed(self, extensions):
        """ Handle the extensions removed registry notification.

        This will refresh the owner ui plugin.

        """
        self._refresh()

    def _refresh(self):
        """ Trigger a refresh of the owner ui plugin.

        """
        if self.plugin_ref:
            getattr(self.plugin_ref(), self.method_name)()
