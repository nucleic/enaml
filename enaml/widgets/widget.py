#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, Unicode, Coerced, Typed, ForwardTyped, observe

from enaml.colors import ColorMember
from enaml.core.declarative import d_
from enaml.fonts import FontMember
from enaml.layout.geometry import Size

from .toolkit_object import ToolkitObject, ProxyToolkitObject

from .styling.style import Style
from .styling.styledata import StyleData
from .styling.stylesheet import StyleSheet


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


class Widget(ToolkitObject):
    """ The base class of visible widgets in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the widget is visible.
    visible = d_(Bool(True))

    #: The style to apply directly to this object. The selector rules
    #: for the style will be ignored and the setters will be assigned
    #: the highest precedence during the styling passes. This will be
    #: overridden by any Style object declared as a widget child. For
    #: all but the simplest cases, a StyleSheet should be preferred
    #: over a direct style assignment.
    style = d_(Typed(Style))

    #: The stylesheet to apply to the widget and its children. The
    #: styles defined on the stylesheet will have a higher precedence
    #: than those defined on the widget's ancestors. This will be
    #: overridden by any StyleSheet object declared as a widget child.
    stylesheet = d_(Typed(StyleSheet))

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

    #: The resolved style data for the widget. This value is updated
    #: during a styling pass and consumed by the toolkit backend. It
    #: should not be modified directly by user code.
    styledata = Typed(StyleData)

    #: A reference to the ProxyWidget object.
    proxy = Typed(ProxyWidget)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('enabled', 'visible', 'background', 'foreground', 'font',
        'minimum_size', 'maximum_size', 'show_focus_rect', 'tool_tip',
        'status_tip')
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
    def child_added(self, child):
        """ A reimplemented child added event handler.

        This handler will update the Style and StyleSheet attributes
        if children of the given type are added.

        """
        super(Widget, self).child_added(child)
        if isinstance(child, Style):
            self.style = child
        elif isinstance(child, StyleSheet):
            self.stylesheet = child

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This handler will update the Style and StyleSheet attributes
        if children of the given type are removed.

        """
        super(Widget, self).child_removed(child)
        if isinstance(child, Style) and child is self.style:
            new = None
            for child in reversed(self.children):
                if isinstance(child, Style):
                    new = child
            self.style = new
        elif isinstance(child, StyleSheet) and child is self.stylesheet:
            new = None
            for child in reversed(self.children):
                if isinstance(child, StyleSheet):
                    new = child
            self.stylesheet = new

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def restyle(self, ancestors=None):
        """ Restyle the widget and all of it's decendants.

        Parameters
        ----------
        ancestors : list or None
            The style rules for the ancestors of this widget. If given
            the list elements should be the list of styles for the
            ancestor stylesheets of this widget. The ancestor sheets
            will be processed in order according to the within-group
            specificity of the style.

        """
        current = ancestors or []
        sheet = self.stylesheet
        if sheet is not None:
            styles = sheet.styles()
            if styles:
                current += [styles]

        for child in self.children:
            if isinstance(child, Widget):
                child.restyle(current)

        matches = []

        for group in current:
            group_matches = []
            for style in group:
                match, spec = style.match(self)
                if match:
                    group_matches.append((spec, style))
            if matches:
                matches.sort()
                matches.extend(match for _, match in group_matches)

        if self.style is not None:
            matches.append(self.style)

        if matches:
            data = self.styledata
            if data is None:
                data = self.stylesdata = StyleData()
            for style in matches:
                for setter in style.setters():
                    data.apply(setter)

        #if self.proxy_is_active:
        #    self.proxy.restyle()

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
