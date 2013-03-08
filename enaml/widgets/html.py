#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Str, observe, set_default

from enaml.core.declarative import d_

from .control import Control


class Html(Control):
    """ An extremely simple widget for displaying HTML.

    """
    #: The Html source code to be rendered.
    source = d_(Str())

    #: An html control expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dictionary of creation attributes for the control.

        """
        snap = super(Html, self).snapshot()
        snap['source'] = self.source
        return snap

    @observe('source')
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Html, self).send_member_change(change)

