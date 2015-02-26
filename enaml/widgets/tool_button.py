#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .abstract_button import AbstractButton, ProxyAbstractButton


class ProxyToolButton(ProxyAbstractButton):
    """ The abstract definition of a proxy ToolButton object.

    """
    #: A reference to the ToolButton declaration.
    declaration = ForwardTyped(lambda: ToolButton)

    def set_button_style(self, style):
        raise NotImplementedError

    def set_auto_raise(self, auto):
        raise NotImplementedError

    def set_popup_mode(self, mode):
        raise NotImplementedError


class ToolButton(AbstractButton):
    """ A widget for creating tool bar buttons.

    A ToolButton can be declared as the child of a ToolBar or used as
    a regular widget in a constraints layout. It supports an optional
    child Menu object which will open when the button is clicked
    according the specified popup mode.

    """
    #: The button style to apply to this tool button.
    button_style = d_(Enum(
        'icon_only', 'text_only', 'text_beside_icon', 'text_under_icon'
    ))

    #: Whether or not auto-raise is enabled for the button.
    auto_raise = d_(Bool(True))

    #: The mode for displaying a child popup menu.
    popup_mode = d_(Enum('delayed', 'button', 'instant'))

    #: A reference to the ProxyToolButton object.
    proxy = Typed(ProxyToolButton)

    @observe('button_style', 'auto_raise', 'popup_mode')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the ToolButton changes.

        """
        # The superclass implementation is sufficient
        super(ToolButton, self)._update_proxy(change)
