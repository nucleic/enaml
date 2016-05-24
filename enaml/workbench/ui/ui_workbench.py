#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import unicode_literals

from enaml.workbench.workbench import Workbench


UI_PLUGIN = u'enaml.workbench.ui'


class UIWorkbench(Workbench):
    """ A class for creating workbench UI applications.

    The UIWorkbench class is a subclass of Workbench which loads the
    builtin ui plugin and provides an entry point to start the main
    application event loop.

    """
    def run(self):
        """ Run the UI workbench application.

        This method will load the core and ui plugins and start the
        main application event loop. This is a blocking call which
        will return when the application event loop exits.

        """
        import enaml
        with enaml.imports():
            from enaml.workbench.core.core_manifest import CoreManifest
            from enaml.workbench.ui.ui_manifest import UIManifest

        self.register(CoreManifest())
        self.register(UIManifest())

        ui = self.get_plugin(UI_PLUGIN)
        ui.show_window()
        ui.start_application()

        # TODO stop all plugins on app exit?

        self.unregister(UI_PLUGIN)
