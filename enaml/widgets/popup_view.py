#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Coerced, Enum, Float, Event, Int, Typed, ForwardTyped, observe,
    set_default
)

from enaml.application import deferred_call
from enaml.core.declarative import d_
from enaml.layout.geometry import Pos, PosF

from .container import Container
from .widget import Widget, ProxyWidget


def coerce_pos(thing):
    """ Coerce a thing to a Pos.

    """
    if isinstance(thing, tuple):
        return Pos(*thing)
    if isinstance(thing, (int, float)):
        return Pos(thing, thing)
    msg = "Cannot coerce object of type '%s' to a Pos"
    raise ValueError(msg % type(thing).__name__)


def coerce_posf(thing):
    """ Coerce a thing to a PosF.

    """
    if isinstance(thing, tuple):
        return PosF(*thing)
    if isinstance(thing, (int, float)):
        return PosF(thing, thing)
    msg = "Cannot coerce object of type '%s' to a PosF"
    raise ValueError(msg % type(thing).__name__)


class ProxyPopupView(ProxyWidget):
    """ The abstract definition of a proxy PopupView object.

    """
    #: A reference to the PopupView declaration.
    declaration = ForwardTyped(lambda: PopupView)

    def set_anchor(self, anchor):
        raise NotImplementedError

    def set_anchor_mode(self, mode):
        raise NotImplementedError

    def set_parent_anchor(self, anchor):
        raise NotImplementedError

    def set_arrow_size(self, size):
        raise NotImplementedError

    def set_arrow_edge(self, edget):
        raise NotImplementedError

    def set_offset(self, pos):
        raise NotImplementedError

    def set_timeout(self, timeout):
        raise NotImplementedError

    def set_fade_in_duration(self, duration):
        raise NotImplementedError

    def set_fade_out_duration(self, duration):
        raise NotImplementedError

    def set_close_on_click(self, enable):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class PopupView(Widget):
    """ A widget which implements a nice popup view.

    A PopupView is a single-use transient widget that is automatically
    destroyed when it is closed. It is useful for showing contextual
    popup dialogs or notification messages.

    """
    #: Static class-level storage for the view instances. A view will
    #: automatically add and remove itself from this list as needed.
    #: This list prevents the need for the user to manage a strong
    #: reference to a transient popup.
    popup_views = []

    #: The type of the window to create. Each has different behavior. The
    #: window type cannot be changed after the widget is created.
    #:
    #: 'popup'
    #:     This window will close when the user presses escape or clicks
    #:     outside of the window. It will block all external interactions
    #:     until it is closed.
    #:
    #: 'tool_tip'
    #:     This window will close when the user clicks inside the window.
    #:     It stays on top of all the other windows on the desktop. It is
    #:     useful for showing mouse cursor or desktop notifications.
    #:
    #: 'window'
    #:     This window will close when the user clicks inside the window.
    #:     It stays on top of its parent, but not the other windows on
    #:     the desktop. It is useful for notifications inside a window.
    window_type = d_(Enum('popup', 'tool_tip', 'window'))

    #: The mode to use for anchoring. The 'parent' mode uses a point
    #: on the parent or the desktop as the target anchor, the 'cursor'
    #: mode uses the current cursor position as the target anchor.
    anchor_mode = d_(Enum('parent', 'cursor'))

    #: The relative position on the parent to use as the anchor. This
    #: anchor will be aligned with the view anchor to position the
    #: popup view. It is expressed as a percentage of the parent size.
    #: The default anchors will position the popup just below the
    #: center of the parent widget.
    parent_anchor = d_(Coerced(PosF, (0.5, 0.5), coercer=coerce_posf))

    #: The relative position on the view to use as the view anchor.
    #: This anchor will be aligned with the parent anchor to position
    #: the popup view. It is expressed as a percentage of the view
    #: size. The default anchors will position the popup just below
    #: the center of the parent widget.
    anchor = d_(Coerced(PosF, (0.5, 0.0), coercer=coerce_posf))

    #: The offset to apply between the two anchors, in pixels.
    offset = d_(Coerced(Pos, (0, 0), coercer=coerce_pos))

    #: The edge of the popup view to use for rendering the arrow.
    arrow_edge = d_(Enum('top', 'bottom', 'left', 'right'))

    #: The size of the arrow in pixels. If this value is > 0, the view
    #: anchor is taken to be the point of the arrow. If the arrow edge
    #: is 'left' or 'right', the anchor's y-coordinate is used to set
    #: the arrow position, and the x-coordinate is ignored. If the
    #: arrow edge is 'top' or 'bottom', the anchor's x-coordinate is
    #: used to set the arrow position, and the y-coordinate is ignored.
    arrow_size = d_(Int(0))

    #: The timeout, in seconds, before automatically closing the popup.
    #: A value less than or equal to zero means no timeout. This is
    #: typically useful when displaying non-interactive notifications.
    timeout = d_(Float(0.0))

    #: The duration of the fade-in, in milliseconds. A value less than
    #: or equal to zero means no fade.
    fade_in_duration = d_(Int(100))

    #: The duration of the fade-out, in milliseconds. A value less than
    #: or equal to zero means no fade.
    fade_out_duration = d_(Int(100))

    #: Whether or not close the popup view on a mouse click. For 'popup'
    #: windows, this means clicking outside of the view. For 'tool_tip'
    #: and 'window' windows, this means clicking inside of the view.
    close_on_click = d_(Bool(True))

    #: Whether or not the background of the popup view is translucent.
    #: This must be True in order to use background colors with alpha
    #: and for the fade in and out animation to have effect. This value
    #: must be set before the popup view is shown. Changes to this value
    #: after the popup is shown will have no effect.
    translucent_background = d_(Bool(True))

    #: An event emitted when the view is closed. After this event is
    #: fired, the view will be destroyed and should not be used.
    closed = d_(Event(), writable=False)

    #: PopupViews are invisible by default.
    visible = set_default(False)

    #: A reference to the ProxyPopupView object.
    proxy = Typed(ProxyPopupView)

    #: This attribute is deprecated and will be removed in Enaml 1.0
    arrow_position = d_(Float(0.5))

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def central_widget(self):
        """ Get the central widget defined on the PopupView.

        The last `Container` child of the window is the central widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    def show(self):
        """ Show the PopupView.

        This is a reimplemented method which will intitialize the proxy
        tree before showing the view.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        super(PopupView, self).show()
        PopupView.popup_views.append(self)

    def close(self):
        """ Close the PopupView.

        Closing the view, as opposed to hiding it or setting it's
        visibility to False, will cause the 'closed' event to be
        emitted and the view to be destroyed.

        """
        if self.proxy_is_active:
            self.proxy.close()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('anchor', 'anchor_mode', 'parent_anchor', 'arrow_size', 'offset',
        'arrow_edge', 'timeout', 'fade_in_duration', 'fade_out_duration',
        'close_on_click')
    def _update_proxy(self, change):
        """ Update the proxy when the PopupView data changes.

        """
        # The superclass handler implementation is sufficient.
        super(PopupView, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _popup_closed(self):
        """ Handle the popup view being closed.

        This method is called by the proxy object when the toolkit
        popup view is closed.

        """
        self.visible = False
        self.closed()
        deferred_call(self.destroy)
        PopupView.popup_views.remove(self)
