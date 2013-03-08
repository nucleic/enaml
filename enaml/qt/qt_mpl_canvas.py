#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QFrame, QVBoxLayout
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg


class QtMPLCanvas(QtControl):
    """ A Qt implementation of an Enaml MPLCanvas.

    """
    #: Internal storage for the matplotlib figure.
    _figure = None

    #: Internal storage for whether or not to show the toolbar.
    _toolbar_visible = False

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = QFrame(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMPLCanvas, self).create(tree)
        self._figure = tree['figure']
        self._toolbar_visible = tree['toolbar_visible']

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtMPLCanvas, self).init_layout()
        self.refresh_mpl_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_figure(self, content):
        """ Handle the 'set_figure' action from the Enaml widget.

        """
        self._figure = content['figure']
        with size_hint_guard(self):
            self.refresh_mpl_widget()

    def on_action_set_toolbar_visible(self, content):
        """ Handle the 'set_toolbar_visible' action from the Enaml
        widget.

        """
        visible = content['toolbar_visible']
        self._toolbar_visible = visible
        layout = self.widget().layout()
        if layout.count() == 2:
            with size_hint_guard(self):
                toolbar = layout.itemAt(0).widget()
                toolbar.setVisible(visible)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_mpl_widget(self):
        """ Create the mpl widget and update the underlying control.

        """
        # Delete the old widgets in the layout, it's just shenanigans
        # to try to reuse the old widgets when the figure changes.
        widget = self.widget()
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
        figure = self._figure
        if figure is not None:
            canvas = FigureCanvasQTAgg(figure)
            canvas.setParent(widget)
            canvas.setFocusPolicy(Qt.ClickFocus)
            canvas.setVisible(True)
            toolbar = NavigationToolbar2QTAgg(canvas, widget)
            toolbar.setVisible(self._toolbar_visible)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)

