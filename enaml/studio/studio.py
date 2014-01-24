#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from atom.api import Callable, Typed, Unicode

from enaml.application import Application
from enaml.icon import Icon
from enaml.workbench.api import Workbench


CORE_UI = 'core_ui'

CORE_UI_PLUGIN = u'enaml.studio.core.ui'


class Studio(Workbench):
    """ A class for creating studio-style UI applications.

    The Enaml Studio class is a subclass of the Enaml Workbench which
    includes a core plugin for creating extensible UI applications.

    The studio framework includes additional optional plugins which
    implement useful behaviors such as a pluggable central dock area.

    """
    #: A callable object which returns an Enaml Application. This
    #: application object will be used to start the UI event loop
    #: when the studio is started. It provides the developer with
    #: the opportunity to use a custom application class if needed.
    #: If this is not provided, the QtApplication class will be used.
    application_factory = Callable()

    #: A callable object which returns an Enaml MainWindow. This
    #: window object will be used when the studio is started. This
    #: provides the developer with the opportunity to use a custom
    #: MainWindow class if needed. If this is not provided, the
    #: standard MainWindow class will be used.
    main_window_factory = Callable()

    #: The application instance created by the application factory.
    #: This value should not be manipulated by user code.
    application = Typed(Application)

    #: The root title to apply to the main window.
    title = Unicode()

    #: The icon to use for the main window.
    icon = Typed(Icon)

    def load_builtin_plugin(self, name):
        """ Load one of the builtin Enaml studio plugins.

        This method cannot be used to load arbitrary user plugins.
        Use the 'register' method on the base class for that purpose.

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
        self.register(data, validate=True)

    def start(self):
        """ Start the studio.

        This method will load the core studio plugin and start the
        main application event loop. This is a blocking call which
        will return when the application event loop exits.

        """
        # Load the builtin core ui plugin manifest.
        self.load_builtin_plugin(CORE_UI)

        # Create the application instance.
        app = Application.instance()
        if app is None:
            factory = self.application_factory
            if factory is None:
                from enaml.qt.qt_application import QtApplication
                factory = QtApplication
            app = factory()
        self.application = app

        # Activate the core ui plugin and show the main window.
        core = self.get_plugin(CORE_UI_PLUGIN)
        core.main_window.show()

        # Start the application event loop.
        app.start()

        # Formally stop the studio if the app terminated on its own.
        if self.application is not None:
            self.stop()

    def stop(self):
        """ Stop the studio.

        This method will stop the application event loop and cause
        the call to 'start' to return.

        """
        self.unregister(CORE_UI_PLUGIN)
        self.application.stop()
        self.application = None
