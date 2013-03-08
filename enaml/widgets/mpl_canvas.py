#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import ForwardInstance, Bool, observe, set_default

from enaml.core.declarative import d_

from .control import Control


#: Delay the import of matplotlib until needed
def Figure():
    from matplotlib.figure import Figure
    return Figure


class MPLCanvas(Control):
    """ A control which can be used to embded a matplotlib figure.

    """
    #: The matplotlib figure to display in the widget.
    figure = d_(ForwardInstance(Figure))

    #: Whether or not the matplotlib figure toolbar is visible.
    toolbar_visible = d_(Bool(False))

    #: Matplotlib figures expand freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the MPLCanvas.

        """
        snap = super(MPLCanvas, self).snapshot()
        snap['figure'] = self.figure
        snap['toolbar_visible'] = self.toolbar_visible
        return snap

    @observe(r'^(figure|toolbar_visible)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(MPLCanvas, self).send_member_change(change)

