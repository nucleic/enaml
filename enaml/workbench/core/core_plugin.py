#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
import warnings

from atom.api import Typed

from enaml.workbench.plugin import Plugin

from .command import Command


COMMANDS_POINT = u'enaml.workbench.core.commands'


class CorePlugin(Plugin):
    """ The core plugin for the Enaml workbench.

    """
    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._refresh_commands()
        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()

    def invoke_command(self, command_id, *args, **kwargs):
        """ Invoke the command object for the given command id.

        Parameters
        ----------
        command_id : unicode
            The unique identifier of the command to invoke.

        *args
            Additional positional arguments to pass to the handler.

        **kwargs
            Additional keyword arguments to pass to the handler.

        """
        if command_id not in self._commands:
            msg = "'%s' is not a registered command id"
            warnings.warn(msg % command_id)
            return

        command = self._commands[command_id]
        if command.handler is None:
            msg = "command '%s' does not declare and handler"
            warnings.warn(msg % command_id)

        command.handler(self.workbench, *args, **kwargs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The mapping of command id to ranking Command object.
    _commands = Typed(dict, ())

    #: The mapping of extension object to list of Command objects.
    _command_extensions = Typed(defaultdict, (list,))

    def _refresh_commands(self):
        """ Refresh the command objects for the plugin.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(COMMANDS_POINT)
        extensions = point.extensions
        if not extensions:
            self._commands.clear()
            self._command_extensions.clear()
            return

        # Extensions are already ordered by rank, so command overrides
        # will naturally follow the ranking order of the extensions.

        new_extensions = defaultdict(list)
        old_extensions = self._command_extensions
        for extension in extensions:
            if extension in old_extensions:
                commands = old_extensions[extension]
            else:
                commands = self._load_commands(extension)
            new_extensions[extension].extend(commands)

        commands = {}
        for extension in extensions:
            for command in new_extensions[extension]:
                commands[command.id] = command

        self._commands = commands
        self._command_extensions = new_extensions

    def _load_commands(self, extension):
        """ Load the command objects for the given extension.

        Parameters
        ----------
        extension : Extension
            The extension object of interest.

        Returns
        -------
        result : list
            The list of Command objects declared by the extension.

        """
        workbench = self.workbench
        commands = extension.get_children(Command)
        if extension.factory is not None:
            for item in extension.factory(workbench):
                if not isinstance(item, Command):
                    msg = "extension '%s' created non-Command of type '%s'"
                    args = (extension.qualified_id, type(item).__name__)
                    warnings.warn(msg % args)
                    continue
                commands.append(item)
        return commands

    def _on_commands_updated(self, change):
        """ The observer for the commands extension point.

        """
        self._refresh_commands()

    def _bind_observers(self):
        """ Setup the observers for the plugin.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(COMMANDS_POINT)
        point.observe('extensions', self._on_commands_updated)

    def _unbind_observers(self):
        """ Remove the observers for the plugin.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(COMMANDS_POINT)
        point.unobserve('extensions', self._on_commands_updated)
