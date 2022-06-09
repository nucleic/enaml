# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
"""Test flow area behavior.

With a particular focus on resizing.

"""
import pytest

from utils import compile_source, wait_for_window_displayed


SOURCE = """
from enaml.core.api import Looper
from enaml.widgets.api import Container, FlowArea, FlowItem, Label, Window

enamldef Main(Window): w:

    alias horizontal_spacing: flow_area.horizontal_spacing
    alias vertical_spacing: flow_area.vertical_spacing
    alias direction: flow_area.direction
    alias align: flow_area.align

    initial_size = (800, 800)
    Container:
        FlowArea: flow_area:
            Looper:
                iterable = [1, 2, 3, 4, 5, 6]
                FlowItem:
                    Container:
                        Label:
                            text = str(loop.item)

"""


@pytest.mark.parametrize("horizontal_spacing", [1, 2])
@pytest.mark.parametrize("vertical_spacing", [1, 2])
@pytest.mark.parametrize(
    "direction", ["left_to_right", "right_to_left", "top_to_bottom", "bottom_to_top"]
)
@pytest.mark.parametrize("align", ["leading", "center", "justify", "trailing"])
def test_flow_area_sizing(
    enaml_qtbot, horizontal_spacing, vertical_spacing, direction, align
):
    """Check we can click on a push button."""
    win = compile_source(SOURCE, "Main")(
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
        direction=direction,
        align=align,
    )
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    win.set_size((801, 801))
    enaml_qtbot.wait(1)
    win.set_size((802, 802))
    enaml_qtbot.wait(1)
