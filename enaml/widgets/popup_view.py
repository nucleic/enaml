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

    def set_arrow_position(self, pos):
        raise NotImplementedError

    def set_offset(self, pos):
        raise NotImplementedError

    def set_timeout(self, timeout):
        raise NotImplementedError

    def set_fade_in_duration(self, duration):
        raise NotImplementedError

    def set_fade_out_duration(self, duration):
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

    #: The type of the window to create. A 'popup' window will close
    #: when the user presses escape or clicks outside of the window.
    #: A 'tool_tip' window will close when the user clicks the window.
    #: The popup window is useful for showing configuration dialogs,
    #: while the tool tip window is useful for notification messages.
    #: The window type cannot be changed once the widget is created.
    window_type = d_(Enum('popup', 'tool_tip'))

    #: The relative position on the view to use as the anchor. This
    #: anchor will be aligned with the parent anchor to position the
    #: popup view. It is expressed as a percentage of the view size.
    #: The default anchors will position the popup just below the
    #: center of the parent widget.
    anchor = d_(Coerced(PosF, (0.5, 0.0), coercer=coerce_posf))

    #: If the anchor mode is cursor, ignore the parent and use the cursor
    #: position for the popup
    anchor_mode = d_(Enum('parent', 'cursor'))

    #: The relative position on the parent to use as the anchor. This
    #: anchor will be aligned with the view anchor to position the
    #: popup view. It is expressed as a percentage of the parent size.
    #: The default anchors will position the popup just below the
    #: center of the parent widget.
    parent_anchor = d_(Coerced(PosF, (0.5, 0.5), coercer=coerce_posf))

    #: The size of the arrow in pixels. Zero size indicates no anchor.
    arrow_size = d_(Int(0))

    #: The edge of the popup view to use for drawing the arrow.
    arrow_edge = d_(Enum('top', 'bottom', 'left', 'right'))

    #: The position of the arrow along the arrow edge. This is expressed
    #: as a percentage of the arrow edge size.
    arrow_position = d_(Float(0.5))

    #: The adjustment to apply to the final anchored position. This
    #: is expressed as an offset in pixel coordinates.
    offset = d_(Coerced(Pos, (0, 0), coercer=coerce_pos))

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
    @observe(('anchor', 'anchor_mode', 'parent_anchor', 'arrow_size',
        'arrow_edge', 'arrow_position', 'offset', 'timeout',
        'fade_in_duration', 'fade_out_duration'))
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
