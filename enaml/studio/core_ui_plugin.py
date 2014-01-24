#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.studio.studio import Studio
from enaml.widgets.main_window import MainWindow
from enaml.workbench.api import Plugin


class CoreUIPlugin(Plugin):
    """ The core UI plugin class for the Enaml studio.

    The core ui plugin manages the extension points for the main window.
    User code can contribute menus to the menu bar and central widgets.
    This plugin must be used with an instance of the Enaml Studio class.

    """
    #: A redefinition of the workbench attribute to enfore the use
    #: of the Studio Workbench subclass.
    workbench = Typed(Studio)

    #: A reference to the main window which is managed by this plugin.
    #: The main window is created when the plugin is started, using
    #: the main window factory provided to the Studio instance.
    main_window = Typed(MainWindow)

    #--------------------------------------------------------------------------
    # Plugin API
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the plugin life-cycle.

        This method will initialize the main window, but not show it.
        The Studio instance is responsible for showing the window after
        this plugin is started.

        """
        self._initialize_window()

    def stop(self):
        """ Stop the plugin life-cycle.

        This will hide and destroy the main window.

        """
        self._destroy_window()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _initialize_window(self):
        """ Initialize the main window instance.

        """
        studio = self.workbench
        factory = studio.main_window_factory or MainWindow
        window = self.main_window = factory()
        window.title = studio.title
        window.icon = studio.icon

    def _destroy_window(self):
        """ Destroy the main window instance.

        """
        self.main_window.hide()
        self.main_window.destroy()
        self.main_window = None
