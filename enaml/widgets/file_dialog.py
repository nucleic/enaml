#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Bool, Callable, List, Unicode, Event

from enaml.application import deferred_call
from enaml.core.declarative import Declarative, d_
from enaml.core.messenger import Messenger


class FileDialog(Messenger, Declarative):
    """ A dialog widget that allows the user to open and save files and
    directories.

    """
    #: The title to use for the dialog.
    title = d_(Unicode())

    #: The mode of the dialog.
    mode = d_(Enum('open_file', 'open_files', 'save_file', 'directory'))

    #: The selected path in the dialog. This value will be used to set
    #: the initial working directory and file, as appropriate, when the
    #: dialog is opened. It will aslo be updated when the dialog is
    #: closed and accepted.
    path = d_(Unicode())

    #: The list of selected paths in the dialog. It will be updated
    #: when the dialog is closed and accepted. It is output only and
    #: is only applicable for the `open_files` mode.
    paths = List(Unicode())

    #: The string filters used to restrict the user's selections.
    filters = d_(List(Unicode()))

    #: The selected filter from the list of filters. This value will be
    #: used as the initial working filter when the dialog is opened. It
    #: will also be updated when the dialog is closed and accepted.
    selected_filter = d_(Unicode())

    #: Whether to use a platform native dialog, when available.
    native_dialog = d_(Bool(True))

    #: An enum indicating if the dialog was accepted or rejected by
    #: the user. It will be updated when the dialog is closed. This
    #: value is output only.
    result = Enum('rejected', 'accepted')

    #: An optional callback which will be invoked when the dialog is
    #: closed. This is a convenience to make it easier to handle the
    #: non-blocking behavior of the dialog. The callback must accept
    #: a single argument, which will be the dialog instance.
    callback = d_(Callable())

    #: An event fired when the dialog is closed. The dialog state will
    #: be updated before this event is fired.
    closed = Event()

    #: Whether to destroy the dialog widget on close. The default is
    #: True since dialogs are typically used in a transitory fashion.
    #: If this value is set to True, the dialog will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = d_(Bool(True))

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the dialog for user interaction.

        """
        if self.parent is None:
            raise ValueError('FileDialog cannot be opened without a parent.')
        content = {}
        content['title'] = self.title
        content['mode'] = self.mode
        content['path'] = self.path
        content['filters'] = self.filters
        content['selected_filter'] = self.selected_filter
        content['native_dialog'] = self.native_dialog
        # A common dialog idiom is as follows:
        #
        #    dlg = FileDialog(foo, ...)
        #    dlg.open()
        #
        # With this scenario, the dialog will not have been initialized
        # by the time the `open` method is called, since the child event
        # of the dialog parent is batched by the Messenger class. The
        # 'open' action must therefore be deferred in order to allow the
        # dialog be fully initialized and capable of sending messages.
        # Otherwise, the 'open' message will be dropped.
        if self.is_active:
            self.send_action('open', content)
        else:
            deferred_call(self.send_action, 'open', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.result = content['result']
        if self.result == 'accepted':
            paths = content['paths']
            self.paths = paths
            self.path = paths[0] if paths else u''
            self.selected_filter = content['selected_filter']
        if self.callback:
            self.callback(self)
        self.closed()
        if self.destroy_on_close:
            self.destroy()

