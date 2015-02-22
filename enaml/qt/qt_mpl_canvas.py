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
from .QtGui import QFrame, QVBoxLayout, QWidget

from .qt_control import QtControl


class QtMPLCanvas(QtControl, ProxyMPLCanvas):
    """ A Qt implementation of an Enaml ProxyMPLCanvas.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFrame)

    #: The MPL canvas widget.
    canvas = Typed(FigureCanvasQTAgg)

    #: The MPL toolbar widget.
    toolbar = Typed(QWidget)

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
        if self.toolbar:
            with self.geometry_guard():
                self.toolbar.setVisible(visible)

    def focus_target(self):
        """ Get the focus target for the control.

        This returns the canvas widget if possible.

        """
        return self.canvas or self.widget

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_mpl_widget(self):
        """ Create the mpl widget and update the underlying control.

        """
        figure = self.declaration.figure
        old_canvas = self.canvas
        old_toolbar = self.toolbar
        if not figure:
            if old_canvas:
                old_canvas.setParent(None)
            if old_toolbar:
                old_toolbar.setParent(None)
            self.canvas = None
            self.toolbar = None
            return

        new_canvas = _ensure_canvas(figure)
        new_toolbar = _ensure_toolbar(new_canvas, self.widget)

        if new_toolbar is not old_toolbar:
            if old_toolbar:
                old_toolbar.setParent(None)
            self.widget.layout().insertWidget(0, new_toolbar)

        if new_canvas is not old_canvas:
            if old_canvas:
                old_canvas.setParent(None)
            self.widget.layout().insertWidget(1, new_canvas)

        figure.canvas = new_canvas
        new_canvas.figure = figure
        new_canvas.setFocusPolicy(Qt.ClickFocus)
        new_canvas.setVisible(True)
        new_canvas.draw_idle()

        new_toolbar.setVisible(self.declaration.toolbar_visible)
        new_toolbar.home()
        new_toolbar.update()

        self.canvas = new_canvas
        self.toolbar = new_toolbar


def _ensure_canvas(figure):
    """ Get the canvas associated with the figure, or create one.

    Parameters
    ----------
    figure : Figure
        The mpl figure object.

    Returns
    -------
    result : FigureCanvasQTAgg
        The Qt rendering canvas.

    """
    if isinstance(figure.canvas, FigureCanvasQTAgg):
        return figure.canvas
    return FigureCanvasQTAgg(figure)


def _ensure_toolbar(canvas, parent):
    """ Get the toolbar associated with the figure or create one.

    Parameters
    ----------
    canvas : FigureCanvasQTAgg
        The mpl canvas object.

    parent : QWidget
        The parent for the toolbar.

    Returns
    -------
    result : QWidget
        The toolbar for the figure.

    """
    if isinstance(canvas.toolbar, QWidget):
        return canvas.toolbar
    return NavigationToolbar2QT(canvas, parent)
