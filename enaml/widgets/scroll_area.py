#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Bool, Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_

from .container import Container
from .frame import Frame, ProxyFrame, Border


class ProxyScrollArea(ProxyFrame):
    """ The abstract definition of a proxy ScrollArea object.

    """
    #: A reference to the ScrollArea declaration.
    declaration = ForwardTyped(lambda: ScrollArea)

    def set_horizontal_policy(self, policy):
        raise NotImplementedError

    def set_vertical_policy(self, policy):
        raise NotImplementedError

    def set_widget_resizable(self, resizable):
        raise NotImplementedError


class ScrollArea(Frame):
    """ A Frame which displays a single child in a scrollable area.

    A ScrollArea has at most a single child Container widget.

    """
    #: The horizontal scrollbar policy.
    horizontal_policy = d_(Enum('as_needed', 'always_on', 'always_off'))

    #: The vertical scrollbar policy.
    vertical_policy = d_(Enum('as_needed', 'always_on', 'always_off'))

    #: Whether to resize the scroll widget when possible to avoid the
    #: need for scrollbars or to make use of extra space.
    widget_resizable = d_(Bool(True))

    #: A scroll area is free to expand in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyScrollArea object.
    proxy = Typed(ProxyScrollArea)

    def scroll_widget(self):
        """ Get the scroll widget child defined on the area.

        The scroll widget is the last Container child.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    #--------------------------------------------------------------------------
    # Default Handlers
    #--------------------------------------------------------------------------
    def _default_border(self):
        """ Get the default border for the scroll area.

        The default value matches the default for Qt's QScrollArea.

        """
        return Border(style='styled_panel', line_style='sunken')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('horizontal_policy', 'vertical_policy', 'widget_resizable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ScrollArea, self)._update_proxy(change)
