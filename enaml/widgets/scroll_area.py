#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Bool, observe, set_default

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget
from .container import Container


class ScrollArea(ConstraintsWidget):
    """ A widget which displays a single child in a scrollable area.

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

    @property
    def scroll_widget(self):
        """ A read only property which returns the scrolled widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(ScrollArea, self).snapshot()
        snap['horizontal_policy'] = self.horizontal_policy
        snap['vertical_policy'] = self.vertical_policy
        snap['widget_resizable'] = self.widget_resizable
        return snap

    @observe(r'^(horizontal_policy|vertical_policy|widget_resizable)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ScrollArea, self).send_member_change(change)

