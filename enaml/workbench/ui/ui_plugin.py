#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import warnings

from atom.api import ForwardTyped, Typed

from enaml.application import Application
from enaml.workbench.extension import Extension
from enaml.workbench.plugin import Plugin

from .branding import Branding
from .window_model import WindowModel


APPLICATION_FACTORY_POINT = u'enaml.workbench.ui.application_factory'

BRANDING_POINT = u'enaml.workbench.ui.branding'

WINDOW_FACTORY_POINT = u'enaml.workbench.ui.window_factory'


def WorkbenchWindow():
    """ A lazy importer for the enaml WorkbenchWindow.

    """
    import enaml
    with enaml.imports():
        from enaml.workbench.ui.workbench_window import WorkbenchWindow
    return WorkbenchWindow


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
    _window = ForwardTyped(WorkbenchWindow)

    #: The view model object used to drive the window.
    _model = Typed(WindowModel)

    #: The currently activate branding extension object.
    _branding_extension = Typed(Extension)

    def _create_application(self):
        """ Create the Application object for the ui.

        This will load the highest ranking extension to the application
        factory extension point, and use it to create the instance.

        If an application object already exists, that application will
        be used instead of any defined by a factory, since there can be
        only one application per-process.

        """
        if Application.instance() is not None:
            self._application = Application.instance()
            return

        workbench = self.workbench
        point = workbench.get_extension_point(APPLICATION_FACTORY_POINT)
        extensions = point.extensions
        if not extensions:
            msg = "Cannot create an Application instance. No plugin "\
                  "contributed an extension to the '%s' extension point."
            raise RuntimeError(msg % APPLICATION_FACTORY_POINT)

        extension = extensions[-1]
        if extension.factory is None:
            msg = "Cannot create an Application instance. Extension "\
                  "'%s' does not declare an application factory."
            raise RuntimeError(msg % extension.qualified_id)

        application = extension.factory()
        if not isinstance(application, Application):
            msg = "extension '%s' created non-Application type '%s'"
            args = (extension.qualified_id, type(application).__name__)
            raise TypeError(msg % args)

        self._application = application

    def _create_model(self):
        """ Create and initialize the model which drives the window.

        """
        self._model = WindowModel()
        self._refresh_branding()

    def _create_window(self):
        """ Create the Window object for the studio.

        This will load the highest ranking extension to the window
        factory extension point, and use it to create the instance.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(WINDOW_FACTORY_POINT)
        extensions = point.extensions
        if not extensions:
            msg = "Cannot create a StudioWindow instance. No plugin "\
                  "contributed an extension to the '%s' extension point."
            raise RuntimeError(msg % WINDOW_FACTORY_POINT)

        extension = extensions[-1]
        if extension.factory is None:
            msg = "Cannot create a WorkbenchWindow instance. Extension "\
                  "'%s' does not declare a window factory."
            raise RuntimeError(msg % extension.qualified_id)

        window = extension.factory(workbench, window_model=self._model)
        if not isinstance(window, WorkbenchWindow()):
            msg = "extension '%s' created non-WorkbenchWindow type '%s'"
            args = (extension.qualified_id, type(window).__name__)
            raise TypeError(msg % args)

        self._window = window

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

    def _refresh_branding(self):
        """ Refresh the title provider for the window model.

        This method can be called to update the window model's title
        provider to the current highest ranking extension. If the
        effective provider has not changed, this method is a no-op.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(BRANDING_POINT)
        extensions = point.extensions
        if not extensions:
            self._branding_extension = None
            self._model.branding = Branding()
            return

        extension = extensions[-1]
        if extension is self._branding_extension:
            return

        if extension.factory:
            branding = extension.factory(workbench)
            if not isinstance(branding, Branding):
                msg = "extension '%s' created non-Branding type '%s'"
                args = (extension.qualified_id, type(branding).__name__)
                warnings.warn(msg % args)
                branding = None
        else:
            branding = extension.get_child(Branding, reverse=True)

        self._branding_extension = extension
        self._model.branding = branding or Branding()

    def _on_branding_updated(self, change):
        """ The observer for the title extension point.

        """
        self._refresh_branding()

    def _bind_observers(self):
        """ Install the registry event listeners for the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(BRANDING_POINT)
        point.observe('extensions', self._on_branding_updated)

    def _unbind_observers(self):
        """ Remove the registry event listeners installed by the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(BRANDING_POINT)
        point.unobserve('extensions', self._on_branding_updated)
