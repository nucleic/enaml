#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.frame import ProxyFrame

from .QtGui import QFrame

from .qt_constraints_widget import QtConstraintsWidget


STYLE = {
    'box': QFrame.Box,
    'panel': QFrame.Panel,
    'styled_panel': QFrame.StyledPanel,
}


LINE_STYLE = {
    'plain': QFrame.Plain,
    'sunken': QFrame.Sunken,
    'raised': QFrame.Raised,
}


class QtFrame(QtConstraintsWidget, ProxyFrame):
    """ A Qt implementation of an Enaml ProxyFrame.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QFrame)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the QContainer widget.

        """
        self.widget = QFrame(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtFrame, self).init_widget()
        self.set_border(self.declaration.border)

    #--------------------------------------------------------------------------
    # ProxyFrame API
    #--------------------------------------------------------------------------
    def set_border(self, border):
        """ Set the border for the widget.

        """
        widget = self.widget
        if border is None:
            widget.setFrameShape(QFrame.NoFrame)
            return
        widget.setFrameShape(STYLE[border.style])
        widget.setFrameShadow(LINE_STYLE[border.line_style])
        widget.setLineWidth(border.line_width)
        widget.setMidLineWidth(border.midline_width)
