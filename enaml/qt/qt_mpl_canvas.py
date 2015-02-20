#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.mpl_canvas import ProxyMPLCanvas

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT

from .QtCore import Qt
from .QtGui import QFrame, QVBoxLayout

from .qt_control import QtControl


class QtMPLCanvas(QtControl, ProxyMPLCanvas):
    """ A Qt implementation of an Enaml ProxyMPLCanvas.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFrame)

    #: MPL Canvas Object (Singleton)
    canvas = Typed(FigureCanvasQTAgg)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        widget = QFrame(self.parent_widget())
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        self.widget = widget

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtMPLCanvas, self).init_layout()
        self._refresh_mpl_widget()

    #--------------------------------------------------------------------------
    # ProxyMPLCanvas API
    #--------------------------------------------------------------------------
    def set_figure(self, figure):
        """ Set the MPL figure for the widget.

        """
        with self.geometry_guard():
            self._refresh_mpl_widget()

    def set_toolbar_visible(self, visible):
        """ Set the toolbar visibility for the widget.

        """
        layout = self.widget.layout()
        if layout.count() == 2:
            with self.geometry_guard():
                toolbar = layout.itemAt(0).widget()
                toolbar.setVisible(visible)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_mpl_widget(self):
        """ Create the mpl widget and update the underlying control.

        """
        widget = self.widget
        layout = widget.layout()

        # Create the new canvas and toolbar widgets if suitable ones have
        # not been created.
        # The canvas is manually set to visible, or QVBoxLayout will
        # ignore it for size hinting.
        figure = self.declaration.figure
        if figure:
            if not self.canvas:

                if isinstance(figure.canvas, FigureCanvasQTAgg):
                    canvas = figure.canvas
                else:
                    canvas = FigureCanvasQTAgg(figure)

                if canvas.toolbar:
                    # Avoid RuntimeError due to multiple calls to destroy
                    if hasattr(canvas, 'manager'):
                        canvas.manager.toolbar = None
                    toolbar = canvas.toolbar
                    toolbar.setParent(widget)
                else:
                    toolbar = NavigationToolbar2QT(canvas, widget)

                layout.addWidget(toolbar)
                layout.addWidget(canvas)
                canvas.setParent(widget)
                # Use focus policy from MPL FigureManager
                canvas.setFocusPolicy(Qt.StrongFocus)
                canvas.setFocus()
                canvas.setVisible(True)
                self.canvas = canvas

            else:
                canvas = self.canvas
                # Reset and clear the toolbar
                canvas.toolbar.home()
                canvas.toolbar.update()
                figure.canvas = canvas
                canvas.figure = figure
                canvas.draw_idle()

            toolbar = self.canvas.toolbar
            toolbar.setVisible(self.declaration.toolbar_visible)
