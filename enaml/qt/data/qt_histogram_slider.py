#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.stdlib.data.histogram_slider import ProxyHistogramSlider

from enaml.qt.qt_dual_slider import QtDualSlider

from .q_histogram_slider import QHistogramSlider


class QtHistogramSlider(QtDualSlider, ProxyHistogramSlider):
    """ A Qt implementation of an Enaml ProxyDualSlider.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QHistogramSlider)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDualSlider widget.

        """
        self.widget = QHistogramSlider(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying widget.

        """
        super(QtHistogramSlider, self).init_widget()
        d = self.declaration
        if d.histogram:
            self.set_histogram(d.histogram)

    #--------------------------------------------------------------------------
    # ProxyHistogramSlider API
    #--------------------------------------------------------------------------
    def set_histogram(self, histogram):
        """ Set the histogram to render in the underlying widget.

        """
        self.widget.setHistogram(histogram)
