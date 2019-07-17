#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, ForwardTyped, Typed, observe

from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyButtonGroup(ProxyToolkitObject):
    """ The abstract defintion of a proxy ButtonGroup object.

    """
    #: A reference to the ButtonGroup declaration.
    declaration = ForwardTyped(lambda: ButtonGroup)

    def set_exclusive(self, exclusive):
        raise NotImplementedError

    def add_button(self, button):
        raise NotImplementedError

    def remove_button(self, button):
        raise NotImplementedError


class ButtonGroup(ToolkitObject):
    """ A way to declare a group of buttons.

    This allows to group buttons even though they beloing to different
    container.

    """

    #: Can only a single button in the group be checked at a time.
    exclusive = d_(Bool(True))

    #: A reference to the ProxyButtonGroup object.
    proxy = Typed(ProxyButtonGroup)

    @observe("exclusive")
    def _update_proxy(self, change):
        super(ButtonGroup, self)._update_proxy(change)

