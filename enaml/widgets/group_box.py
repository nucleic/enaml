#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Unicode, Enum, observe

from enaml.core.declarative import d_

from .container import Container


class GroupBox(Container):
    """ The GroupBox container, which introduces a group of widgets with
    a title and usually has a border.

    """
    #: The title displayed at the top of the box.
    title = d_(Unicode())

    #: The flat parameter determines if the GroupBox is displayed with
    #: just the title and a header line (True) or with a full border
    #: (False, the default).
    flat = d_(Bool(False))

    #: The alignment of the title text.
    title_align = d_(Enum('left', 'right', 'center'))

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Populates the initial attributes dict for the component.

        """
        snap = super(GroupBox, self).snapshot()
        snap['title'] = self.title
        snap['flat'] = self.flat
        snap['title_align'] = self.title_align
        return snap

    @observe(r'^(title|title_align|flat)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(GroupBox, self).send_member_change(change)

