#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Unicode, Enum, Bool, Event, Coerced, Typed, ForwardTyped, observe,
    set_default
)

from enaml.core.declarative import d_
from enaml.icon import Icon
from enaml.layout.geometry import Size

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyWindow(ProxyWidget):
    """ The abstract definition of a proxy Window object.

    """
    #: A reference to the Window declaration.
    declaration = ForwardTyped(lambda: Window)

    def create_if_needed(self):
        raise NotImplementedError

    def set_title(self, title):
        raise NotImplementedError

    def set_modality(self, modality):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def minimize(self):
        raise NotImplementedError

    def maximize(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


class Window(Widget):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is dubbed the 'central widget'. The central widget is an instance
    of Container and is expanded to fit the size of the window.

    A Window does not support features like MenuBars or DockPanes, for
    such functionality, use a MainWindow widget.

    """
    #: The titlebar text.
    title = d_(Unicode())

    #: The initial size of the window. A value of (-1, -1) indicates
    #: to let the toolkit choose the initial size.
    initial_size = d_(Coerced(Size, Size(-1, -1)))

    #: An enum which indicates the modality of the window. The default
    #: value is 'non_modal'.
    modality = d_(Enum('non_modal', 'application_modal', 'window_modal'))

    #: If this value is set to True, the window will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = d_(Bool(True))

    #: The title bar icon.
    icon = d_(Typed(Icon))

    #: An event fired when the window is closed. This event is triggered
    #: by the proxy object when the window is closed.
    closed = Event()

    #: Windows are invisible by default.
    visible = set_default(False)

    #: A reference to the ProxyWindow object.
    proxy = Typed(ProxyWindow)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def central_widget(self):
        """ Get the central widget defined on the window.

        The last `Container` child of the window is the central widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    def close(self):
        """ Send the 'close' action to the client widget.

        """
        self.proxy.close()

    def maximize(self):
        """ Send the 'maximize' action to the client widget.

        """
        self.proxy.maximize()

    def minimize(self):
        """ Send the 'minimize' action to the client widget.

        """
        self.proxy.minimize()

    def restore(self):
        """ Send the 'restore' action to the client widget.

        """
        self.proxy.restore()

    def show(self):
        """ Show the window to the screen.

        This will create the underlying toolkit window as-needed.

        """
        if not self.is_initialized:
            self.initialize()
        self.proxy.create_if_needed()
        self.visible = True

    def hide(self):
        """ Hide the window from the screen.

        """
        self.visible = False

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('title', 'modality', 'icon'))
    def _update_proxy(self, change):
        """ Update the ProxyWindow when the Window data changes.

        """
        # The superclass handler implementation is sufficient.
        super(Window, self)._update_proxy(change)
