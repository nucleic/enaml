#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .abstract_button import AbstractButton, ProxyAbstractButton
from .menu import Menu


class ProxyPushButton(ProxyAbstractButton):
    """ The abstract definition of a proxy PushButton object.

    """
    #: A reference to the PushButton declaration.
    declaration = ForwardTyped(lambda: PushButton)


class PushButton(AbstractButton):
    """ A button control represented by a standard push button widget.

    """
    #: A reference to the ProxyPushButton object.
    proxy = Typed(ProxyPushButton)

    def menu(self):
        """ Get the menu defined for the PushButton, if any.

        """
        for child in reversed(self.children):
            if isinstance(child, Menu):
                return child
