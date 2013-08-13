#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Bool, observe, set_default

from enaml.core.declarative import d_

from .control import Control, ProxyControl


#: Delay the import of matplotlib until needed. This removes the hard
#: dependecy on matplotlib for the rest of the Enaml code base.
def Figure():
    from matplotlib.figure import Figure
    return Figure


class ProxyMPLCanvas(ProxyControl):
    """ The abstract definition of a proxy MPLCanvas object.

    """
    #: A reference to the MPLCanvas declaration.
    declaration = ForwardTyped(lambda: MPLCanvas)

    def set_figure(self, figure):
        raise NotImplementedError

    def set_toolbar_visible(self, visible):
        raise NotImplementedError


class MPLCanvas(Control):
    """ A control which can be used to embded a matplotlib figure.

    """
    #: The matplotlib figure to display in the widget.
    figure = d_(ForwardTyped(Figure))

    #: Whether or not the matplotlib figure toolbar is visible.
    toolbar_visible = d_(Bool(False))

    #: Matplotlib figures expand freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyMPLCanvas object.
    proxy = Typed(ProxyMPLCanvas)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('figure', 'toolbar_visible')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(MPLCanvas, self)._update_proxy(change)
