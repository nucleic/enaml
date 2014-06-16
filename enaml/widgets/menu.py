#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, Unicode, observe

from enaml.core.declarative import d_

from .action import Action
from .action_group import ActionGroup
from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyMenu(ProxyToolkitObject):
    """ The abstract definition of a proxy Menu object.

    """
    #: A reference to the Menu declaration.
    declaration = ForwardTyped(lambda: Menu)

    def set_title(self, title):
        raise NotImplementedError

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_visible(self, visible):
        raise NotImplementedError

    def set_context_menu(self, context):
        raise NotImplementedError

    def popup(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class Menu(ToolkitObject):
    """ A widget used as a menu in a MenuBar.

    """
    #: The title to use for the menu.
    title = d_(Unicode())

    #: Whether or not the menu is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the menu is visible.
    visible = d_(Bool(True))

    #: Whether this menu should behave as a context menu for its parent.
    context_menu = d_(Bool(False))

    #: A reference to the ProxyMenu object.
    proxy = Typed(ProxyMenu)

    def items(self):
        """ Get the items defined on the Menu.

        A menu item is one of Action, ActionGroup, or Menu.

        """
        allowed = (Action, ActionGroup, Menu)
        return [c for c in self.children if isinstance(c, allowed)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title', 'enabled', 'visible', 'context_menu')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the menu changes.

        """
        # The superclass implementation is sufficient.
        super(Menu, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def popup(self):
        """ Popup the menu over the current mouse location.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        self.proxy.popup()

    def close(self):
        """ Close the menu.

        This API can be used by embedded widgets to close the menu
        at the appropriate time.

        """
        if self.proxy_is_active:
            self.proxy.close()
