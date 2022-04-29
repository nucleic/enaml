# ------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------

from utils import compile_source, wait_for_window_displayed

FLOW_EXAMPLE = \
"""from enaml.widgets.api import Window, Container, FlowItem, FlowArea
from enaml.core.api import Include

enamldef SomeFlowItem(FlowItem):
    stretch = 1
    ortho_stretch = 1


enamldef Main(Window):
    Container:
        FlowArea:
            Include:
               objects << [SomeFlowItem() for _ in range(4)]

"""


def test_flow_layout_sort_with_non_zero_item_stretch(enaml_qtbot, enaml_sleep):
    """Test that a FlowArea that contains FlowItems with non zero ortho_stretch or stretch
    doesnt error with:

    TypeError: '<' not supported between instances of 'QFlowWidgetItem' and 'QFlowWidgetItem'
    """
    win = compile_source(FLOW_EXAMPLE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
