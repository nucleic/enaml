#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from enaml.workbench.workbench import Workbench


PLUGIN_DIR = os.path.abspath(__file__)
PLUGIN_DIR = os.path.dirname(PLUGIN_DIR)
PLUGIN_DIR = os.path.join(PLUGIN_DIR, 'plugins')
PLUGIN_DIR = PLUGIN_DIR.replace('\\', '/')


class Studio(Workbench):
    """ A class for creating studio-style UI applications.

    The Enaml Studio class is a subclass of the Enaml Workbench which
    includes a set of core plugins for creating extensible UI apps.

    The studio framework includes additional optional plugins which
    implement useful behaviors such as a pluggable central dock area.

    The studio will automatically load the 'core' and 'ui' builtin
    plugins when it is started. User code is responsible for loading
    any other desired plugins.

    """
    def load_studio_plugin(self, name):
        """ Load one of the builtin Enaml studio plugins.

        This method cannot be used to load arbitrary user plugins. Use
        the 'register' method on the base class for that purpose.

        Parameters
        ----------
        name : str
            The name of the builtin studio plugin to load. This will
            correspond to one of the json files while live in the
            'plugins' directory alongside this file.

        """
        url = "file://%s/%s.json" % (PLUGIN_DIR, name)
        self.register(url)

    def run(self):
        """ Run the studio.

        This method will load the studio ui plugin and start the
        main application event loop. This is a blocking call which
        will return when the application event loop exits.

        """
        self.load_studio_plugin('ui')

        ui = self.get_plugin(u'enaml.studio.ui')
        ui.show_window()
        ui.start_application()

        # TODO stop all plugins on app exit?

        self.unregister(u'enaml.studio.ui')
