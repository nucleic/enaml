#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .action import Action
from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyActionGroup(ProxyToolkitObject):
    """ The abstract definition of a proxy ActionGroup object.

    """
    #: A reference to the ActionGroup declaration.
    declaration = ForwardTyped(lambda: ActionGroup)

    def set_exclusive(self, exclusive):
        raise NotImplementedError

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_visible(self, visible):
        raise NotImplementedError


class ActionGroup(ToolkitObject):
    """ A non visible widget used to group actions.

    An action group can be used in a MenuBar or a ToolBar to group a
    related set of Actions and apply common operations to the set. The
    primary use of an action group is to make any checkable actions in
    the group mutually exclusive.

    """
    #: Whether or not the actions in this group are exclusive.
    exclusive = d_(Bool(True))

    #: Whether or not the actions in this group are enabled.
    enabled = d_(Bool(True))

    #: Whether or not the actions in this group are visible.
    visible = d_(Bool(True))

    #: A reference to the ProxyActionGroup object.
    proxy = Typed(ProxyActionGroup)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def actions(self):
        """ Get Actions defined as children of the ActionGroup.

        """
        return [child for child in self.children if isinstance(child, Action)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('exclusive', 'enabled', 'visible')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the group changes.

        """
        # The superclass implementation is sufficient.
        super(ActionGroup, self)._update_proxy(change)
