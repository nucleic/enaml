#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Event, Typed, ForwardTyped, set_default

from enaml.core.declarative import d_

from .window import Window, ProxyWindow


class ProxyDialog(ProxyWindow):
    """ The abstract definition of a proxy Dialog object.

    """
    #: A reference to the Dialog declaration.
    declaration = ForwardTyped(lambda: Dialog)

    def done(self, accept):
        raise NotImplementedError

    def exec_(self):
        raise NotImplementedError


class Dialog(Window):
    """ A top-level Window class for creating dialogs.

    """
    #: The result of the dialog.
    result = d_(Bool(False), writable=False)

    #: An event fired when the dialog is finished. The payload will be
    #: the boolean result of the dialog.
    finished = d_(Event(bool), writable=False)

    #: An event fired when the dialog is accepted.
    accepted = d_(Event(), writable=False)

    #: An event fired when the dialog is rejected.
    rejected = d_(Event(), writable=False)

    #: Dialogs are application modal by default.
    modality = set_default('application_modal')

    #: A reference to the ProxyDialog object.
    proxy = Typed(ProxyDialog)

    def done(self, accept):
        """ Close the dialog and set the result value.

        This will cause a call to 'exec_' to return.

        Parameters
        ----------
        accept : bool
            Wether to accept or reject the dialog.

        """
        if self.proxy_is_active:
            self.proxy.done(accept)

    def accept(self):
        """ Close the dialog and set the result to True.

        """
        self.done(True)

    def reject(self):
        """ Close the dialog and set the result to False.

        """
        self.done(False)

    def exec_(self):
        """ Launch the dialog as a modal window.

        Returns
        -------
        result : bool
            The result value of the dialog.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        return self.proxy.exec_()
