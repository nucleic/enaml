#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import Typed

from enaml.workbench.plugin import Plugin

from .command import Command
from .execution_event import ExecutionEvent


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
        self._commands.clear()
        self._command_extensions.clear()

    def invoke_command(self, command_id, parameters={}, trigger=None):
        """ Invoke the command handler for the given command id.

        Parameters
        ----------
        command_id : unicode
            The unique identifier of the command to invoke.

        parameters : dict, optional
            The parameters to pass to the command handler.

        trigger : object, optional
            The object which triggered the command.

        Returns
        -------
        result : object
            The return value of the command handler.

        """
        if command_id not in self._commands:
            msg = "'%s' is not a registered command id"
            raise ValueError(msg % command_id)

        command = self._commands[command_id]

        event = ExecutionEvent()
        event.command = command
        event.workbench = self.workbench
        event.parameters = parameters  # copied on assignment
        event.trigger = trigger

        return command.handler(event)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: The mapping of command id to Command object.
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
                if command.id in commands:
                    msg = "command '%s' is already registered"
                    raise ValueError(msg % command.id)
                if command.handler is None:
                    msg = "command '%s' does not declare a handler"
                    raise ValueError(msg % command.id)
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
                    raise TypeError(msg % args)
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
