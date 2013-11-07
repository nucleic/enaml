#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .abstract_button import AbstractButton, ProxyAbstractButton
from .menu import Menu


class ProxyPushButton(ProxyAbstractButton):
    """ The abstract definition of a proxy PushButton object.

    """
    #: A reference to the PushButton declaration.
    declaration = ForwardTyped(lambda: PushButton)

    def set_default(self, default):
        raise NotImplementedError


class PushButton(AbstractButton):
    """ A button control represented by a standard push button widget.

    """
    #: Whether this button is the default action button in a dialog.
    default = d_(Bool(False))

    #: A reference to the ProxyPushButton object.
    proxy = Typed(ProxyPushButton)

    def menu(self):
        """ Get the menu defined for the PushButton, if any.

        """
        for child in reversed(self.children):
            if isinstance(child, Menu):
                return child

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('default')
    def _update_proxy(self, change):
        """ Send the member state change to the proxy.

        """
        # The superclass implementation is sufficient
        super(PushButton, self)._update_proxy(change)
