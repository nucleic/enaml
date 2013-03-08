#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, observe, set_default

from .constraints_widget import ConstraintsWidget
from .split_item import SplitItem


class Splitter(ConstraintsWidget):
    """ A widget which displays its children in separate resizable
    compartements that are connected with a resizing bar.

    A Splitter can have an arbitrary number of Container children.

    """
    #: The orientation of the Splitter. 'horizontal' means the children
    #: are laid out left to right, 'vertical' means top to bottom.
    orientation = Enum('horizontal', 'vertical')

    #: Whether the child widgets resize as a splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = Bool(True)

    #: A splitter expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    @property
    def split_items(self):
        """ A read only property which returns the list of split items.

        """
        isinst = isinstance
        target = SplitItem
        return [child for child in self.children if isinst(child, target)]

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the control.

        """
        snap = super(Splitter, self).snapshot()
        snap['orientation'] = self.orientation
        snap['live_drag'] = self.live_drag
        return snap

    @observe(r'^(orientation|live_drag)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Splitter, self).send_member_change(change)

