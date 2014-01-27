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

from .application_factory import ApplicationFactory
from .content_provider import ContentProvider
from .icon_provider import IconProvider
from .title_provider import TitleProvider
from .utils import highest_ranked
from .window_factory import WindowFactory
from .window_model import WindowModel


APPLICATION_POINT = u'enaml.studio.ui.application'

CONTENT_POINT = u'enaml.studio.ui.content'

ICON_POINT = u'enaml.studio.ui.icon'

MENUS_POINT = u'enaml.studio.ui.menus'

TITLE_POINT = u'enaml.studio.ui.title'

WINDOW_POINT = u'enaml.studio.ui.window'


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
    #: A reference to the Enaml application used by the ui. It can be
    #: provided via the 'enaml.studio.ui.application' extension point.
    _application = Typed(Application)

    #: A reference to the main window for the ui. It can be provided
    #: via the 'enaml.studio.ui.window' extension point.
    _window = ForwardTyped(StudioWindow)

    #: The view model object used to drive the window.
    _model = Typed(WindowModel, ())

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
        self._initialize_model()
        self._initialize_window()

    def stop(self):
        """ Stop the plugin life-cycle.

        This will hide and destroy the main window.

        """
        self._destroy_window()
        self._destroy_model()
        self._destroy_application()

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def show_window(self):
        """

        """
        self._window.show()

    def start_application(self):
        """

        """
        self._application.start()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _initialize_application(self):
        workbench = self.workbench
        extensions = workbench.get_extensions(APPLICATION_POINT)
        if not extensions:
            msg = "Cannot create an Application instance. No plugin "\
                  "contributed a factory to the '%s' extension point."
            raise RuntimeError(msg % APPLICATION_POINT)
        extension = highest_ranked(extensions)
        factory = workbench.create_extension_object(extension)
        if not isinstance(factory, ApplicationFactory):
            msg = "extension '%s' created non-ApplicationFactory type '%s'"
            raise TypeError(msg % (extension.cls, type(factory).__name__))
        self._application = factory()

    def _initialize_model(self):
        self._initialize_title()
        self._initialize_icon()
        #self._initialize_menus()
        self._initialize_content()

    def _initialize_title(self):
        workbench = self.workbench
        extensions = workbench.get_extensions(TITLE_POINT)
        if not extensions:
            return
        extension = highest_ranked(extensions)
        if extension.cls:
            provider = workbench.create_extension_object(extension)
        else:
            title = extension.get_property(u'title', u'')
            provider = TitleProvider(title=title)
        self._model.title_provider = provider

    def _initialize_icon(self):
        workbench = self.workbench
        extensions = workbench.get_extensions(ICON_POINT)
        if not extensions:
            return
        extension = highest_ranked(extensions)
        if extension.cls:
            provider = workbench.create_extension_object(extension)
        else:
            provider = IconProvider()  # XXX use a loader
        self._model.icon_provider = provider

    # def _initialize_menus(self):
    #     workbench = self.workbench
    #     extensions = workbench.get_extensions(MENUS_POINT)
    #     if not extensions:
    #         return
    #     action_exts = []
    #     for ext in extensions:
    #         if ext.get_property(u'type') == u'action':
    #             action_exts.append(ext)
    #     self._model.menus = create_menus(action_exts)

    def _initialize_content(self):
        workbench = self.workbench
        extensions = workbench.get_extensions(CONTENT_POINT)
        if not extensions:
            provider = ContentProvider()
        else:
            extension = highest_ranked(extensions)
            provider = workbench.create_extension_object(extension)
        self._model.content_provider = provider

    def _initialize_window(self):
        workbench = self.workbench
        extensions = workbench.get_extensions(WINDOW_POINT)
        if not extensions:
            msg = "Cannot create a StudioWindow instance. No plugin "\
                  "contributed a factory to the '%s' extension point."
            raise RuntimeError(msg % WINDOW_POINT)
        extension = highest_ranked(extensions)
        factory = workbench.create_extension_object(extension)
        if not isinstance(factory, WindowFactory):
            msg = "extension '%s' created non-WindowFactory type '%s'"
            raise TypeError(msg % (extension.cls, type(factory).__name__))
        self._window = factory(window_model=self._model)

    def _destroy_window(self):
        self._window.hide()
        self._window.destroy()
        self._window = None

    def _destroy_model(self):
        self._model = None

    def _destroy_application(self):
        self._application.stop()
        self._application = None
