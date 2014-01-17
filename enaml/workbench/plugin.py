#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Event, ForwardTyped, Unicode

from .extensionpoint import ExtensionPointEvent


def Workbench():
    """ A lazy forward import function for the Workbench type.

    """
    from .workbench import Workbench
    return Workbench


class Plugin(Atom):
    """ A base class for defining workbench plugins.

    This class provides the base life-cycle api required of workbench
    plugins. User code should subclass this class and implement the
    various methods and behaviors as needed.

    Subclasses should declare ExtensionPoint instances in their class
    body to define the points to which other plugins may contribute.
    A plugin (or other code) can `observe` the extension points to
    be notified when their extensions change. The observer will be
    passed a change dict with type 'extension-point' and a value
    which is an ExtensionPointEvent instance.

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
    #: provided by this plugin to another's extension points change.
    #: The 'added' and 'removed' values of the event will be used by
    #: the framework to update the relevant extension point. This
    #: event will only have an effect after the plugin is added to the
    #: workbench and after the first time 'get_extensions' is called.
    extensions_changed = Event(ExtensionPointEvent)

    def initialize(self):
        """ Start the life-cycle of the plugin.

        This method will be called by the once by the workbench during
        the lifetime of the plugin. It will occur after the workbench
        has querried for the plugin's extensions. This method should
        never be called directly by user code.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        """
        pass

    def dispose(self):
        """ Stop the life-cycle of the plugin.

        This method will be called by the once by the workbench during
        the lifetime of the plugin. It will occur after the workbench
        has removed the plugin and it's extensions. This method should
        never be called directly by user code.

        The default implementation of this method does nothing, and
        can be safetly ignored by subclasses which do not need it.

        """
        pass

    def get_extensions(self):
        """ Get the list of extensions contributed by this plugin.

        The default implementation of this method returns an empty
        list and can be safetly ignored by subclasses which do not
        contribute any extensions to other plugins.

        Returns
        -------
        result : list
            A list of Extension objects which contribute functionality
            to the extension points of other plugins.

        """
        return []
