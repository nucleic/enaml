#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Unicode, Typed, ForwardTyped, Event, Callable, observe
)

from enaml.application import deferred_call
from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyToolkitDialog(ProxyToolkitObject):
    """ The abstract definition of a proxy ToolkitDialog object.

    """
    #: A reference to the ToolkitDialog declaration.
    declaration = ForwardTyped(lambda: ToolkitDialog)

    def set_title(self, title):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def exec_(self):
        raise NotImplementedError

    def accept(self):
        raise NotImplementedError

    def reject(self):
        raise NotImplementedError


class ToolkitDialog(ToolkitObject):
    """ A base class for defining toolkit dialogs.

    A toolkit dialog is a dialog where the content is defined by the
    toolkit rather than the user. Customary examples would be a file
    dialog or a color selection dialog, where the implementation can
    often be a native operating system dialog.

    """
    #: The title of the dialog window.
    title = d_(Unicode())

    #: An optional callback which will be invoked when the dialog is
    #: closed. This is a convenience to make it easier to handle a
    #: dialog opened in non-blocking mode. The callback must accept
    #: a single argument, which will be the dialog instance.
    callback = d_(Callable())

    #: Whether to destroy the dialog widget on close. The default is
    #: True since dialogs are typically used in a transitory fashion.
    destroy_on_close = d_(Bool(True))

    #: An event fired if the dialog is accepted. It has no payload.
    accepted = d_(Event(), writable=False)

    #: An event fired when the dialog is rejected. It has no payload.
    rejected = d_(Event(), writable=False)

    #: An event fired when the dialog is finished. The payload is the
    #: boolean result of the dialog.
    finished = d_(Event(bool), writable=False)

    #: Whether or not the dialog was accepted by the user. It will be
    #: updated when the dialog is closed. This value is output only.
    result = Bool(False)

    #: A reference to the ProxyToolkitDialog object.
    proxy = Typed(ProxyToolkitDialog)

    def show(self):
        """ Open the dialog as a non modal dialog.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        self._prepare()
        self.proxy.show()

    def open(self):
        """ Open the dialog as a window modal dialog.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        self._prepare()
        self.proxy.open()

    def exec_(self):
        """ Open the dialog as an application modal dialog.

        Returns
        -------
        result : bool
            Whether or not the dialog was accepted.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        self._prepare()
        self.proxy.exec_()
        return self.result

    def accept(self):
        """ Accept the current state and close the dialog.

        """
        if self.proxy_is_active:
            self.proxy.accept()

    def reject(self):
        """ Reject the current state and close the dialog.

        """
        if self.proxy_is_active:
            self.proxy.reject()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(ToolkitDialog, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def _proxy_finished(self, result):
        """ Called by the proxy object when the dialog is finished.

        Parameters
        ----------
        result : bool
            Wether or not the dialog was accepted.

        """
        self.result = result
        self.finished(result)
        if result:
            self.accepted()
        else:
            self.rejected()
        if self.callback:
            self.callback(self)
        if self.destroy_on_close:
            deferred_call(self.destroy)

    def _prepare(self):
        """ Prepare the dialog to be shown.

        This method can be reimplemented by subclasses.

        """
        self.result = False
