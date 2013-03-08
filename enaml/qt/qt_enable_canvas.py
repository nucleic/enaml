#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QFrame
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl

from enable.api import Window as EnableWindow


class QtEnableCanvas(QtControl):
    """ A Qt implementation of an Enaml EnableCanvas.

    """
    #: Internal storage for the enable component.
    _component = None

    #: Internal storage for the enable window.
    _window = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = QFrame(parent)
        layout = QSingleWidgetLayout()
        widget.setLayout(layout)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtEnableCanvas, self).create(tree)
        self._component = tree['component']

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtEnableCanvas, self).init_layout()
        self.refresh_enable_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_component(self, content):
        """ Handle the 'set_component' action from the Enaml widget.

        """
        self._component = content['component']
        with size_hint_guard(self):
            self.refresh_enable_widget()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_enable_widget(self):
        """ Create the enable widget and update the underlying control.

        """
        widget = self.widget()
        component = self._component
        if component is not None:
            self._window = EnableWindow(widget, component=component)
            enable_widget = self._window.control
        else:
            self._window = None
            enable_widget = None
        widget.layout().setWidget(enable_widget)

