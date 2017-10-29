#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import str
from atom.api import (
    Enum, Bool, Callable, List, Unicode, Typed, ForwardTyped, Event
)

from enaml.application import deferred_call
from enaml.core.declarative import d_
from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyFileDialog(ProxyToolkitObject):
    """ The abstract definition of a proxy FileDialog object.

    """
    #: A reference to the FileDialog declaration.
    declaration = ForwardTyped(lambda: FileDialog)

    def open(self):
        raise NotImplementedError

    def exec_(self):
        raise NotImplementedError


class FileDialog(ToolkitObject):
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

    #: Whether to use a platform native dialog, when available. This
    #: attribute is deprecated and no longer has any effect. Native
    #: dialogs are always used when available in a given toolkit.
    native_dialog = d_(Bool(True))

    #: An enum indicating if the dialog was accepted or rejected by
    #: the user. It will be updated when the dialog is closed. This
    #: value is output only.
    result = Enum('rejected', 'accepted')

    #: An optional callback which will be invoked when the dialog is
    #: closed. This is a convenience to make it easier to handle a
    #: dialog opened in non-blocking mode. The callback must accept
    #: a single argument, which will be the dialog instance.
    callback = d_(Callable())

    #: An event fired if the dialog is accepted. The payload will be
    #: the selected path.
    accepted = d_(Event(str), writable=False)

    #: An event fired when the dialog is rejected. It has no payload.
    rejected = d_(Event(), writable=False)

    #: An event fired when the dialog is closed. It has no payload.
    closed = d_(Event(), writable=False)

    #: Whether to destroy the dialog widget on close. The default is
    #: True since dialogs are typically used in a transitory fashion.
    destroy_on_close = d_(Bool(True))

    #: A reference to the ProxyFileDialog object.
    proxy = Typed(ProxyFileDialog)

    def open(self):
        """ Open the dialog in a non-blocking fashion.

        This method will always return None. The state of the dialog
        will be updated when the dialog is closed by the user.

        """
        if not self.is_initialized:
            self.initialize()
        self.proxy.open()

    def exec_(self):
        """ Open the dialog in a blocking fashion.

        Returns
        -------
        result : unicode
            The path selected by the user, or an empty string if the
            dialog is cancelled.

        """
        if not self.is_initialized:
            self.initialize()
        self.proxy.exec_()
        if self.result == 'accepted':
            return self.path
        return u''

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def _handle_close(self, result, paths, selected_filter):
        """ Called by the proxy object when the dialog is closed.

        Parameters
        ----------
        result : string
            The result of the dialog; either 'accepted' or 'rejected'.

        paths : list
            The list of user selected paths. If the result is 'rejected'
            this should be an empty list.

        selected_filter : unicode
            The user selected name filter. If the result is 'rejected'
            this should be an empty string.

        """
        self.result = result
        if result == 'accepted':
            self.paths = paths
            self.path = paths[0] if paths else u''
            self.selected_filter = selected_filter
            self.accepted(self.path)
        else:
            self.rejected()
        if self.callback:
            self.callback(self)
        self.closed()
        if self.destroy_on_close:
            deferred_call(self.destroy)
