#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from enaml.workbench.api import Workbench


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
    def load_builtin_plugin(self, name):
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
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        path = os.path.join(dirname, 'plugins', name + '.json')
        with open(path) as f:
            data = f.read()
        self.register(data)

    def run(self):
        """ Run the studio.

        This method will load the core studio plugin and start the
        main application event loop. This is a blocking call which
        will return when the application event loop exits.

        """
        self.load_builtin_plugin('core')
        self.load_builtin_plugin('ui')

        ui = self.get_plugin(u'enaml.studio.ui')
        ui.show_window()
        ui.start_application()

        self.unregister(u'enaml.studio.ui')
        self.unregister(u'enaml.studio.core')
