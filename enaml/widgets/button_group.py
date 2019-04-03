from atom.api import Bool, ForwardTyped, Typed, observe

from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyButtonGroup(ProxyToolkitObject):
    declaration = ForwardTyped(lambda: ButtonGroup)

    def set_exclusive(self, exclusive):
        raise NotImplementedError

    def add_button(self, button):
        raise NotImplementedError

    def remove_button(self, button):
        raise NotImplementedError


class ButtonGroup(ToolkitObject):
    exclusive = d_(Bool(True))

    proxy = Typed(ProxyButtonGroup)

    @observe("exclusive")
    def _update_proxy(self, change):
        super(ButtonGroup, self)._update_proxy(change)

    def add_button(self, button):
        if self.proxy_is_active:
            self.proxy.add_button(button)

    def remove_button(self, button):
        if self.proxy_is_active:
            self.proxy.remove_button(button)
