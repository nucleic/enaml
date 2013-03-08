#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, Enum, Unicode, Coerced, observe

from enaml.core.declarative import Declarative, d_
from enaml.core.messenger import Messenger
from enaml.layout.geometry import Size


class Widget(Messenger, Declarative):
    """ The base class of all visible widgets in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = d_(Bool(True))

    #: Whether or not the widget is visible.
    visible = d_(Bool(True))

    #: The background color of the widget. Supports CSS3 color strings.
    bgcolor = d_(Str())

    #: The foreground color of the widget. Supports CSS3 color strings.
    fgcolor = d_(Str())

    #: The font used for the widget. Supports CSS font formats.
    font = d_(Str())

    #: The minimum size for the widget. The default means that the
    #: client should determine an intelligent minimum size.
    minimum_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: The maximum size for the widget. The default means that the
    #: client should determine and inteliigent maximum size.
    maximum_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = d_(Unicode())

    #: The status tip to show when the user hovers over the widget.
    status_tip = d_(Unicode())

    #: A flag indicating whether or not to show the focus rectangle for
    #: the given widget. This is not necessarily support by all widgets
    #: on all clients. A value of None indicates to use the default as
    #: supplied by the client.
    show_focus_rect = d_(Enum(None, True, False))

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        snap = super(Widget, self).snapshot()
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['bgcolor'] = self.bgcolor
        snap['fgcolor'] = self.fgcolor
        snap['font'] = self.font
        snap['minimum_size'] = self.minimum_size
        snap['maximum_size'] = self.maximum_size
        snap['show_focus_rect'] = self.show_focus_rect
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        return snap

    @observe(r'^(enabled|visible|bgcolor|fgcolor|font|minimum_size|'
             r'maximum_size|show_focus_rect|tool_tip|status_tip)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler is sufficient
        super(Widget, self).send_member_change(change)

