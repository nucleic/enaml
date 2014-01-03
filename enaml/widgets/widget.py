#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Unicode, Coerced, Typed, ForwardTyped, List, \
    Event, observe

from enaml.colors import ColorMember
from enaml.core.declarative import d_
from enaml.fonts import FontMember
from enaml.layout.geometry import Size
from enaml.styling import Stylable

from .toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyWidget(ProxyToolkitObject):
    """ The abstract definition of a proxy Widget object.

    """
    #: A reference to the Widget declaration.
    declaration = ForwardTyped(lambda: Widget)

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_visible(self, visible):
        raise NotImplementedError

    def set_background(self, background):
        raise NotImplementedError

    def set_foreground(self, foreground):
        raise NotImplementedError

    def set_font(self, font):
        raise NotImplementedError

    def set_minimum_size(self, minimum_size):
        raise NotImplementedError

    def set_maximum_size(self, maximum_size):
        raise NotImplementedError

    def set_tool_tip(self, tool_tip):
        raise NotImplementedError

    def set_status_tip(self, status_tip):
        raise NotImplementedError

    def set_show_focus_rect(self, show_focus_rect):
        raise NotImplementedError

    def ensure_visible(self):
        raise NotImplementedError

    def ensure_hidden(self):
        raise NotImplementedError

    def restyle(self):
        raise NotImplementedError


class Widget(ToolkitObject, Stylable):
    """ The base class of visible widgets in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the widget is visible.
    visible = d_(Bool(True))

    #: The background color of the widget.
    background = d_(ColorMember())

    #: The foreground color of the widget.
    foreground = d_(ColorMember())

    #: The font used for the widget.
    font = d_(FontMember())

    #: The minimum size for the widget. The default means that the
    #: client should determine an intelligent minimum size.
    minimum_size = d_(Coerced(Size, (-1, -1)))

    #: The maximum size for the widget. The default means that the
    #: client should determine an intelligent maximum size.
    maximum_size = d_(Coerced(Size, (-1, -1)))

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = d_(Unicode())

    #: The status tip to show when the user hovers over the widget.
    status_tip = d_(Unicode())

    #: A flag indicating whether or not to show the focus rectangle for
    #: the given widget. This is not necessarily support by all widgets
    #: on all clients. A value of None indicates to use the default as
    #: supplied by the client.
    show_focus_rect = d_(Enum(None, True, False))

    #: Whether or not the widget can be dropped on
    accept_drops = d_(Bool(False))

    #: Whether or not the widget can be dragged
    accept_drags = d_(Bool(False))

    #: The mime-type associated with the drag
    drag_type = d_(Unicode())

    #: The data to be dragged
    drag_data = d_(Unicode())

    #: The mime types that the widget allows to be dropped on itself
    drop_types = d_(List())

    #: Whether or not to highlight drop areas
    highlight_drop = d_(Bool(False))

    #: Fired when something is dropped on the widget
    dropped = d_(Event(), writable=False)

    #: A reference to the ProxyWidget object.
    proxy = Typed(ProxyWidget)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('enabled', 'visible', 'background', 'foreground', 'font',
        'minimum_size', 'maximum_size', 'show_focus_rect', 'tool_tip',
        'status_tip', 'accept_drops', 'accept_drags', 'drag_type', 'drag_data',
        'drop_types', 'highlight_drop')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data changes.

        This method only updates the proxy when an attribute is updated;
        not when it is created or deleted.

        """
        # The superclass implementation is sufficient.
        super(Widget, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def restyle(self):
        """ Restyle the toolkit widget.

        This method is invoked by the Stylable class when the style
        dependencies have changed for the widget. This will trigger a
        proxy restyle if necessary. This method should not typically be
        called directly by user code.

        """
        if self.proxy_is_active:
            self.proxy.restyle()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def show(self):
        """ Ensure the widget is shown.

        Calling this method will also set the widget visibility to True.

        """
        self.visible = True
        if self.proxy_is_active:
            self.proxy.ensure_visible()

    def hide(self):
        """ Ensure the widget is hidden.

        Calling this method will also set the widget visibility to False.

        """
        self.visible = False
        if self.proxy_is_active:
            self.proxy.ensure_hidden()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _handle_drop(self, content):
        """ A method called by the proxy when the user drops the dragged
        widget.

        """
        self.dropped(content)