#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Enum, Bool, Callable, List, Unicode, Typed, ForwardTyped, Event
)

from enaml.application import deferred_call
from enaml.core.declarative import d_
from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyFileDialog(ProxyToolkitObject):
    """ The abstract defintion of a proxy FileDialog object.

    """
    #: A reference to the FileDialog declaration.
    declaration = ForwardTyped(lambda: FileDialog)

    def open(self):
        raise NotImplementedError

    def exec_(self):
        raise NotImplementedError

    def accept(self):
        raise NotImplementedError

    def reject(self):
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

    #: Whether to use a platform native dialog, when available.
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
    accepted = Event(unicode)

    #: An event fired when the dialog is rejected.
    rejected = Event(unicode)

    #: An event fired when the dialog is closed. This is deprecated,
    #: use 'accepted' or 'rejected' intead.
    closed = Event()

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
        if not self.parent:
            raise ValueError('FileDialog cannot be opened without a parent')
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

    def accept(self):
        """ Close the dialog, accepting the current selection.

        """
        if self.is_initialized:
            self.proxy.accept()

    def reject(self):
        """ Close the dialog, rejecting the current selection.

        """
        if self.is_initialized:
            self.proxy.reject()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def _handle_close(self):
        """ Called by the proxy object when the dialog is closed.

        The proxy should first update the dialog state, then call this
        method to fire off the appropriate closed events. If the dialog
        is set to destroy on the close, the call to destroy will occur
        on the next cycle of the event loop.

        """
        if self.callback:
            self.callback(self)
        if self.result == 'accepted':
            self.accepted(self.path)
        else:
            self.rejected()
        self.closed()
        if self.destroy_on_close:
            deferred_call(self.destroy)
