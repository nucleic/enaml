#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.mpl_canvas import ProxyMPLCanvas

from .QtCore import Qt, __version__ as QT_VERSION
from .QtWidgets import QFrame, QVBoxLayout

from .qt_control import QtControl

if QT_VERSION[0] == '4':
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
    try:
        from matplotlib.backends.backend_qt4agg import (
            NavigationToolbar2QTAgg as NavigationToolbar2QT)
    except ImportError:
        from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
elif QT_VERSION[0] == '5':
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
else:

    raise RuntimeError("No known Matplotlib backend for qt version {} "
                       "(as reported by qtpy.QT_VERSION)".format(QT_VERSION))


class QtMPLCanvas(QtControl, ProxyMPLCanvas):
    """ A Qt implementation of an Enaml ProxyMPLCanvas.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFrame)

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
        # Delete the old widgets in the layout, it's just shenanigans
        # to try to reuse the old widgets when the figure changes.
        widget = self.widget
        layout = widget.layout()
        while layout.count():
            layout_item = layout.takeAt(0)
            layout_item.widget().deleteLater()

        # Create the new figure and toolbar widgets. It seems that key
        # events will not be processed without an mpl figure manager.
        # However, a figure manager will create a new toplevel window,
        # which is certainly not desired in this case. This appears to
        # be a limitation of matplotlib. The canvas is manually set to
        # visible, or QVBoxLayout will ignore it for size hinting.
        figure = self.declaration.figure
        if figure:
            canvas = FigureCanvasQTAgg(figure)
            canvas.setParent(widget)
            canvas.setFocusPolicy(Qt.ClickFocus)
            canvas.setVisible(True)
            toolbar = NavigationToolbar2QT(canvas, widget)
            toolbar.setVisible(self.declaration.toolbar_visible)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
