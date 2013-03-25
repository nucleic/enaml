#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, Float, Typed, ForwardTyped

from enaml.core.declarative import d_

from enaml.widgets.dual_slider import DualSlider, ProxyDualSlider


class ProxyHistogramSlider(ProxyDualSlider):
    """ The abstract definition of a proxy Slider object.

    """
    #: A reference to the Slider declaration.
    declaration = ForwardTyped(lambda: HistogramSlider)

    def set_histogram(self, histogram):
        raise NotImplementedError


class HistogramSlider(DualSlider):
    """ A simple dual slider widget that renders a histogram.

    A dual slider can be used to select a range within a larger range
    of integral values.

    """
    #: Histogram to render
    #: Should be a list of values that sum to 1.0
    histogram = d_(List(Float()))

    #: A reference to the ProxyHistogramSlider object.
    proxy = Typed(ProxyHistogramSlider)
