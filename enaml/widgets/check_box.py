#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, set_default

from .abstract_button import AbstractButton, ProxyAbstractButton


class ProxyCheckBox(ProxyAbstractButton):
    """ The abstract definition of a proxy PushButton object.

    """
    #: A reference to the CheckBox declaration.
    declaration = ForwardTyped(lambda: CheckBox)


class CheckBox(AbstractButton):
    """ An checkable button represented by a standard check box widget.

    Use a check box when it's necessary to toggle a boolean value
    independent of any other widgets in a group.

    When its necessary to allow the toggling of only one value in a
    group of values, use a group of RadioButtons or the RadioGroup
    control from the Enaml standard library.

    The interface for AbstractButton fully defines the interface for
    a CheckBox.

    """
    #: Check boxes are checkable by default.
    checkable = set_default(True)

    #: A reference to the ProxyPushButton object.
    proxy = Typed(ProxyCheckBox)
