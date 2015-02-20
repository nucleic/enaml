#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Atom, Unicode, Enum, Bool, Event, Coerced, Typed, ForwardTyped, observe,
    set_default
)

from enaml.core.declarative import d_
from enaml.icon import Icon
from enaml.layout.geometry import Pos, Rect, Size

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyWindow(ProxyWidget):
    """ The abstract definition of a proxy Window object.

    """
    #: A reference to the Window declaration.
    declaration = ForwardTyped(lambda: Window)

    def set_title(self, title):
        raise NotImplementedError

    def set_modality(self, modality):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def position(self):
        raise NotImplementedError

    def set_position(self, pos):
        raise NotImplementedError

    def size(self):
        raise NotImplementedError

    def set_size(self, size):
        raise NotImplementedError

    def geometry(self):
        raise NotImplementedError

    def set_geometry(self, rect):
        raise NotImplementedError

    def frame_geometry(self):
        raise NotImplementedError

    def minimize(self):
        raise NotImplementedError

    def is_minimized(self):
        raise NotImplementedError

    def maximize(self):
        raise NotImplementedError

    def is_maximized(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError

    def send_to_front(self):
        raise NotImplementedError

    def send_to_back(self):
        raise NotImplementedError

    def activate_window(self):
        raise NotImplementedError

    def center_on_screen(self):
        raise NotImplementedError

    def center_on_widget(self, other):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class CloseEvent(Atom):
    """ An payload object carried by a window 'closing' event.

    User code can manipulate this object to veto a close event.

    """
    #: The internal accepted state.
    _accepted = Bool(True)

    def is_accepted(self):
        """ Get whether or not the event is accepted.

        Returns
        -------
        result : bool
            True if the event is accepted, False otherwise. The
            default is True.

        """
        return self._accepted

    def accept(self):
        """ Accept the close event and allow the window to be closed.

        """
        self._accepted = True

    def ignore(self):
        """ Reject the close event and prevent the window from closing.

        """
        self._accepted = False


class Window(Widget):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is dubbed the 'central widget'. The central widget is an instance
    of Container and is expanded to fit the size of the window.

    A Window does not support features like MenuBars or DockPanes, for
    such functionality, use a MainWindow widget.

    """
    #: A static set of windows being used by the application. A window
    #: adds itself to this list when it is initialized, and removes
    #: itself when it is destroyed. This allows toplevel windows with
    #: no parent to persist without any other strong references.
    windows = set()

    #: The titlebar text.
    title = d_(Unicode())

    #: The initial position of the window frame. A value of (-1, -1)
    #: indicates that the toolkit should choose the initial position.
    initial_position = d_(Coerced(Pos, (-1, -1)))

    #: The initial size of the window client area. A value of (-1, -1)
    #: indicates that the toolkit should choose the initial size.
    initial_size = d_(Coerced(Size, (-1, -1)))

    #: An enum which indicates the modality of the window. The default
    #: value is 'non_modal'.
    modality = d_(Enum('non_modal', 'application_modal', 'window_modal'))

    #: If this value is set to True, the window will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = d_(Bool(True))

    #: The title bar icon.
    icon = d_(Typed(Icon))

    #: Whether the window stays on top of other windows on the desktop.
    #: Changes to this value after the window is shown will be ignored.
    always_on_top = d_(Bool(False))

    #: An event fired when the user request the window to be closed.
    #: This will happen when the user clicks on the "X" button in the
    #: title bar button, or when the 'close' method is called. The
    #: payload will be a CloseEvent object which will allow code to
    #: veto the close event and prevent the window from closing.
    closing = d_(Event(CloseEvent), writable=False)

    #: An event fired when the window is closed.
    closed = d_(Event(), writable=False)

    #: Windows are invisible by default.
    visible = set_default(False)

    #: A reference to the ProxyWindow object.
    proxy = Typed(ProxyWindow)

    def initialize(self):
        """ An overridden initializer method.

        This method adds the window to the static set of Windows.

        """
        super(Window, self).initialize()
        Window.windows.add(self)

    def destroy(self):
        """ An overridden destructor method.

        This method removes the window from the static set of Windows.

        """
        super(Window, self).destroy()
        Window.windows.discard(self)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Get the central widget defined on the window.

        The last `Container` child of the window is the central widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    def position(self):
        """ Get the position of the window frame.

        Returns
        -------
        result : Pos
            The current position of the window frame.

        """
        if self.proxy_is_active:
            return self.proxy.position()
        return Pos(-1, -1)

    def set_position(self, pos):
        """ Set the position of the window frame.

        Parameters
        ----------
        pos : Pos
            The desired position of the window the window frame.

        """
        if self.proxy_is_active:
            self.proxy.set_position(pos)

    def size(self):
        """ Get the size of the window client area.

        Returns
        -------
        result : Size
            The current size of the window client area.

        """
        if self.proxy_is_active:
            return self.proxy.size()
        return Size(-1, -1)

    def set_size(self, size):
        """ Set the size of the window client area.

        Parameters
        ----------
        size : Size
            The desired size of the window client area.

        """
        if self.proxy_is_active:
            self.proxy.set_size(size)

    def geometry(self):
        """ Get the geometry of the window client area.

        Returns
        -------
        result : Rect
            The current geometry of the window client area.

        """
        if self.proxy_is_active:
            return self.proxy.geometry()
        return Rect(-1, -1, -1, -1)

    def set_geometry(self, rect):
        """ Set the geometry of the window client area.

        Parameters
        ----------
        rect : Rect
            The desired geometry of the window client area.

        """
        if self.proxy_is_active:
            self.proxy.set_geometry(rect)

    def frame_geometry(self):
        """ Get the geometry of the window frame.

        Returns
        -------
        result : Rect
            The current geometry of the window frame.

        """
        if self.proxy_is_active:
            return self.proxy.frame_geometry()
        return Rect(-1, -1, -1, -1)

    def maximize(self):
        """ Maximize the window.

        """
        if self.proxy_is_active:
            self.proxy.maximize()

    def is_maximized(self):
        """ Get whether the window is maximized.

        """
        if self.proxy_is_active:
            return self.proxy.is_maximized()
        return False

    def minimize(self):
        """ Minimize the window.

        """
        if self.proxy_is_active:
            self.proxy.minimize()

    def is_minimized(self):
        """ Get whether the window is minimized.

        """
        if self.proxy_is_active:
            return self.proxy.is_minimized()
        return False

    def restore(self):
        """ Restore the window from a maximized or minimized state.

        """
        if self.proxy_is_active:
            self.proxy.restore()

    def send_to_front(self):
        """ Send the window to the top of the Z-order.

        This will only affect the Z-order of the window relative to the
        Z-order of other windows in the same application.

        """
        if self.proxy_is_active:
            self.proxy.send_to_front()

    def send_to_back(self):
        """ Send the window to the bottom of the Z-order.

        This will only affect the Z-order of the window relative to the
        Z-order of other windows in the same application.

        """
        if self.proxy_is_active:
            self.proxy.send_to_back()

    def activate_window(self):
        """ Set this window to be the active application window.

        This performs the same operation as clicking the mouse on the
        title bar of the window, except that it will not effect the Z
        order of the window.

        On Windows, this will cause the taskbar icon to flash if the
        window does not belong to the active application.

        """
        if self.proxy_is_active:
            self.proxy.activate_window()

    def center_on_screen(self):
        """ Center the window on the screen.

        """
        if self.proxy_is_active:
            self.proxy.center_on_screen()

    def center_on_widget(self, other):
        """ Center this window on another widget.

        Parameters
        ----------
        other : Widget
            The widget onto which to center this window.

        """
        assert isinstance(other, Widget)
        if self.proxy_is_active and other.proxy_is_active:
            self.proxy.center_on_widget(other)

    def close(self):
        """ Close the window.

        This will cause the window to be hidden, the 'closed' event
        to be fired, and the window subsequently destroyed.

        """
        if self.proxy_is_active:
            self.proxy.close()

    def show(self):
        """ Show the window to the screen.

        This is a reimplemented parent class method which will init
        and build the window hierarchy if needed.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        super(Window, self).show()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title', 'modality', 'icon')
    def _update_proxy(self, change):
        """ Update the ProxyWindow when the Window data changes.

        """
        # The superclass handler implementation is sufficient.
        super(Window, self)._update_proxy(change)
