#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import ForwardTyped, List, Typed

from enaml.application import Application
from enaml.icon import Icon, IconImage
from enaml.image import Image
from enaml.workbench.extension import Extension
from enaml.workbench.plugin import Plugin

from .content_provider import ContentProvider
from .icon_provider import IconProvider
from .menu_provider import MenuProvider
from .title_provider import TitleProvider
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
    import enaml
    with enaml.imports():
        from enaml.studio.ui.studio_window import StudioWindow
    return StudioWindow


def load_icon(workbench, extension):
    """ Load an icon from an extension object.

    Parameters
    ----------
    workbench : Workbench
        The workbench for which the icon is being loaded.

    extension : Extension
        The extension which declares the icon in its config.

    Returns
    -------
    result : Icon or None
        The loaded Icon, or None if it could not be loaded.

    """
    url = extension.config.get(u'icon')
    if not url:
        return None

    manifest = workbench.get_manifest(extension.plugin_id)
    core = workbench.get_plugin(u'enaml.workbench.core')
    data = core.load_url(url, manifest.url)
    if data is None:
        return None

    image = Image(data=data)
    icon_image = IconImage(image=image)
    return Icon(images=[icon_image])


class UIPlugin(Plugin):
    """ The main UI plugin class for the Enaml studio.

    The ui plugin manages the extension points for user contributions
    to the main window.

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
        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method will hide and destroy the main window.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()
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
        point = workbench.get_extension_point(APPLICATION_POINT)
        extensions = point.extensions
        if not extensions:
            msg = "Cannot create an Application instance. No plugin "\
                  "contributed a factory to the '%s' extension point."
            raise RuntimeError(msg % APPLICATION_POINT)

        factory = workbench.create_extension_object(extensions[-1])
        if factory is None:
            raise RuntimeError('failed to load application factory')

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
        point = workbench.get_extension_point(WINDOW_POINT)
        extensions = point.extensions
        if not extensions:
            msg = "Cannot create a StudioWindow instance. No plugin "\
                  "contributed a factory to the '%s' extension point."
            raise RuntimeError(msg % WINDOW_POINT)

        factory = workbench.create_extension_object(extensions[-1])
        if factory is None:
            raise RuntimeError('failed to load window factory')

        self._window = factory(window_model=self._model)

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
        workbench = self.workbench
        point = workbench.get_extension_point(TITLE_POINT)
        extensions = point.extensions
        if not extensions:
            self._title_extension = None
            self._model.title_provider = TitleProvider()
            return

        extension = extensions[-1]
        if extension is self._title_extension:
            return

        if extension.cls:
            provider = workbench.create_extension_object(extension)
            if provider is None:
                provider = TitleProvider()
        else:
            title = extension.config.get(u'title', u'')
            provider = TitleProvider(title=title)

        self._title_extension = extension
        self._model.title_provider = provider

    def _refresh_icon(self):
        """ Refresh the icon provider for the window model.

        This method can be called to update the window model's icon
        provider to the current highest ranking extension. If the
        effective provider has not changed, this method is a no-op.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(ICON_POINT)
        extensions = point.extensions
        if not extensions:
            self._icon_extension = None
            self._model.icon_provider = IconProvider()
            return

        extension = extensions[-1]
        if extension is self._icon_extension:
            return

        if extension.cls:
            provider = workbench.create_extension_object(extension)
            if provider is None:
                provider = IconProvider()
        else:
            icon = load_icon(workbench, extension)
            provider = IconProvider(icon=icon)

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
        point = workbench.get_extension_point(MENUS_POINT)
        extensions = point.extensions
        if not extensions:
            self._menu_extensions = []
            self._model.menu_providers = []
            return

        # TODO more flexible menu ordering

        extensions = reversed(extensions)
        if extensions == self._menu_extensions:
            return

        new_pairs = []
        current = dict(zip(self._menu_extensions, self._model.menu_providers))
        for extension in extensions:
            if extension in current:
                new_pairs.append((extension, current[extension]))
                continue
            provider = workbench.create_extension_object(extension)
            if provider is None:
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
        point = workbench.get_extension_point(CONTENT_POINT)
        extensions = point.extensions
        if not extensions:
            self._content_extension = None
            self._model.content_provider = ContentProvider()
            return

        extension = extensions[-1]
        if extension is self._content_extension:
            return

        if extension.cls:
            provider = self.workbench.create_extension_object(extension)
            if provider is None:
                provider = ContentProvider()
        else:
            provider = ContentProvider()

        self._content_extension = extension
        self._model.content_provider = provider

    def _on_icon_updated(self, change):
        """ The observer for the icon extension point.

        """
        self._refresh_icon()

    def _on_title_updated(self, change):
        """ The observer for the title extension point.

        """
        self._refresh_title()

    def _on_menus_updated(self, change):
        """ The observer for the menus extension point.

        """
        self._refresh_menus()

    def _on_content_updated(self, change):
        """ The observer for the content extension point.

        """
        self._refresh_content()

    def _bind_observers(self):
        """ Install the registry event listeners for the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(ICON_POINT)
        point.updated.bind(self._on_icon_updated)

        point = workbench.get_extension_point(TITLE_POINT)
        point.updated.bind(self._on_title_updated)

        point = workbench.get_extension_point(MENUS_POINT)
        point.updated.bind(self._on_menus_updated)

        point = workbench.get_extension_point(CONTENT_POINT)
        point.updated.bind(self._on_content_updated)

    def _unbind_observers(self):
        """ Remove the registry event listeners installed by the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(ICON_POINT)
        point.updated.unbind(self._on_icon_updated)

        point = workbench.get_extension_point(TITLE_POINT)
        point.updated.unbind(self._on_title_updated)

        point = workbench.get_extension_point(MENUS_POINT)
        point.updated.unbind(self._on_menus_updated)

        point = workbench.get_extension_point(CONTENT_POINT)
        point.updated.unbind(self._on_content_updated)
