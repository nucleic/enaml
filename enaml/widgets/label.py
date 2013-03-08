#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Enum, observe, set_default

from enaml.core.declarative import d_

from .control import Control


class Label(Control):
    """ A simple control for displaying read-only text.

    """
    #: The unicode text for the label.
    text = d_(Unicode())

    #: The horizontal alignment of the text in the widget area.
    align = d_(Enum('left', 'right', 'center', 'justify'))

    #: The vertical alignment of the text in the widget area.
    vertical_align = d_(Enum('center', 'top', 'bottom'))

    #: Labels hug their width weakly by default.
    hug_width = set_default('weak')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(Label, self).snapshot()
        snap['text'] = self.text
        snap['align'] = self.align
        snap['vertical_align'] = self.vertical_align
        return snap

    @observe(r'^(text|align|vertical_align)$', regex=True)
    def send_member_change(self, change):
        """ An observe which sends the state change to the client.

        """
        # The superclass implementation is sufficient.
        super(Label, self).send_member_change(change)

