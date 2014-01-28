#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import warnings

from atom.api import ForwardTyped, List, Typed, atomref

import enaml
from enaml.application import Application
from enaml.workbench.api import Plugin, Extension

from .application_factory import ApplicationFactory
from .content_provider import ContentProvider
from .icon_provider import IconProvider
from .menu_provider import MenuProvider
from .refresh_listener import RefreshListener
from .title_provider import TitleProvider
from .utils import highest_ranked, rank_sort
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
    def start(self):
        """ Start the plugin life-cycle.

        This method will initialize the main window, but not show it.
        The Studio instance is responsible for showing the window after
        this plugin is started.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._create_application()
        self._create_model()
        self._create_window()
        self._install_listeners()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method will hide and destroy the main window.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._remove_listeners()
        self._destroy_window()
        self._release_model()
        self._release_application()

    def show_window(self):
        """ Ensure the underlying window object is shown.

        """
        self._window.show()

    def hide_window(self):
        """ Ensure the underlying window object is hidden.

        """
        self._window.hide()

    def start_application(self):
        """ Start the event loop of the underlying application.

        """
        self._application.start()

    def stop_application(self):
        """ Stop the event loop of the underlying application.

        """
        self._application.stop()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The application provided by an ApplicationFactory extension.
    _application = Typed(Application)

    #: The window object provided by a WindowFactory extension.
    _window = ForwardTyped(StudioWindow)

    #: The view model object used to drive the window.
    _model = Typed(WindowModel)

    #: The currently active title extension.
    _title_extension = Typed(Extension)

    #: The currently active icon extension.
    _icon_extension = Typed(Extension)

    #: The currently active menu extensions.
    _menu_extensions = List(Extension)

    #: A currently active content extension.
    _content_extension = Typed(Extension)

    #: The registry listeners installed for the for plugin.
    _registry_listeners = List()

    def _create_application(self):
        """ Create the Application object for the studio.

        This will load the ApplicationFactory for the highest ranking
        extension to the application extension point, and use that
        factory to create the Application instance for the ui.

        If an application object already exists, that application will
        be used instead of any defined by a factory, since there can be
        only one application per-process.

        """
        if Application.instance() is not None:
            self._application = Application.instance()
            return

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

    def _create_model(self):
        """ Create and initialize the model which drives the window.

        """
        self._model = WindowModel()
        self._refresh_title()
        self._refresh_icon()
        self._refresh_menus()
        self._refresh_content()

    def _create_window(self):
        """ Create the Window object for the studio.

        This method will load the WindowFactory for the highest ranking
        extension to the window extension point, and use that factory
        to create the StudioWindow instance for the ui.

        """
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

    def _install_listeners(self):
        """ Install the registry event listeners for the plugin.

        """
        listeners = []
        ref = atomref(self)
        workbench = self.workbench
        pairs = ((CONTENT_POINT, '_refresh_content'),
                 (ICON_POINT, '_refresh_icon'),
                 (MENUS_POINT, '_refresh_menus'),
                 (TITLE_POINT, '_refresh_title'))

        for point, name in pairs:
            listener = RefreshListener(plugin_ref=ref, method_name=name)
            workbench.add_listener(point, listener)
            listeners.append((point, listener))

        self._registry_listeners = listeners

    def _remove_listeners(self):
        """ Remove the registry event listeners installed by the plugin.

        """
        workbench = self.workbench
        for point, listener in self._registry_listeners:
            workbench.remove_listener(point, listener)
        self._registry_listeners = []

    def _destroy_window(self):
        """ Destroy and release the underlying window object.

        """
        self._window.hide()
        self._window.destroy()
        self._window = None

    def _release_model(self):
        """ Release the underlying window model object.

        """
        self._model = None

    def _release_application(self):
        """ Stop and release the underlyling application object.

        """
        self._application.stop()
        self._application = None

    def _refresh_title(self):
        """ Refresh the title provider for the window model.

        This method can be called to update the window model's title
        provider to the current highest ranking extension. If the
        effective provider has not changed, this method is a no-op.

        """
        extensions = self.workbench.get_extensions(TITLE_POINT)
        if not extensions:
            self._title_extension = None
            self._model.title_provider = TitleProvider()
            return

        extension = highest_ranked(extensions)
        if extension is self._title_extension:
            return

        if extension.cls:
            provider = self.workbench.create_extension_object(extension)
            if not isinstance(provider, TitleProvider):
                msg = "extension '%s' created non-TitleProvider type '%s'"
                warnings.warn(msg % (extension.cls, type(provider).__name__))
                provider = TitleProvider()
        else:
            title = extension.get_property(u'title', u'')
            provider = TitleProvider(title=title)

        self._title_extension = extension
        self._model.title_provider = provider

    def _refresh_icon(self):
        """ Refresh the icon provider for the window model.

        This method can be called to update the window model's icon
        provider to the current highest ranking extension. If the
        effective provider has not changed, this method is a no-op.

        """
        extensions = self.workbench.get_extensions(ICON_POINT)
        if not extensions:
            self._icon_extension = None
            self._model.icon_provider = IconProvider()
            return

        extension = highest_ranked(extensions)
        if extension is self._icon_extension:
            return

        if extension.cls:
            provider = self.workbench.create_extension_object(extension)
            if not isinstance(provider, IconProvider):
                msg = "extension '%s' created non-IconProvider type '%s'"
                warnings.warn(msg % (extension.cls, type(provider).__name__))
                provider = IconProvider()
        elif extension.has_property(u'icon'):
            uri = extension.get_property(u'icon')
            core = self.workbench.get_plugin(u'enaml.studio.core')
            icon = core.load_resource(u'icon', uri)
            provider = IconProvider(icon=icon)
        else:
            provider = IconProvider()

        self._icon_extension = extension
        self._model.icon_provider = provider

    def _refresh_menus(self):
        """ Refresh the menu providers for the window model.

        This method can be called to update the window model's menu
        providers to the current rank sorted extensions. This method
        will only create the extension objects for the providers which
        have changed.

        """
        workbench = self.workbench
        extensions = workbench.get_extensions(MENUS_POINT)
        if not extensions:
            self._menu_extensions = []
            self._model.menu_providers = []
            return

        extensions = rank_sort(extensions, reverse=True)
        if extensions == self._menu_extensions:
            return

        current = dict(zip(self._menu_extensions, self._model.menu_providers))
        new_pairs = []
        for extension in extensions:
            if extension in current:
                new_pairs.append((extension, current[extension]))
                continue
            provider = workbench.create_extension_object(extension)
            if not isinstance(provider, MenuProvider):
                msg = "extension '%s' created non-MenuProvider type '%s'"
                warnings.warn(msg % (extension.cls, type(provider).__name__))
                provider = MenuProvider()
            new_pairs.append((extension, provider))

        exts, providers = zip(*new_pairs)
        self._menu_extensions = list(exts)
        self._model.menu_providers = list(providers)

    def _refresh_content(self):
        """ Refresh the content provider for the window model.

        This method can be called to update the window model's content
        provider to the current highest ranking extension. If the
        effective provider has not changed, this method is a no-op.

        """
        workbench = self.workbench
        extensions = workbench.get_extensions(CONTENT_POINT)
        if not extensions:
            self._content_extension = None
            self._model.content_provider = ContentProvider()
            return

        extension = highest_ranked(extensions)
        if extension is self._content_extension:
            return

        if extension.cls:
            provider = self.workbench.create_extension_object(extension)
            if not isinstance(provider, ContentProvider):
                msg = "extension '%s' created non-ContentProvider type '%s'"
                warnings.warn(msg % (extension.cls, type(provider).__name__))
                provider = ContentProvider()
        else:
            provider = ContentProvider()

        self._content_extension = extension
        self._model.content_provider = provider
