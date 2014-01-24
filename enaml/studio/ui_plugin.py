#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import ForwardTyped, Typed

import enaml
from enaml.application import Application
from enaml.workbench.api import Plugin

from .utils import highest_ranked
from .window_model import WindowModel


def StudioWindow():
    """ A lazy importer for the enaml StudioWindow.

    """
    with enaml.imports():
        from enaml.studio.studio_window import StudioWindow
    return StudioWindow


class UIPlugin(Plugin):
    """ The main UI plugin class for the Enaml studio.

    The ui plugin manages the extension points for the main window. User
    code can contribute menus to the menu bar and central widgets.

    """
    #: A reference to the Enaml application used by the ui. The
    #: application class can be provided via the extension point
    #: 'enaml.studio.ui.application'
    application = Typed(Application)

    #: A reference to the main window which is managed by this plugin.
    #: The main window class can be provided via the extension point
    #: 'enaml.studio.ui.window'
    main_window = ForwardTyped(StudioWindow)

    #: A reference to the window model which drives the main window.

    #--------------------------------------------------------------------------
    # Plugin API
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the plugin life-cycle.

        This method will initialize the main window, but not show it.
        The Studio instance is responsible for showing the window after
        this plugin is started.

        """
        self._initialize_application()
        self._initialize_window()

    def stop(self):
        """ Stop the plugin life-cycle.

        This will hide and destroy the main window.

        """
        self._destroy_window()
        self._destroy_application()

    #--------------------------------------------------------------------------
    # Studio API
    #--------------------------------------------------------------------------
    def show_main_window(self):
        """

        """
        self.main_window.show()

    def start_event_loop(self):
        """

        """
        self.application.start()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _initialize_application(self):
        """

        """
        bench = self.workbench
        extensions = bench.get_extensions('enaml.studio.ui.application')
        ext = highest_ranked(extensions)
        app_class = bench.load_extension_class(ext)
        app = app_class.instance()
        if app is None:
            app = app_class()
        self.application = app

    def _initialize_window(self):
        """ Initialize the main window instance.

        """
        bench = self.workbench
        extensions = bench.get_extensions('enaml.studio.ui.window')
        ext = highest_ranked(extensions)
        win_class = bench.load_extension_class(ext)
        self.main_window = win_class(window_model=WindowModel())
        self._initialize_branding()

    def _initialize_branding(self):
        """ Initialize the branding of the main window.

        """
    def _destroy_window(self):
        """ Destroy the main window instance.

        """
        self.main_window.hide()
        self.main_window.destroy()
        self.main_window = None

    def _destroy_application(self):
        """

        """
        self.application.stop()
        self.application = None


