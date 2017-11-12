#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.progress_bar import ProxyProgressBar

from .QtWidgets import QProgressBar

from .qt_control import QtControl


class QtProgressBar(QtControl, ProxyProgressBar):
    """ A Qt implementation of an Enaml ProxyProgressBar.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QProgressBar)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying progress bar widget.

        """
        self.widget = QProgressBar(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtProgressBar, self).init_widget()
        d = self.declaration
        self.set_minimum(d.minimum)
        self.set_maximum(d.maximum)
        self.set_value(d.value)
        self.set_text_visible(d.text_visible)

    #--------------------------------------------------------------------------
    # ProxyProgressBar API
    #--------------------------------------------------------------------------
    def set_minimum(self, value):
        """ Set the minimum value of the widget.

        """
        self.widget.setMinimum(value)

    def set_maximum(self, value):
        """ Set the maximum value of the widget.

        """
        self.widget.setMaximum(value)

    def set_value(self, value):
        """ Set the value of the widget.

        """
        self.widget.setValue(value)

    def set_text_visible(self, visible):
        """ Set the text visibility on the widget.

        """
        self.widget.setTextVisible(visible)
