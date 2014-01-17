#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Event, ForwardTyped, Unicode

from .extension_point import ExtensionPointEvent


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


class Plugin(Atom):
    """ A base class for defining workbench plugins.

    This class provides the base life-cycle api required of workbench
    plugins. User code should subclass this class and implement the
    various life-cycle methods as needed.

    Subclasses may declare ExtensionPoint instances in their body to
    define the points to which other plugins may contribute extensions.
    A plugin can `observe` the extension points in order to be notified
    when the contributed extensions change. An observer will be passed
    a change dict with type 'extension-point' and 'value' which is an
    ExtensionPointEvent instance.

    """
    #: A reference to the workbench instance which manages the plugin.
    #: This is assigned when the plugin is added to the workbench. It
    #: should not be manipulated by user code.
    workbench = ForwardTyped(Workbench)

    #: A globally unique identifier for the plugin. This is typically
    #: provided in the form: 'mypackage.mymodule.myplugin'.
    identifier = Unicode()

    #: A human-readable name for the plugin. This need not be unique.
    name = Unicode()

    #: An event which should be fired by user code when the extensions
    #: contributed by this plugin to extensions points change. Firing
    #: this event will only have an effect after the plugin is added
    #: to the workbench and 'get_extensions' is called.
    extensions_changed = Event(ExtensionPointEvent)

    def get_extensions(self):
        """ Get the extensions contributed by this plugin.

        This method is called when the plugin is added to a workbench.

        The default implementation of this method returns an empty dict
        and can be safetly ignored by subclasses which do not contribute
        any extensions to other plugins.

        This method should never be called by user code.

        Returns
        -------
        result : dict
            A dict which maps extension point id to list of extension
            objects. The extensions can be of any type allowed by the
            specified extension point.

        """
        return {}

    def initialize(self):
        """ Invoked when the plugin is added to the workbench.

        This method is called when the plugin is added to a workbench,
        before the workbench queries the plugin for its extensions. A
        plugin may reimplement this method if, for example, it wishes
        to lazily import its extensions, or install other plugins.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass

    def start(self):
        """ Start the life-cycle of the plugin.

        This method will be called once by the workbench during the
        lifetime of the plugin. It is guaranteed to be called after
        the 'initialize' method has been invoked.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass

    def stop(self):
        """ Stop the life-cycle of the plugin.

        This method will be called once by the workbench at the end of
        the plugin's lifetime.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass

    def destroy(self):
        """ Invoked when a plugin is removed from the workbench.

        This method will be called when the plugin is removed from
        the workbench. The plugin should release any resources it
        acquired during its lifetime. After this method returns the
        plugin should be considered invalid and no longer used.

        Before this method is called, the plugin's extensions and
        extension points will be unloaded and removed.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        This method should never be called by user code.

        """
        pass
