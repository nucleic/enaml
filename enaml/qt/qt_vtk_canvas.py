#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.vtk_canvas import ProxyVTKCanvas

from . import QT_API, PYQT5_API, PYSIDE2_API
if QT_API in PYQT5_API or QT_API in PYSIDE2_API:
    from vtk.qt5.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
else:
    from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from .QtWidgets import QFrame, QVBoxLayout

from .qt_control import QtControl


class QtVTKCanvas(QtControl, ProxyVTKCanvas):
    """ A Qt implementation of an Enaml ProxyVTKCanvas.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFrame)

    #: A reference to the underlying vtk widget.
    vtk_widget = Typed(QVTKRenderWindowInteractor)

    #: The set of current renderers installed on the window.
    _current_renderers = Typed(set, ())

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        # The vtk widget is nested in a QFrame because the Qt render
        # window interactor does not support reparenting.
        widget = QFrame(self.parent_widget())
        vtk_widget = QVTKRenderWindowInteractor(widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(vtk_widget)
        widget.setLayout(layout)
        self.widget = widget
        self.vtk_widget = vtk_widget

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtVTKCanvas, self).init_widget()
        self._refresh_renderers()
        self.vtk_widget.Initialize()

    #--------------------------------------------------------------------------
    # ProxyVTKCanvas API
    #--------------------------------------------------------------------------
    def set_renderer(self, renderer):
        """ Set the renderer for the widget.

        """
        self._refresh_renderers()

    def set_renderers(self, renderers):
        """ Set the renderers for the widget.

        """
        self._refresh_renderers()

    def render(self):
        """ Request a render of the underlying scene.

        """
        self.vtk_widget.Render()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_renderers(self):
        """ Refresh the renderers installed on the render window.

        """
        d = self.declaration
        old = self._current_renderers
        new = set([_f for _f in [d.renderer] + d.renderers if _f])
        to_remove = old.difference(new)
        to_add = new.difference(old)
        window = self.vtk_widget.GetRenderWindow()
        for r in to_remove:
            window.RemoveRenderer(r)
        for r in to_add:
            window.AddRenderer(r)
        self._current_renderers = new
