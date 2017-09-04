#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import unicode_literals

from atom.api import Typed

from enaml.application import Application
from enaml.workbench.extension import Extension
from enaml.workbench.plugin import Plugin

from .action_item import ActionItem
from .autostart import Autostart
from .branding import Branding
from .menu_helper import create_menus
from .menu_item import MenuItem
from .window_model import WindowModel
from .workspace import Workspace

import enaml
with enaml.imports():
    from .workbench_window import WorkbenchWindow


ACTIONS_POINT = u'enaml.workbench.ui.actions'

APPLICATION_FACTORY_POINT = u'enaml.workbench.ui.application_factory'

BRANDING_POINT = u'enaml.workbench.ui.branding'

WINDOW_FACTORY_POINT = u'enaml.workbench.ui.window_factory'

WORKSPACES_POINT = u'enaml.workbench.ui.workspaces'

AUTOSTART_POINT = u'enaml.workbench.ui.autostart'


class UIPlugin(Plugin):
    """ The main UI plugin class for the Enaml studio.

    The ui plugin manages the extension points for user contributions
    to the main window.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._create_application()
        self._create_model()
        self._create_window()
        self._bind_observers()
        self._start_autostarts()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._stop_autostarts()
        self._unbind_observers()
        self._destroy_window()
        self._release_model()
        self._release_application()

    @property
    def window(self):
        """ Get a reference to the primary window.

        """
        return self._window

    @property
    def workspace(self):
        """ Get a reference to the currently active workspace.

        """
        return self._model.workspace

    def show_window(self):
        """ Ensure the underlying window object is shown.

        """
        self._window.show()

    def hide_window(self):
        """ Ensure the underlying window object is hidden.

        """
        self._window.hide()

    def start_application(self):
        """ Start the application event loop.

        """
        self._application.start()

    def stop_application(self):
        """ Stop the application event loop.

        """
        self._application.stop()

    def close_window(self):
        """ Close the underlying workbench window.

        """
        self._window.close()

    def close_workspace(self):
        """ Close and dispose of the currently active workspace.

        """
        self._workspace_extension = None
        self._model.workspace.stop()
        self._model.workspace.workbench = None
        self._model.workspace = Workspace()

    def select_workspace(self, extension_id):
        """ Select and start the workspace for the given extension id.

        The current workspace will be stopped and released.

        """
        target = None
        workbench = self.workbench
        point = workbench.get_extension_point(WORKSPACES_POINT)
        for extension in point.extensions:
            if extension.qualified_id == extension_id:
                target = extension
                break

        if target is None:
            msg = "'%s' is not a registered workspace extension"
            raise ValueError(msg % extension_id)

        if target is self._workspace_extension:
            return

        old_workspace = self._model.workspace
        old_workspace.stop()
        old_workspace.workbench = None

        self._workspace_extension = target
        new_workspace = self._create_workspace(target)

        new_workspace.workbench = workbench
        new_workspace.start()
        self._model.workspace = new_workspace

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The application provided by an ApplicationFactory extension.
    _application = Typed(Application)

    #: The window object provided by a WindowFactory extension.
    _window = Typed(WorkbenchWindow)

    #: The view model object used to drive the window.
    _model = Typed(WindowModel)

    #: The currently activate branding extension object.
    _branding_extension = Typed(Extension)

    #: The currently activate workspace extension object.
    _workspace_extension = Typed(Extension)

    #: The currently active action extension objects.
    _action_extensions = Typed(dict, ())

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
            msg = "no contributions to the '%s' extension point"
            raise RuntimeError(msg % APPLICATION_FACTORY_POINT)

        extension = extensions[-1]
        if extension.factory is None:
            msg = "extension '%s' does not declare an application factory"
            raise ValueError(msg % extension.qualified_id)

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
        self._refresh_actions()

    def _create_window(self):
        """ Create the WorkbenchWindow object for the workbench.

        This will load the highest ranking extension to the window
        factory extension point, and use it to create the instance.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(WINDOW_FACTORY_POINT)
        extensions = point.extensions
        if not extensions:
            msg = "no contributions to the '%s' extension point"
            raise RuntimeError(msg % WINDOW_FACTORY_POINT)

        extension = extensions[-1]
        if extension.factory is None:
            msg = "extension '%s' does not declare a window factory"
            raise ValueError(msg % extension.qualified_id)

        window = extension.factory(workbench)
        if not isinstance(window, WorkbenchWindow):
            msg = "extension '%s' created non-WorkbenchWindow type '%s'"
            args = (extension.qualified_id, type(window).__name__)
            raise TypeError(msg % args)

        window.workbench = workbench
        window.window_model = self._model
        self._window = window

    def _create_workspace(self, extension):
        """ Create the Workspace object for the given extension.

        Parameters
        ----------
        extension : Extension
            The extension object of interest.

        Returns
        -------
        result : Workspace
            The workspace object for the given extension.

        """
        if extension.factory is None:
            msg = "extension '%s' does not declare a workspace factory"
            raise ValueError(msg % extension.qualified_id)

        workspace = extension.factory(self.workbench)
        if not isinstance(workspace, Workspace):
            msg = "extension '%s' created non-Workspace type '%s'"
            args = (extension.qualified_id, type(workspace).__name__)
            raise TypeError(msg % args)

        return workspace

    def _create_action_items(self, extension):
        """ Create the action items for the extension.

        """
        workbench = self.workbench
        menu_items = extension.get_children(MenuItem)
        action_items = extension.get_children(ActionItem)
        if extension.factory:
            for item in extension.factory(workbench):
                if isinstance(item, MenuItem):
                    menu_items.append(item)
                elif isinstance(item, ActionItem):
                    action_items.append(item)
                else:
                    msg = "action extension created invalid action type '%s'"
                    raise TypeError(msg % type(item).__name__)
        return menu_items, action_items

    def _destroy_window(self):
        """ Destroy and release the underlying window object.

        """
        self._window.hide()
        self._window.destroy()
        self._window = None

    def _release_model(self):
        """ Release the underlying window model object.

        """
        self._model.workspace.stop()
        self._model = None

    def _release_application(self):
        """ Stop and release the underlyling application object.

        """
        self._application.stop()
        self._application = None

    def _refresh_branding(self):
        """ Refresh the branding object for the window model.

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
                raise TypeError(msg % args)
        else:
            branding = extension.get_child(Branding, reverse=True)
            branding = branding or Branding()

        self._branding_extension = extension
        self._model.branding = branding

    def _refresh_actions(self):
        """ Refresh the actions for the workbench window.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(ACTIONS_POINT)
        extensions = point.extensions
        if not extensions:
            self._action_extensions.clear()
            self._model.menus = []
            return

        menu_items = []
        action_items = []
        new_extensions = {}
        old_extensions = self._action_extensions
        for extension in extensions:
            if extension in old_extensions:
                m_items, a_items = old_extensions[extension]
            else:
                m_items, a_items = self._create_action_items(extension)
            new_extensions[extension] = (m_items, a_items)
            menu_items.extend(m_items)
            action_items.extend(a_items)

        menus = create_menus(workbench, menu_items, action_items)
        self._action_extensions = new_extensions
        self._model.menus = menus

    def _get_autostarts(self):
        """ Get the autostart extension objects.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(AUTOSTART_POINT)
        extensions = sorted(point.extensions, key=lambda ext: ext.rank)

        autostarts = []
        for extension in extensions:
            autostarts.extend(extension.get_children(Autostart))

        return autostarts

    def _start_autostarts(self):
        """ Start the plugins for the autostart extension point.

        """
        workbench = self.workbench
        for autostart in self._get_autostarts():
            workbench.get_plugin(autostart.plugin_id)

    def _stop_autostarts(self):
        """ Stop the plugins for the autostart extension point.

        """
        workbench = self.workbench
        for autostart in reversed(self._get_autostarts()):
            plugin = workbench.get_plugin(autostart.plugin_id)
            plugin.stop()

    def _on_branding_updated(self, change):
        """ The observer for the branding extension point.

        """
        self._refresh_branding()

    def _on_actions_updated(self, change):
        """ The observer for the actions extension point.

        """
        self._refresh_actions()

    def _bind_observers(self):
        """ Setup the observers for the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(BRANDING_POINT)
        point.observe('extensions', self._on_branding_updated)

        point = workbench.get_extension_point(ACTIONS_POINT)
        point.observe('extensions', self._on_actions_updated)

    def _unbind_observers(self):
        """ Remove the observers for the plugin.

        """
        workbench = self.workbench

        point = workbench.get_extension_point(BRANDING_POINT)
        point.unobserve('extensions', self._on_branding_updated)

        point = workbench.get_extension_point(ACTIONS_POINT)
        point.unobserve('extensions', self._on_actions_updated)
