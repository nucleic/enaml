#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    List, Typed, ForwardTyped, ForwardInstance, observe, set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


#: Delay the import of vtk until needed. This removes the hard dependecy
#: on vtk for the rest of the Enaml code base.
def vtkRenderer():
    from vtk import vtkRenderer
    return vtkRenderer


class ProxyVTKCanvas(ProxyControl):
    """ The abstract definition of a proxy VTKCanvas object.

    """
    #: A reference to the VTKCanvas declaration.
    declaration = ForwardTyped(lambda: VTKCanvas)

    def set_renderer(self, renderer):
        raise NotImplementedError

    def set_renderers(self, renderers):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class VTKCanvas(Control):
    """ A control which can be used to embded vtk renderers.

    """
    #: The vtk renderer to display in the window. This should be used
    #: if only a single renderer is required for the scene.
    renderer = d_(ForwardInstance(vtkRenderer))

    #: The list of vtk renderers to display in the window. This should
    #: be used if multiple renderers are required for the scene.
    renderers = d_(List(ForwardInstance(vtkRenderer)))

    #: A VTKCanvas expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyVTKCanvas object.
    proxy = Typed(ProxyVTKCanvas)

    def render(self):
        """ Request a render of the underlying scene.

        """
        if self.proxy_is_active:
            self.proxy.render()

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('renderer', 'renderers')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(VTKCanvas, self)._update_proxy(change)
